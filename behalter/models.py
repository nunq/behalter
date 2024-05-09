#!/usr/bin/env python3
"""db models"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime as dt
from datetime import timezone
from typing import List

from flask_sqlalchemy import SQLAlchemy as sa
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Table
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from behalter import app


class Base(DeclarativeBase):  # pylint: disable=R0903
    """sqlalchemy orm base class for declarative mappings"""

    pass  # pylint: disable=W0107


db = sa(model_class=Base)
db.init_app(app)

# bookmark <-> tag association table
bookmark_tag = Table(
    "bookmark_tag",
    Base.metadata,
    Column("bookmark", ForeignKey("bookmark.id"), primary_key=True),
    Column("tag", ForeignKey("tag.name"), primary_key=True),
)


@dataclass
class Bookmark(db.Model):  # pylint: disable=R0903,R0902
    """bookmark database model"""

    __tablename__ = "bookmark"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created: Mapped[dt] = mapped_column(default=dt.now(timezone.utc))
    deleted: Mapped[bool] = mapped_column(default=False)
    title: Mapped[str] = mapped_column()
    detail: Mapped[str] = mapped_column()
    link: Mapped[str] = mapped_column(unique=True)
    domain: Mapped[str] = mapped_column()
    note: Mapped[str] = mapped_column()
    tags: Mapped[List[Tag]] = relationship(
        secondary=bookmark_tag, back_populates="bookmarks"
    )


@dataclass
class Tag(db.Model):  # pylint: disable=R0903
    """tag database model"""

    __tablename__ = "tag"

    name: Mapped[str] = mapped_column(primary_key=True)
    usage: Mapped[int] = mapped_column()
    bookmarks: Mapped[List[Bookmark]] = relationship(
        secondary=bookmark_tag, back_populates="tags"
    )


# create all models as db tables
with app.app_context():
    db.create_all()
