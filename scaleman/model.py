from scaleman.db import db

class UsageMetrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    average_usage = db.Column(db.Float)
    fetchDate = db.Column(db.DateTime)
    instance_ip = db.Column(db.String(20))

class AutoScalingGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    load_balancer_id = db.Column(db.String(1000))
    desired_instance_count = db.Column(db.Integer)
    max_instance_count = db.Column(db.Integer)
    cool_down_time = db.Column(db.Integer)
    name = db.Column(db.Integer)
    setup_type = db.Column(db.String(1000))
    bootstrap_script = db.Column(db.String(10000))
    ansible_repo = db.Column(db.String(1000))
    snapshot_id = db.Column(db.String(1000))
    termination_policy = db.Column(db.String(1000))
    max_cpu_usage = db.Column(db.Float)

    def as_dict(self):
        return {
            "id": self.id,
            "load_balancer_id": self.load_balancer_id,
            "desired_instance_count": self.desired_instance_count,
            "max_instance_count": self.max_instance_count,
            "cool_down_time": self.cool_down_time,
            "name": self.name,
            "setup_type": self.setup_type,
            "bootstrap_script": self.bootstrap_script,
            "ansible_repo": self.ansible_repo,
            "snapshot_id": self.snapshot_id,
            "termination_policy": self.termination_policy,
            "max_cpu_usage": self.max_cpu_usage
        }
