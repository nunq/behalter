#!/usr/bin/env python3

from flask import Flask, render_template, request
import json
import sqlite3
import urllib.request
from urllib.parse import unquote
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
    bm = conn.execute("SELECT * FROM bookmarks ORDER BY id DESC").fetchall()
    return render_template("index.html", bookmarks=bm)

@app.route("/api/add")
def add_bookmark():
    title = request.args.get("title")
    link_enc = request.args.get("link")
    link = unquote(link_enc)
    detail = request.args.get("detail")
    note = request.args.get("note")
    tags = request.args.get("tags")
    try:
        domain = re.search(r'://(.*?)/', link).group(1)
    except:
        domain = ""
    # TODO append / in frontend js


    cur.execute("INSERT INTO bookmarks (title, currentlink, origlink, archivelink, domain, detail, note, tags) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (title, link, link, "ARCHIVE TODO", domain, detail, note, tags)
            )
    conn.commit()

    # TODO full page text (selenium or library?) ?

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
    #html = res.read().decode("utf-8")

    soup = BeautifulSoup(res, "html.parser",
                         from_encoding=res.info().get_param("charset"))

    title = soup.title.string

    detail = ""
    if soup.find(name="meta", attrs={"name":"detail"}) != None:
        detail = soup.find(name="meta", attrs={"name":"detail"}).get("content")

    if soup.find(name="meta", attrs={"name":"og:description"}) != None and detail == "":
        detail = soup.find(name="meta", attrs={"name":"og:description"}).get("content")

    if soup.find(name="meta", attrs={"name":"twitter:description"}) != None and detail == "":
        detail = soup.find(name="meta", attrs={"name":"twitter:description"}).get("content")

    return json.dumps({"result": "success", "title": title, "detail": detail})


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
