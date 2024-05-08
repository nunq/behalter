#!/usr/bin/env python3
"""this module does all the db retrieval"""
from re import search

from behalter import app
from behalter.models import *
from sqlalchemy.exc import InvalidRequestError


def get_all_bookmarks():
    # try:
    stmt = db.select(Bookmark).where(Bookmark.deleted == False)  # pylint: disable=C0121
    bookmarks = db.session.scalars(stmt)
    return bookmarks


def create_bookmark(title, link, detail, note, tags=None):
    try:
        domain = search(r"://(.*?)(/|$)", link).group(1)
    except AttributeError:
        pass
        # TODO

    tags_clean = None
    if tags is not None:
        tags_clean = [tag_dirty.strip() for tag_dirty in tags.split(",")]

    bm_tags = []
    if tags_clean:
        for tag_name in tags_clean:
            tag = Tag.query.filter_by(name=tag_name).first()  # TODO
            if not tag:
                tag = Tag(name=tag_name, usage=1)
                db.session.add(tag)
            bm_tags.append(tag)

    bm = Bookmark(
        title=title, link=link, detail=detail, domain=domain, note=note, tags=bm_tags
    )
    db.session.add(bm)
    db.session.commit()
    return bm
