#!/bin/sh

echo "Starting Twitter Sink"
curl -s \
     -X POST http://localhost:8083/connectors \
     -H "Content-Type: application/json" \
     -d '{
  "name": "twittersink",
  "config":{
    "connector.class": "com.datastax.oss.kafka.sink.CassandraSinkConnector",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "false",  
    "key.converter": "org.apache.kafka.connect.json.JsonConverter",
    "key.converter.schemas.enable":"false",
    "tasks.max": "10",
    "topics": "twittersink",
    "contactPoints": "cassandra",
    "loadBalancing.localDc": "datacenter1",
    "topic.twittersink.pipeline.twitter.mapping": "created_at=value.created_at, author=value.author, tweet=value.tweet, id=value.id, engagements=value.engagements, author_verified=value.author_verified, author_created_at=value.author_created_at",
    "topic.twittersink.pipeline.twitter.consistencyLevel": "LOCAL_QUORUM"
  }
}'

echo "Starting Article Sink"
curl -s \
     -X POST http://localhost:8083/connectors \
     -H "Content-Type: application/json" \
     -d '{
  "name": "articlesink",
  "config":{
    "connector.class": "com.datastax.oss.kafka.sink.CassandraSinkConnector",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "false",
    "key.converter": "org.apache.kafka.connect.json.JsonConverter",
    "key.converter.schemas.enable":"false",
    "tasks.max": "10",
    "topics": "articlesink",
    "contactPoints": "cassandra",
    "loadBalancing.localDc": "datacenter1",
    "topic.articlesink.pipeline.articles.mapping": "created_at=value.created_at, title=value.title, url=value.url",
    "topic.articlesink.pipeline.articles.consistencyLevel": "LOCAL_QUORUM"
  }
}'

echo "Done."
