#!/usr/bin/env python3

#from behalter import app
from behalter.models import *


def get_all_bookmarks():
  bm = db.session.execute(db.select(Bookmark).where(Bookmark.deleted is False))
  return bm

#def create_bookmark():
