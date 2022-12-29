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
    author_verified BOOLEAN,
    author_created_at TEXT,
    label TEXT,
    PRIMARY KEY (id)
);

CREATE TABLE news (
    title TEXT,
    url TEXT,
    created_at TEXT,
    PRIMARY KEY (title, url)
);
