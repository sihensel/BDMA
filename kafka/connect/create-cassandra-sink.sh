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
    "topic.twittersink.pipeline.twitter.mapping": "label=value.label, created_at=value.created_at, author=value.author, tweet=value.tweet, id=value.id, engagements=value.engagements, verified=value.verified, author_created_at=value.author_created_at, followers_count=value.followers_count, friends_count=value.friends_count, statuses_count=value.statuses_count, listedcount=value.listedcount, bot=value.bot",
    "topic.twittersink.pipeline.twitter.consistencyLevel": "LOCAL_QUORUM"
  }
}'

echo "Starting News Sink"
curl -s \
     -X POST http://localhost:8083/connectors \
     -H "Content-Type: application/json" \
     -d '{
  "name": "newssink",
  "config":{
    "connector.class": "com.datastax.oss.kafka.sink.CassandraSinkConnector",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "false",
    "key.converter": "org.apache.kafka.connect.json.JsonConverter",
    "key.converter.schemas.enable":"false",
    "tasks.max": "10",
    "topics": "newssink",
    "contactPoints": "cassandra",
    "loadBalancing.localDc": "datacenter1",
    "topic.newssink.pipeline.news.mapping": "created_at=value.created_at, title=value.title, url=value.url",
    "topic.newssink.pipeline.news.consistencyLevel": "LOCAL_QUORUM"
  }
}'

echo "Done."
