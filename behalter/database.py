#!/usr/bin/env python3
"""this module does all the db retrieval"""
from datetime import datetime as dt
from datetime import timezone
from re import search

from sqlalchemy import or_

from behalter.models import Bookmark
from behalter.models import bookmark_tag
from behalter.models import db
from behalter.models import Tag


def get_all_bookmarks(include_deleted=False):
    """fetches all undeleted bookmarks from the database,
    ordered by id descending.

    Returns:
        list(Bookmark): list of Bookmark ORM types
    """
    stmt = (
        db.select(Bookmark)
        .filter(
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


def search_bookmarks_by_tag(tag):
    """search bookmarks by tag"""
    stmt = (
        db.select(Bookmark)
        .join(bookmark_tag, Bookmark.id == bookmark_tag.c.bookmark)
        .join(Tag, Tag.name == bookmark_tag.c.tag)
        .filter(
            Bookmark.deleted == False,  # pylint: disable=C0121
            Tag.name.like(f"%{tag}%"),
        )
        .order_by(Bookmark.id.desc())
    )
    bookmarks = db.session.execute(stmt).scalars()
    return bookmarks


def search_bookmark_by_id(b_id):
    """search a bookmark by id"""
    stmt = db.select(Bookmark).filter(
        Bookmark.deleted == False, Bookmark.id == b_id  # pylint: disable=C0121
    )
    bookmarks = db.session.scalars(stmt)
    return bookmarks


def search_bookmarks_by_query(query):
    """search bookmarks by user query in various db fields"""
    stmt = (
        db.select(Bookmark)
        .filter(
            Bookmark.deleted == False,  # pylint: disable=C0121
            or_(
                Bookmark.title.like(f"%{query}%"),
                Bookmark.link.like(f"%{query}%"),
                Bookmark.detail.like(f"%{query}%"),
                Bookmark.note.like(f"%{query}%"),
            ),
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
        tags (str, optional): comma separated string of tags. Defaults to None.

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
                db.select(Tag).filter(Tag.name == tag_name)
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
    """mark a bookmark as deleted in the database

    Args:
        id_to_delete (int): id of bookmark

    Returns:
        bool: successful operation or not
    """
    try:
        bm = db.session.execute(
            db.select(Bookmark).filter_by(id=id_to_delete)
        ).scalar_one()
        bm.deleted = True
        bm.deleted_time = dt.now(timezone.utc)
        db.session.commit()
        return True
    except Exception:  # pylint: disable=W0718
        return False


def edit_bookmark(b_id, new_title, new_detail, new_note, new_tags_str):
    """update all fields for a bookmark in the database

    Args:
        b_id (int): bookmark id
        new_title (str): new bookmark title
        new_detail (str): new bookmark detail text
        new_note (str): new personal note text
        new_tags_str (str): new comma separated string of tags

    Returns:
        (bool, Bookmark|None): bool indicates function success,
        if True Bookmark is the edited bookmark. If not -> None
    """
    new_tags = set()
    if new_tags_str != "":
        new_tags = {
            tag_dirty.strip()
            for tag_dirty in new_tags_str.split(",")
            if tag_dirty != ""
        }

    try:
        bm_db = db.session.execute(db.select(Bookmark).filter_by(id=b_id)).scalar_one()
        db_tags = {tag.name for tag in bm_db.tags}

        tags_new = new_tags - db_tags
        tags_missing = db_tags - new_tags

        # try insert new tags, if they already exist increment usage
        for tag_name in tags_new:
            tag = db.session.execute(
                db.select(Tag).filter(Tag.name == tag_name)
            ).scalar()
            if not tag:
                tag = Tag(name=tag_name, usage=0)
                db.session.add(tag)
            bm_db.tags.append(tag)
            tag.usage += 1

        # for every tag thats missing (deleted) decrease usage by one and remove if 0
        for tag_name in tags_missing:
            tag = db.session.execute(
                db.select(Tag).filter(Tag.name == tag_name)
            ).scalar()
            tag.usage -= 1
            bm_db.tags.remove(tag)
            if len(tag.bookmarks) == 0:
                db.session.delete(tag)

        bm_db.title = new_title
        bm_db.detail = new_detail
        bm_db.note = new_note
        db.session.commit()
        return True, bm_db
    except Exception:  # pylint: disable=W0718
        return False, None


def check_duplicate(link_to_check):
    """check if link_to_check is already associated with a bookmark in the db"""
    dup = db.session.execute(
        db.select(Bookmark.id).filter(Bookmark.link == link_to_check)
    ).scalar()
    if dup:
        print("is dup!")
        return True, dup

    return False, None
