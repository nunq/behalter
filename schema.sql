DROP TABLE IF EXISTS bookmarks;

CREATE TABLE bookmarks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created INTEGER NOT NULL DEFAULT (unixepoch()),
    title TEXT NOT NULL,
    currentlink TEXT NOT NULL,
    origlink TEXT NOT NULL,
    archivelink TEXT NOT NULL,
    domain TEXT NOT NULL,
    description TEXT NOT NULL,
    note TEXT NOT NULL,
    tags TEXT NOT NULL
);

