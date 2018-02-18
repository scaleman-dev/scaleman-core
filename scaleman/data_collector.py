from datetime import datetime

from flask import Blueprint, request, jsonify

from scaleman.db import db
from scaleman.model import UsageMetrics

DATA_COLLECTOR = Blueprint('data_collector', __name__)

@DATA_COLLECTOR.route('/api/metric', methods=['POST'])
def collect_metrics():
    print(request.json)
    usage_metric = UsageMetrics(
        average_usage=request.json['average_usage'],
        fetchDate=datetime.now(),
        instance_ip=request.json.get('instance_ip', 'unknown')
    )
    db.session.add(usage_metric)
    db.session.commit()
    return jsonify({
        "response": "success"
    })
