#!/usr/bin/env python3
"""flask views"""
from pathlib import Path
from json import dumps

from flask import render_template, request, send_from_directory

from behalter import app, database
from behalter.util import fetch_link_info


@app.route("/")
def index():
    bm = database.get_all_bookmarks()
    return render_template("index.html", bookmarks=bm)


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        Path(app.root_path) / "static",
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


@app.route("/api/bm/add")
def add_bookmark():
    ra = request.args
    title = ra.get("title")
    link = ra.get("link")
    detail = ra.get("detail")
    note = ra.get("note")
    tags = ra.get("tags")

    if tags != "":
        created_bm = database.create_bookmark(title, link, detail, note, tags)
    else:
        created_bm = database.create_bookmark(title, link, detail, note)

    # TODO handle duplicates
    # TODO redirect to bookmark if duplicate detected
    # TODO implement search?id=<id> for that
    return dumps(
        {"result": "success", "bmhtml": render_template("bookmark.html", bm=created_bm)}
    )


@app.route("/api/bm/linkinfo")
def link_info():
    ra = request.args
    link = ra.get("link")
    return fetch_link_info(link)


@app.route("/api/tags/get")
def list_tags():
    ret = database.get_tags_ordered_by_usage()
    return dumps({"result": "success", "tags": ret})
