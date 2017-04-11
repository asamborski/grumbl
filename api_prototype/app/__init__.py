from flask import Flask
from flask.ext.pymongo import PyMongo

# Initialize the app
app = Flask(__name__, instance_relative_config=True)
# Initialize mongodb
mongo = PyMongo(app)

# Load the views
from app import views

# Load the config file
app.config.from_object('config')
