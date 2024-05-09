#!/usr/bin/env python3
"""bundles util functions"""
import urllib.request

from bs4 import BeautifulSoup
from flask import jsonify

from behalter import app


@app.template_filter()
def datetime_to_human(dt):
    return dt.strftime("%d-%m-%Y")


def fetch_link_info(url):
    title = ""
    detail = ""

    req = urllib.request.Request(
        url,
        data=None,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0"
        },
    )

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
