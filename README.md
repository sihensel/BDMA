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
curl http://localhost:8083/connectors
```
Make sure this returns `["twittersink","newssink"]`.<br>
It might be necessary to manually start `/usr/app/create-cassandra-sink.sh` inside the `kafka-connect` container.

Start the consumer:
```bash
docker compose -f consumer/docker-compose.yml up -d
```

Make sure to create `producer_twitter/keys.py` and add your Twitter API keys. Then, you can start the producers:
```bash
docker compose -f producer_twitter/docker-compose.yml up -d
docker compose -f producer_news/docker-compose.yml up -d
```

Finally, start the dashboard container.
```bash
docker compose -f dashboard/docker-compose.yml up -d
```
The dashboard is available at [http://localhost:8050](http://localhost:8050).

Sanity check that all containers are running with `docker ps -a`.<br>
Verify the output of the producers with `docker logs -f <container_name>`.

All data that gets streamed to the `twittersink` and `newssink` topics will be automatically propagated to Cassandra for storage.

Verify that Cassandra is receiving data:
```bash
docker exec -it cassandra bash

# inside the container, run:
cqlsh

select * from pipeline.twitter;
select * from pipeline.news;
```


### Export Data From Cassandra

First, connect to cassandra via `cqlsh`, as shown above.
```bash
COPY pipeline.twitter TO '/twitter.csv' WITH HEADER=TRUE;
```

Then, copy the .csv from the container to the host.
```bash
docker cp cassandra:/twitter.csv .
```

### Rebuild container

The python container images need to be rebuilt after every code change.

```bash
docker compose -f <directory>/docker-compose.yml build --force-rm --no-cache
```


## Tear Down

To remove resources associated with one component, run `docker compose -f <file> down`.<br>
To remove _all_ docker resources, execute [reset_docker.sh](./reset-docker.sh).
