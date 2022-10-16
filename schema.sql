DROP TABLE IF EXISTS bookmarks;
DROP TABLE IF EXISTS tags;

CREATE TABLE bookmarks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created INTEGER NOT NULL DEFAULT (unixepoch()),
    deleted BOOLEAN NOT NULL DEFAULT FALSE,
    title TEXT NOT NULL,
    detail TEXT NOT NULL DEFAULT "",
    currentlink TEXT NOT NULL,
    origlink TEXT NOT NULL,
    archivelink TEXT NOT NULL,
    domain TEXT NOT NULL,
    note TEXT NOT NULL,
    tags TEXT NOT NULL
);

CREATE TABLE tags (
  name TEXT PRIMARY KEY NOT NULL,
  usage INTEGER NOT NULL
);
