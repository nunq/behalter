#!/usr/bin/env python3
import json
import re
import sqlite3
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup
from flask import render_template, request, send_from_directory

from behalter import app, db
from behalter.util import unix_to_date


@app.route("/")
def index():
    bm = db.get_all_bookmarks()
    return render_template("index.html", bookmarks=bm)


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(Path(app.root_path) / "static", "favicon.ico", mimetype="image/vnd.microsoft.icon")

