DROP KEYSPACE IF EXISTS kafkapipeline;

CREATE KEYSPACE IF NOT EXISTS kafkapipeline
WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };

USE kafkapipeline;

CREATE TABLE twitter (
    created_at TEXT,
    tweet TEXT,
    author TEXT,
    PRIMARY KEY (created_at, author)
);
