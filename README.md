# BDMA

Datapipeline for Big Data Management and Analytics @ [HDM Stuttgart](https://www.hdm-stuttgart.de/).

## Installation

Make sure you have `docker` with the `compose` plugin available on your machine.<br>
Refer to the [documentation](https://docs.docker.com/engine/install/ubuntu/) for help.


### Prequesites

Create two networks for Docker
```bash
docker network create kafka-network && \
docker network create cassandra-network
```


### Start the containers

Run all of these commands inside of the root directory of the repo.

Start Cassandra:
```bash
docker compose -f cassandra/docker-compose.yml up -d
```

Check the cassandra logs with `docker logs -f cassandra` and wait until all database tables have been created.

Start all Kafka components:
```bash
docker compose -f kafka/docker-compose.yml up -d
```
The REST-Interface between Kafka and Cassandra is available at [http://localhost:8083](http://localhost:8083).<br>
Sinks are at [http://localhost:8083/connectors](http://localhost:8083/connectors).
```bash
curl -X GET http://localhost:8083/connectors
```

Start the consumer and monitor incoming data with `docker logs -f consumer`.
```bash
docker compose -f consumer/docker-compose.yml up -d
```

Make sure to create `producer_twitter/keys.py` and add your Twitter API keys. Then, you can start the producers:
```bash
docker compose -f producer_twitter/docker-compose.yml up -d
docker compose -f producer_news/docker-compose.yml up -d
```

Sanity check that all containers are running with `docker ps -a`.<br>
Verify the output of the producer with `docker logs -f producer_twitter`.

All data that gets streamed to the `twittersink` topic will be propagated to Cassandra for storage.

Verify that Cassandra is receiving data:
```bash
docker exec -it cassandra bash

# inside the container, run:
cqlsh

select * from pipeline.twitter;
select * from pipeline.news;
```


## Tear Down

To remove resources associated with one component, run `docker compose -f <file> down`.<br>
To remove _all_ docker resources, execute [reset_docker.sh](./reset-docker.sh).
