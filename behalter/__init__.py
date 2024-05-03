#!/usr/bin/env python3
import atexit
import os

from datetime import datetime

from flask import Flask#, render_template, request, send_from_directory

# -----------------------------------
""" # TODO
def shutdown():
    conn.commit()
    conn.close()

atexit.register(shutdown)
"""

app = Flask(__name__)

import behalter.views # pylint: disable=wrong-import-position

@app.template_filter()
def unix_to_date(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime("%d-%m-%Y")


if __name__ == "__main__":
    app.run()
