#!/usr/bin/env python3

from flask import Flask, render_template, request
import json
import sqlite3
import urllib.request
from urllib.parse import unquote
import opengraph_py3 as opengraph
import re
import atexit

conn = sqlite3.connect("bm.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

def shutdown():
    conn.commit()
    conn.close()

atexit.register(shutdown)

app = Flask(__name__)

@app.route("/")
def index():
    bm = conn.execute("SELECT * FROM bookmarks ORDER BY id DESC").fetchall()
    return render_template("index.html", bookmarks=bm)

@app.route("/api/add")
def add_bookmark():
    title = request.args.get("title")
    link_enc = request.args.get("link")
    link = unquote(link_enc)
    description = request.args.get("description")
    note = request.args.get("note")
    tags = request.args.get("tags")
    domain = re.search(r'://(.*?)/', link).group(1)
    # TODO append / in frontend js


    cur.execute("INSERT INTO bookmarks (title, currentlink, origlink, archivelink, domain, description, note, tags) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (title, link, link, "ARCHIVE TODO", domain, description, note, tags)
            )
    conn.commit()

    # TODO full page text (selenium or library?) ?

    # insert into db


    return json.dumps({"result": "success"})


@app.route("/api/linkinfo")
def linkinfo():
    link_enc = request.args.get("link")
    link = unquote(link_enc)

    req = urllib.request.Request(
            link,
            data = None,
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0"
                }
            )

    res = urllib.request.urlopen(req)
    html = res.read().decode("utf-8")

# TODO do opengraph without this library
    data = opengraph.OpenGraph(url=link)
    title = data["title"]
    description = data["description"]

    if title == "" or description == "":
        try:
            title = re.search(r'<title>(.*?)</title>', html).group(1)
            description = re.search(r'<meta name="description">(.*?)</meta>', html).group(1)
        except AttributeError:
            title = description = ""

    return json.dumps({"result": "success", "title": title, "description": description})


@app.route("/api/edit")
def edit_bookmark():
    # anhand der id das ding in der datenbank updaten, alle felder die aus dem frontend kommen


    source = request.args.get("link")
@app.route("/api/delete")
def delete_bookmark():
    # TODO confirm dialog in frontend?
    id = request.args.get("id")

    # dont delete in database but move to deleted table


# TODO return paginated feed
#
#
# TODO on exit db commit and db close

if __name__ == "__main__":
    app.run(threaded=False, processes=1)
