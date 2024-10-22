#!/usr/bin/env python3
"""flask main file"""
import json

from flask import Flask

app = Flask(__name__, instance_relative_config=True)
app.config.from_file("config.json", load=json.load)

import behalter.views # pylint: disable=wrong-import-position
