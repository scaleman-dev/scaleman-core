from flask import Flask
from flask_cors import CORS

from scaleman.db import db
from scaleman.data_collector import DATA_COLLECTOR
from scaleman.auth import AUTH
from scaleman.autoscaling import AUTO_SCALING

app = Flask(__name__, instance_relative_config=True)
CORS(app)
app.config.from_pyfile('default.cfg')
app.config.from_pyfile('application.cfg', silent=True)
db.init_app(app)

app.register_blueprint(DATA_COLLECTOR)
app.register_blueprint(AUTH)
app.register_blueprint(AUTO_SCALING)
