#!/usr/bin/env python3
"""bundles util functions"""
from datetime import timezone
import urllib.request

from bs4 import BeautifulSoup
from flask import jsonify
from tzlocal import get_localzone
from user_agent import generate_user_agent

from behalter import app


@app.template_filter()
def datetime_to_human(dt):
    """utility func that converts a utc python datetime object into local dd-mm-YYYY"""
    local_tz = get_localzone()
    dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(local_tz).strftime("%d-%m-%Y %H:%M")


def fetch_link_info(url):
    """try to extract title and html meta description from a url"""
    title = ""
    detail = ""

    ua = generate_user_agent()
    req = urllib.request.Request(url, data=None, headers={"User-Agent": ua})

    try:
        res = urllib.request.urlopen(req)
    except Exception:  # pylint: disable=W0718
        return jsonify({"result": "success", "title": title, "detail": detail})

    soup = BeautifulSoup(
        res, "html.parser", from_encoding=res.info().get_param("charset")
    )

    try:
        title = soup.title.string.strip()
    except Exception:  # pylint: disable=W0718
        pass

    if soup.find(name="meta", attrs={"name": "description"}) is not None:
        detail = soup.find(name="meta", attrs={"name": "description"}).get("content")

    if (
        soup.find(name="meta", attrs={"name": "og:description"}) is not None
        and detail == ""
    ):
        detail = soup.find(name="meta", attrs={"name": "og:description"}).get("content")

    if (
        soup.find(name="meta", attrs={"name": "twitter:description"}) is not None
        and detail == ""
    ):
        detail = soup.find(name="meta", attrs={"name": "twitter:description"}).get(
            "content"
        )

    return jsonify({"result": "success", "title": title, "detail": detail})
