from datetime import datetime
import random
import time

import requests

from scaleman.db import db
from scaleman.model import AutoScalingGroup, UsageMetrics
from scaleman.util import get_digitalocean_auth_headers

"""
- Get list of all autoscaling groups
- For each auto scaling group DO
    - get load balancer by id
    - create droplet id and ip mappings
    - check for number of droplets in load balancer if they are less then min required then create one
    - if they are equal to min required then check for their mem usage
        create a count of mem usage under limit
        if the count != desired count then create a droplet
        if the count > desired count take diffrence and remove that number of droplet
            remove the oldest ones
    when creating droplet respect the requirements provided by user and also install agent in it
    after creating and fullfiling the reqs attach the droplet to load balancer
    save history
"""

def get_droplet_mappings(droplet_ids):
    mappings = {}
    for droplet_id in droplet_ids:
        URL = 'https://api.digitalocean.com/v2/droplets/' + str(droplet_id)
        droplet = requests.get(
            URL,
            headers=get_digitalocean_auth_headers()
        ).json()['droplet']
        mappings[droplet_id] = {
            "ip": droplet['networks']['v4'][0]['ip_address'],
            "created_at": datetime.strptime(droplet['created_at'], '%Y-%m-%dT%H:%M:%SZ'),
            "region": droplet['region']['slug'],
            "size": droplet['size_slug'],
            "image": droplet['image']['slug'],
        }
    return mappings

def get_cpu_usage(instance_ip):
    try:
        usage_metrics = UsageMetrics.query.filter_by(instance_ip=instance_ip).order_by(UsageMetrics.fetchDate.desc()).first()
        return usage_metrics.average_usage
    except Exception as e:
        print(e)
        return 0

def terminate_droplet(droplet_id):
    URL = 'https://api.digitalocean.com/v2/droplets/' + str(droplet_id)
    response = requests.delete(URL, headers=get_digitalocean_auth_headers())
    if response.status_code == 204:
        return True
    return False

def create_droplet(count, region, size, image, load_balancer, snapshot_id, bootstrap, ansible_config, name):
    URL = 'https://api.digitalocean.com/v2/droplets'
    payload = {
        "region": region,
        "names": ["{}-{}".format(name, random.randint(0, 100)) for i in range(count)],
        "size": size
    }
    if snapshot_id:
        payload['image'] = int(snapshot_id)
    else:
        payload['image'] = image
    droplets = requests.post(URL, json=payload, headers=get_digitalocean_auth_headers()).json()['droplets']
    time.sleep(3)
    load_balancer['droplet_ids'] += [droplet['id'] for droplet in droplets]
    load_balancer['region'] = load_balancer['region']['slug']
    URL = 'https://api.digitalocean.com/v2/load_balancers/' + str(load_balancer['id'])
    response = requests.put(URL, json=load_balancer, headers=get_digitalocean_auth_headers())

def run():
    auto_scaling_groups = AutoScalingGroup.query.all()
    for auto_scaling_group in auto_scaling_groups:
        print("Trying to autoscale {}".format(auto_scaling_group.name))
        URL = 'https://api.digitalocean.com/v2/load_balancers/' + auto_scaling_group.load_balancer_id
        load_balancer = requests.get(
            URL,
            headers=get_digitalocean_auth_headers()
        ).json()['load_balancer']
        instance_ids = load_balancer['droplet_ids']
        droplet_mappings = get_droplet_mappings(instance_ids)
        desired_size = auto_scaling_group.desired_instance_count
        if len(instance_ids) >= desired_size:
            normal_instances = []
            for instance_id in instance_ids:
                cpu_usage = get_cpu_usage(droplet_mappings[instance_id]['ip'])
                if cpu_usage <= auto_scaling_group.max_cpu_usage:
                    normal_instances.append(instance_id)
            if len(normal_instances) < desired_size:
                if len(instance_ids) > 0:
                    region = droplet_mappings[instance_ids[0]]['region']
                    size = droplet_mappings[instance_ids[0]]['size']
                    image = droplet_mappings[instance_ids[0]]['image']
                else:
                    region = 'blr1'
                    image = 'centos-7-x64'
                    size = 's-1vcpu-1gb'
                create_droplet(
                    desired_size - len(normal_instances),
                    region,
                    size,
                    image,
                    load_balancer,
                    auto_scaling_group.snapshot_id,
                    auto_scaling_group.bootstrap_script,
                    auto_scaling_group.ansible_repo,
                    auto_scaling_group.name
                )
                print("scale up")
            elif len(normal_instances) > desired_size:
                droplets = []
                for droplet_id in droplet_mappings:
                    droplets.append((droplet_id, droplet_mappings[droplet_id]['created_at']))
                droplets = sorted(droplets, key=lambda x: x[1])
                droplets_to_remove = droplets[0: len(normal_instances) - desired_size]
                for droplet in droplets_to_remove:
                    droplet_id = droplet[0]
                    terminate_droplet(droplet_id)
                    if terminate_droplet(droplet_id):
                        print("Droplet with ID:{} is terminated".format(droplet_id))
                print("Scale Down Finished")
            else:
                print("No Action needed")
        else:
            if len(instance_ids) > 0:
                region = droplet_mappings[instance_ids[0]]['region']
                size = droplet_mappings[instance_ids[0]]['size']
                image = droplet_mappings[instance_ids[0]]['image']
            else:
                region = 'blr1'
                image = 'centos-7-x64'
                size = 's-1vcpu-1gb'
            create_droplet(
                desired_size - len(instance_ids),
                region,
                size,
                image,
                load_balancer,
                auto_scaling_group.snapshot_id,
                auto_scaling_group.bootstrap_script,
                auto_scaling_group.ansible_repo,
                auto_scaling_group.name
            )
            print("scale up")
            import pdb; pdb.set_trace()
