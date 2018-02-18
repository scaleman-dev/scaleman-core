from flask_script import Server, Manager

from scaleman import app
from scaleman.db import db
from scaleman.model import *
import scaleman.scale_ops as scale_ops

manager = Manager(app)
manager.add_command('runserver', Server())

@manager.command
def autoscale():
    scale_ops.run()

@manager.command
def init_db():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    manager.run()
