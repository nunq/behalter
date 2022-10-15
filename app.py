#!/usr/bin/env python3

from flask import Flask, render_template, request
import json
import sqlite3
import urllib.request
import re
import atexit
from bs4 import BeautifulSoup
from datetime import datetime

conn = sqlite3.connect("bm.db", check_same_thread=False)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

def shutdown():
    conn.commit()
    conn.close()

atexit.register(shutdown)

app = Flask(__name__)


@app.template_filter()
def unix_to_date(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime("%d-%m-%Y")

# -----------------------------------
# routes

@app.route("/")
def index():
    bm = conn.execute("SELECT * FROM bookmarks WHERE NOT deleted ORDER BY id DESC").fetchall()
    return render_template("index.html", bookmarks=bm)

@app.route("/api/bm/add")
def add_bookmark():
    title = request.args.get("title")
    link = request.args.get("link")
    detail = request.args.get("detail")
    note = request.args.get("note")
    tags = request.args.get("tags")
    try:
        domain = re.search(r'://(.*?)/', link).group(1)
    except:
        domain = re.search(r'://(.*?)$', link).group(1)
    # TODO append / in frontend js

    try:
        cur.execute("INSERT INTO bookmarks (title, currentlink, origlink, archivelink, domain, detail, note, tags) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (title, link, link, "ARCHIVE TODO", domain, detail, note, tags)
                )
        conn.commit()
    except:
        return json.dumps({"result": "error", "res-text": "database insert failed"})


    # TODO full page text (selenium or library?) ?

    return json.dumps({"result": "success"})


@app.route("/api/bm/linkinfo")
def linkinfo():
    link = request.args.get("link")

    req = urllib.request.Request(
            link,
            data = None,
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0"
                }
            )

    res = urllib.request.urlopen(req)
    soup = BeautifulSoup(res, "html.parser",
                         from_encoding=res.info().get_param("charset"))
    title = soup.title.string

    detail = ""
    if soup.find(name="meta", attrs={"name":"description"}) != None:
        detail = soup.find(name="meta", attrs={"name":"description"}).get("content")

    if soup.find(name="meta", attrs={"name":"og:description"}) != None and detail == "":
        detail = soup.find(name="meta", attrs={"name":"og:description"}).get("content")

    if soup.find(name="meta", attrs={"name":"twitter:description"}) != None and detail == "":
        detail = soup.find(name="meta", attrs={"name":"twitter:description"}).get("content")

    return json.dumps({"result": "success", "title": title, "detail": detail})


@app.route("/api/bm/edit")
def edit_bookmark():
    # anhand der id das ding in der datenbank updaten, alle felder die aus dem frontend kommen


    source = request.args.get("link")


@app.route("/api/bm/delete")
def delete_bookmark():
    b_id = request.args.get("id")

    try:
        cur.execute("UPDATE bookmarks SET deleted = TRUE WHERE id = (?)", (b_id) )
        conn.commit()
    except:
        return json.dumps({"result": "error", "res-text": "database mark as deleted failed"})

    return json.dumps({"result": "success"})

if __name__ == "__main__":
    app.run()
