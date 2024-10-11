#!/usr/bin/env python3
import argparse
from time import sleep
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
import requests

ap = argparse.ArgumentParser()
ap.add_argument("-o", "--old-file", help="sqlite file from old behalter version", required=True)
ap.add_argument("-n", "--new-file", help="sqlite file for new behalter version", required=True)
args = ap.parse_args()

def chomp(text):
    return text.strip().replace('\r\n', '').replace('\n', '')

def u(text):
    return requests.utils.quote(chomp(text))

def red(text):
    return f"\033[31m{text}\033[0m"

def blue(text):
    return f"\033[34m{text}\033[0m"

def green(text):
    return f"\033[32m{text}\033[0m"

def cyan(text):
    return f"\033[36m{text}\033[0m"

# connect to old sqlite db
engine = sa.create_engine(f"sqlite:///{args.old_file}")
metadata = sa.MetaData()
bm = sa.Table("bookmarks", metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("created", sa.Integer),
    sa.Column("deleted", sa.Boolean),
    sa.Column("title", sa.String),
    sa.Column("detail", sa.String),
    sa.Column("currentlink", sa.String),
    sa.Column("origlink", sa.String),
    sa.Column("archivelink", sa.String),
    sa.Column("domain", sa.String),
    sa.Column("note", sa.String),
    sa.Column("tags", sa.String)
)

Session = sessionmaker(bind=engine)
session = Session()

# first create all
old_items = session.query(bm).all()
for old_item in old_items:
    title = chomp(old_item.title)
    if old_item.deleted:
        print(f"{cyan("SKIPPING")} deleted id {old_item.id}: {title}")
        continue

    r = requests.get(f"http://127.0.0.1:5000/api/bm/add?link={u(old_item.currentlink)}&title={u(title)}&note={u(old_item.note)}&tags={u(old_item.tags)}&detail={u(old_item.detail)}")

    if r.status_code == 302:
        print(f"{blue("SKIPPING")} duplicate: {title}")
    elif r.status_code == 200:
        print(f"{green("SUCCESS")} for {title}")
    else:
        print(f"{red("ERROR")} for {title}")
        print(r)

# just to make sure everything has been written to disk
print("waiting 10 secs ...")
sleep(10)

# connect to new sqlite db
new_engine = sa.create_engine(f"sqlite:///{args.new_file}")

# fix all timestamps
with new_engine.connect() as conn:
    for old_item in old_items:
        if old_item.deleted:
            print(f"{cyan("SKIPPING")} deleted id {old_item.id}")
            continue

        ts = old_item.created
        dt = datetime.fromtimestamp(ts)

        query = sa.text("UPDATE bookmark SET created_time = :created_time WHERE link = :oldlink")
        conn.execute(query, {"created_time": dt, "oldlink": old_item.currentlink})
        conn.commit()

        print(f"{green("FIXED")} created_time for old id {old_item.id}")

session.close()
