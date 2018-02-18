import yaml

def get_digitalocean_auth_headers():
    headers = {
        'Authorization': "Bearer " + yaml.load(open('settings/auth.yml'))['api_key']
    }
    return headers
