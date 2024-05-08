#!/usr/bin/env python3
"""bundles util functions"""
from json import dumps

import urllib.request
from bs4 import BeautifulSoup

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
    except:
        return dumps({"result": "success", "title": title, "detail": detail})

    soup = BeautifulSoup(
        res, "html.parser", from_encoding=res.info().get_param("charset")
    )

    try:
        title = soup.title.string.strip()
    except:
        pass

    if soup.find(name="meta", attrs={"name": "description"}) != None:
        detail = soup.find(name="meta", attrs={"name": "description"}).get("content")

    if (
        soup.find(name="meta", attrs={"name": "og:description"}) != None
        and detail == ""
    ):
        detail = soup.find(name="meta", attrs={"name": "og:description"}).get("content")

    if (
        soup.find(name="meta", attrs={"name": "twitter:description"}) != None
        and detail == ""
    ):
        detail = soup.find(name="meta", attrs={"name": "twitter:description"}).get(
            "content"
        )

    return dumps({"result": "success", "title": title, "detail": detail})
