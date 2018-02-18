from flask import Blueprint, jsonify, request
import yaml

AUTH = Blueprint('auth', __name__)

@AUTH.route('/api/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    users = yaml.load(open('settings/auth.yml'))['users']
    for user in users:
        if username == user['username'] and password == user['password']:
            return jsonify({"response": True})
    return jsonify({"response": False})
