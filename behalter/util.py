#!/usr/bin/env python3
from datetime import datetime
from behalter import app

@app.template_filter()
def unix_to_date(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime("%d-%m-%Y")

