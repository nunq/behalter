#!/usr/bin/env python3
"""flask main file"""
from flask import Flask
from flask_login import LoginManager

app = Flask(__name__)

# Set the secret key to some random bytes. Keep this really secret!
# TODO hide
app.secret_key = "TODO-testing"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bm.db"

login = LoginManager(app)
login.init_app(app)

import behalter.views  # pylint: disable=wrong-import-position
