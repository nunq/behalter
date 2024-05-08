#!/usr/bin/env python3
"""flask main file"""
from flask import Flask

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bm.db"

import behalter.views  # pylint: disable=wrong-import-position
