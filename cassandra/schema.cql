DROP KEYSPACE IF EXISTS pipeline;

CREATE KEYSPACE IF NOT EXISTS pipeline
WITH REPLICATION = {
    'class': 'SimpleStrategy',
    'replication_factor': 1
};

USE pipeline;

CREATE TABLE twitter (
    id TEXT,
    created_at TEXT,
    tweet TEXT,
    author TEXT,
    engagements INT,
    verified TEXT,
    author_created_at TEXT,
    label TEXT,
    followers_count INT,
    friends_count INT,
    statuses_count INT,
    listedcount INT,
    author_location TEXT,
    bot TEXT,
    PRIMARY KEY (id)
);

CREATE TABLE news (
    title TEXT,
    url TEXT,
    created_at TEXT,
    PRIMARY KEY (title, url)
);
