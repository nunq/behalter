#!/usr/bin/env python3
from __future__ import annotations

from sqlalchemy import Column
from sqlalchemy import Table
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship

from flask_sqlalchemy import SQLAlchemy as sa
from datetime import datetime as datetime
from datetime import timezone
from typing import List

from behalter import app

class Base(DeclarativeBase):
  pass

db = sa(model_class=Base)
db.init_app(app)

bookmark_tag = Table(
    "bookmark_tag",
    Base.metadata,
    Column("bookmark", ForeignKey("bookmark.id"), primary_key=True),
    Column("tag", ForeignKey("tag.name"), primary_key=True),
)

class Bookmark(db.Model):
  __tablename__ = "bookmark"

  id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
  created: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))
  deleted: Mapped[bool] = mapped_column(default=False)
  title: Mapped[str] = mapped_column()
  detail: Mapped[str] = mapped_column()
  currentlink: Mapped[str] = mapped_column()
  origlink: Mapped[str] = mapped_column()
  archivelink: Mapped[str] = mapped_column()
  domain: Mapped[str] = mapped_column()
  note: Mapped[str] = mapped_column()
  #tags: Mapped[List[Tag]] = relationship(secondary=bookmark_tag, back_populates="tag")
  # TODO wenn keine bookmarks in db dann gibts hier nen fehler

class Tag(db.Model):
  __tablename__ = "tag"

  name: Mapped[str] = mapped_column(primary_key=True)
  usage: Mapped[int] = mapped_column()
  #bookmarks: Mapped[List[Bookmark]] = relationship(secondary=bookmark_tag, back_populates="bookmark")

# create all models as db tables
with app.app_context():
  db.create_all()
