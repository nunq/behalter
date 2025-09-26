#!/usr/bin/env python3
"""flask views"""
from pathlib import Path

from flask import jsonify
from flask import render_template
from flask import request
from flask import send_from_directory

from behalter import app
from behalter import database
from behalter.util import fetch_link_info


@app.route("/")
def index():
    """show all undeleted bookmark on index"""
    bm = database.get_all_bookmarks(include_deleted=False)
    return render_template("index.html", bookmarks=bm)


@app.route("/favicon.ico")
def favicon():
    """favicon route"""
    return send_from_directory(
        Path(app.root_path) / "static",
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


@app.route("/export")
def export_bookmarks():
    """dump all bookmarks, including deleted ones, as json"""
    bm = list(database.get_all_bookmarks(include_deleted=True))
    return jsonify(bm)


# search
@app.route("/search")
def search_bookmarks():
    """search bookmarks by tag, id, or custom user query"""
    ra = request.args
    q = ra.get("q").strip()

    if q.startswith("tag:"):
        res = database.search_bookmarks_by_tag(q.removeprefix("tag:"))
    elif q.startswith("dup:"):
        # handle duplicate id searches before regular id searches
        res = database.search_bookmark_by_id(q.removeprefix("dup:"))
        dup_id = q.removeprefix("dup:")
        return render_template(
            "results.html", query=f"duplicate check (id:{dup_id})", results=list(res)
        )
    elif q.startswith("id:"):
        res = database.search_bookmark_by_id(q.removeprefix("id:"))
    else:
        res = database.search_bookmarks_by_query(q)

    return render_template("results.html", query=q, results=list(res))


# api
@app.route("/api/bookmarks", methods=["GET"])
def get_bookmarks():
    """get all undeleted bookmarks"""
    bm = database.get_all_bookmarks(include_deleted=False)
    return jsonify({"result": "success", "bookmarks": list(bm)})


@app.route("/api/bookmarks", methods=["POST"])
def create_bookmark():
    """create a new bookmark, return html of newly created bookmark"""
    data = request.get_json()
    title = data.get("title")
    link = data.get("link")
    detail = data.get("detail")
    note = data.get("note")
    tags = data.get("tags", "")

    is_duplicate, dup_id = database.check_duplicate(link)
    if is_duplicate:
        return jsonify({"result": "duplicate", "href": f"/search?q=dup:{dup_id}"}), 409

    if tags != "":
        created_bm = database.create_bookmark(title, link, detail, note, tags)
    else:
        created_bm = database.create_bookmark(title, link, detail, note)

    return jsonify(
        {
            "result": "success",
            "bmhtml": render_template("bookmark.html", bm=created_bm),
        }
    ), 201


@app.route("/api/bookmarks/<int:bookmark_id>", methods=["PUT"])
def update_bookmark(bookmark_id):
    """update all fields for a bookmark. return edited bookmark's html on success."""
    data = request.get_json()
    title = data.get("title")
    detail = data.get("detail")
    note = data.get("note")
    tags = data.get("tags")

    success, ret = database.edit_bookmark(bookmark_id, title, detail, note, tags)
    if success:
        return jsonify(
            {"result": "success", "bmhtml": render_template("bookmark.html", bm=ret)}
        )
    return jsonify({"result": "error", "res-text": "editing failed"}), 400


@app.route("/api/bookmarks/<int:bookmark_id>", methods=["DELETE"])
def delete_bookmark(bookmark_id):
    """delete a bookmark from the database"""
    success = database.mark_bookmark_as_deleted(bookmark_id)
    if success:
        return jsonify({"result": "success"})
    return jsonify({"result": "error", "res-text": "database mark as deleted failed"}), 400


@app.route("/api/linkinfo")
def link_info():
    """fetch html title and detail info for a url"""
    ra = request.args
    link = ra.get("link")
    return fetch_link_info(link)


@app.route("/api/tags")
def list_tags():
    """return a list of tags, ordered by usage. used by awesomplete tag input"""
    ret = database.get_tags_ordered_by_usage()
    return jsonify({"result": "success", "tags": ret})


# webhook
@app.route(f"/{app.config['WEBHOOK_PREFIX']}/webhook/add", methods=["POST"])
def add_bookmark_webhook():
    """add a new bookmark from inoreader webhook request"""
    ra = request.args
    token = ra.get("auth")

    if not token or token != app.config["WEBHOOK_TOKEN"]:
        return "unauthorized", 401 # http unauthorized

    post_body = request.get_json()
    newest_item = post_body["items"][0]

    link = newest_item["canonical"][0]["href"]
    linkinfo = fetch_link_info(link, no_json=True)

    if linkinfo["result"] == "success":
        title = linkinfo["title"]
        detail = linkinfo["detail"]
    else:
        title = newest_item["title"]
        detail = newest_item["summary"]["content"]
    tags = "from-webhook"
    note = ""

    is_duplicate, dup_id = database.check_duplicate(link) # pylint: disable=unused-variable
    if is_duplicate:
        return "duplicate detected", 409 # http conflict

    database.create_bookmark(title, link, detail, note, tags)

    return "success", 201
