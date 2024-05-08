#!/usr/bin/env python3
"""this module does all the db retrieval"""
from re import search

from sqlalchemy import or_
from flask import jsonify

from behalter.models import Bookmark, Tag, db


def get_all_bookmarks(include_deleted=False):
    """fetches all undeleted bookmarks from the database,
    ordered by id descending.

    Returns:
        list(Bookmark): list of Bookmark ORM types
    """
    stmt = (
        db.select(Bookmark)
        .where(
            or_(
                Bookmark.deleted == False,  # pylint: disable=C0121
                # sql shortcut to avoid branching this function
                Bookmark.deleted == include_deleted,
            )
        )
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


def get_tags_ordered_by_usage():
    """fetch tags from tag db table, ordered by their usage desc

    Returns:
        list(tag): list of tag names
    """
    stmt = db.select(Tag.name).order_by(Tag.usage.desc())
    res = db.session.execute(stmt).scalars()
    tags_ordered = list(res)
    return tags_ordered


def mark_bookmark_as_deleted(id_to_delete):
    try:
        bm = db.session.execute(
            db.select(Bookmark).filter_by(id=id_to_delete)
        ).scalar_one()
        bm.deleted = True
        db.session.commit()
        return True
    except:
        return False
