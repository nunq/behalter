#!/usr/bin/env python3
"""this module does all the db retrieval"""
from re import search

from behalter.models import Bookmark, Tag, db


def get_all_bookmarks():
    """fetches all undeleted bookmarks from the database,
    ordered by id descending.

    Returns:
        list(Bookmark): list of Bookmark ORM types
    """
    stmt = (
        db.select(Bookmark)
        .where(Bookmark.deleted == False)  # pylint: disable=C0121
        .order_by(Bookmark.id.desc())
    )
    bookmarks = db.session.scalars(stmt)
    return bookmarks


def create_bookmark(title, link, detail, note, tags=None):
    """creates a bookmark in the database, also sets up new tags

    Args:
        title (str): bookmark title (auto fetched)
        link (str): bookmark link
        detail (str): bookmark detail text (auto fetched from html meta description tag)
        note (str): personal note text
        tags (str, optional): bookmark tags. Defaults to None.

    Returns:
        Bookmark: created bookmark element
    """
    try:
        domain = search(r"://(.*?)(/|$)", link).group(1)
    except AttributeError:
        domain = ""

    tags_clean = None
    if tags is not None:
        tags_clean = {
            tag_dirty.strip() for tag_dirty in tags.split(",") if tag_dirty != ""
        }

    bm_tags = []
    if tags_clean:
        for tag_name in tags_clean:
            tag = db.session.execute(
                db.select(Tag).where(Tag.name == tag_name)
            ).scalar()
            if not tag:
                tag = Tag(name=tag_name, usage=0)
                db.session.add(tag)
            bm_tags.append(tag)
            tag.usage += 1

    bm = Bookmark(
        title=title, link=link, detail=detail, domain=domain, note=note, tags=bm_tags
    )
    db.session.add(bm)
    db.session.commit()
    return bm
