#!/usr/bin/env python3
import atexit
import json
import re
import sqlite3
import urllib.request
from datetime import datetime

from bs4 import BeautifulSoup
from flask import Flask, render_template, request

# -----------------------------------

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
    bm = cur.execute("SELECT * FROM bookmarks WHERE NOT deleted ORDER BY id DESC").fetchall()
    return render_template("index.html", bookmarks=bm)

@app.route("/search")
def search_bookmarks():
    query = request.args.get("q")
    tag = request.args.get("tag") # used by filterbytag

    if (tag != "" and tag != None) and (query == "" or query == None):
        # tag search from filterbytag
        tagsearch = cur.execute("SELECT * FROM bookmarks WHERE NOT deleted AND tags LIKE (?) ORDER BY id DESC", ("%"+tag+"%",)).fetchall()
        return render_template("index.html", bookmarks=tagsearch)
    elif (query != "" and query != None) and (tag == "" or tag == None) and bool(re.search("^tag:(\w+)" , query)):
        # tag search from search box
        tag = re.search("^tag:(\w+)" , query).group(1)
        tagsearch = cur.execute("SELECT * FROM bookmarks WHERE NOT deleted AND tags LIKE (?) ORDER BY id DESC", ("%"+tag+"%",)).fetchall()
        return render_template("index.html", bookmarks=tagsearch)
    elif (query != "" and query != None) and (tag == "" or tag == None) and not bool(re.search("^tag:(\w+)" , query)):
        # general search query
        qsearch = cur.execute("SELECT * FROM bookmarks WHERE NOT deleted AND (title LIKE (?) OR origlink LIKE (?) OR detail LIKE (?) or note LIKE (?)) ORDER BY id DESC", ("%"+query+"%", "%"+query+"%", "%"+query+"%", "%"+query+"%")).fetchall()
        return render_template("index.html", bookmarks=qsearch)
    else:
        return render_template("index.html", bookmarks="")

@app.route("/export")
def export_bookmarks():
    bookmarks = cur.execute("SELECT * FROM bookmarks ORDER BY id DESC").fetchall()
    return json.dumps([dict(bm) for bm in bookmarks])

@app.route("/renametag")
def rename_tag():
    return render_template("renametag.html")

# -----------------------------------
# api

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

    try:
        cur.execute("INSERT INTO bookmarks (title, currentlink, origlink, archivelink, domain, detail, note, tags) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (title, link, link, "ARCHIVE TODO", domain, detail, note, tags))
        conn.commit()
    except:
        return json.dumps({"result": "error", "res-text": "database insert failed"})

    for tag in tags.split(","):
        try:
            cur.execute("INSERT INTO tags (name, usage) VALUES (?, ?)", (tag, 1))
            conn.commit()
        except sqlite3.IntegrityError:
            cur.execute("UPDATE tags SET usage = usage+1 WHERE name = (?)", (tag,))
            conn.commit()

    bm = cur.execute("SELECT * from bookmarks WHERE title = (?) AND origlink = (?) ORDER BY id DESC", (title, link)).fetchone()
    return json.dumps({"result": "success", "bmhtml": render_template("bookmark.html", bm=bm)})

@app.route("/api/bm/linkinfo")
def linkinfo():
    link = request.args.get("link")
    title = ""
    detail = ""

    req = urllib.request.Request(link, data = None, headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0"})

    try:
        res = urllib.request.urlopen(req)
    except:
        return json.dumps({"result": "success", "title": title, "detail": detail})

    soup = BeautifulSoup(res, "html.parser", from_encoding=res.info().get_param("charset"))

    try:
        title = soup.title.string
    except:
        pass

    if soup.find(name="meta", attrs={"name":"description"}) != None:
        detail = soup.find(name="meta", attrs={"name":"description"}).get("content")

    if soup.find(name="meta", attrs={"name":"og:description"}) != None and detail == "":
        detail = soup.find(name="meta", attrs={"name":"og:description"}).get("content")

    if soup.find(name="meta", attrs={"name":"twitter:description"}) != None and detail == "":
        detail = soup.find(name="meta", attrs={"name":"twitter:description"}).get("content")

    return json.dumps({"result": "success", "title": title, "detail": detail})


@app.route("/api/bm/edit")
def edit_bookmark():
    b_id = request.args.get("id")
    title = request.args.get("title")
    detail = request.args.get("detail")
    note = request.args.get("note")
    tags = request.args.get("tags")

    t2 = tags.split(",")

    try:
        t1 = cur.execute("SELECT * from bookmarks WHERE id = (?)", (b_id,)).fetchone()["tags"].split(",")
    except:
        return json.dumps({"result": "error", "res-text": "couldn't get tags for bookmark id "+b_id})

    tags_old = list(set(t1).difference(set(t2)).union(set(t1).intersection(set(t2))))
    tags_new = list(set(t2).difference(set(t1)))
    tags_missing = list(set(t1).difference(set(t2)))

    # try insert new tags, if they already exist then increase usage by one
    for tag in tags_new:
        if tag != "":
            try:
                cur.execute("INSERT INTO tags (name, usage) VALUES (?, ?)", (tag, 1))
                conn.commit()
            except sqlite3.IntegrityError: # already exists
                cur.execute("UPDATE tags SET usage = usage+1 WHERE name = (?)", (tag,))
                conn.commit()

    # for every tag thats missing (deleted) decrease usage by one and remove if 0
    for tag in tags_missing:
        if cur.execute("SELECT * FROM tags WHERE name = (?)", (tag,)).fetchone()["usage"] == 1:
            cur.execute("DELETE FROM tags WHERE name = (?)", (tag,))
            conn.commit()
        else:
            cur.execute("UPDATE tags SET usage = usage-1 WHERE name = (?)", (tag,))
            conn.commit()

    try:
        cur.execute("UPDATE bookmarks SET title = (?), detail = (?), note = (?), tags = (?) WHERE id = (?)", (title, detail, note, tags, b_id))
        conn.commit()
    except:
        return json.dumps({"result": "error", "res-text": "editing failed"})

    bm = cur.execute("SELECT * from bookmarks WHERE id = (?)", (b_id,)).fetchone()
    return json.dumps({"result": "success", "bmhtml": render_template("bookmark.html", bm=bm)})

@app.route("/api/bm/delete")
def delete_bookmark():
    b_id = request.args.get("id")

    try:
        cur.execute("UPDATE bookmarks SET deleted = TRUE WHERE id = (?)", (b_id,))
        conn.commit()
    except:
        return json.dumps({"result": "error", "res-text": "database mark as deleted failed"})

    return json.dumps({"result": "success"})

@app.route("/api/tags/get")
def list_tags():
    tagrows = cur.execute("SELECT name FROM tags ORDER BY usage DESC").fetchall()
    ret = list()
    for row in tagrows:
        ret.append(row[0])

    return json.dumps({"result": "success", "tags": ret})

if __name__ == "__main__":
    app.run()
