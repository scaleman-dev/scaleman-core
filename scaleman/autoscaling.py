from flask import request, jsonify, Blueprint
import requests

from scaleman.model import AutoScalingGroup
from scaleman.db import db
from scaleman.util import get_digitalocean_auth_headers

AUTO_SCALING = Blueprint("auto_scaling", __name__)

@AUTO_SCALING.route('/api/load_balancers')
def get_load_balancers():
    URL = 'https://api.digitalocean.com/v2/load_balancers'
    response = requests.get(URL, headers=get_digitalocean_auth_headers())
    return jsonify({"response": response.json()})

@AUTO_SCALING.route('/api/snapshots')
def snapshots():
    URL = 'https://api.digitalocean.com/v2/snapshots'
    response = requests.get(URL, headers=get_digitalocean_auth_headers())
    return jsonify({"response": response.json()})

@AUTO_SCALING.route('/api/autoscaling_groups', methods=['POST'])
def create_autoscaling_groups():
    auto_scaling_group = AutoScalingGroup(
        load_balancer_id=request.json.get("load_balancer_id"),
        desired_instance_count=request.json.get("desired_instance_count"),
        max_instance_count=request.json.get("max_instance_count"),
        cool_down_time=request.json.get("cool_down_time"),
        name=request.json.get("name"),
        setup_type=request.json.get("setup_type"),
        bootstrap_script=request.json.get("bootstrap_script"),
        ansible_repo=request.json.get("ansible_repo"),
        snapshot_id=request.json.get("snapshot_id"),
        termination_policy=request.json.get("termination_policy"),
        max_cpu_usage=request.json.get("max_cpu_usage")
    )
    db.session.add(auto_scaling_group)
    db.session.commit()
    return jsonify({"response": "success"})

@AUTO_SCALING.route('/api/autoscaling_groups')
def get_autoscaling_groups():
    return jsonify({
        "response": [asg.as_dict() for asg in AutoScalingGroup.query.all()]
    })
