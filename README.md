# BDMA

Datapipeline for Big Data Management and Analytics @ [HDM Stuttgart](https://www.hdm-stuttgart.de/).

## Installation

Make sure you have `docker` and `docker-compose` available on your machine.


### Prequesites

Create two networks for Docker

```bash
docker network create kafka-network
docker network create cassandra-network
```

### Start the containers

Make sure to run all of these commands inside of the root directory of the repo.

Start Cassandra:
```bash
docker-compose -f cassandra/docker-compose.yml up -d
```

Check the cassandra logs with `docker logs -f cassandra` and make sure it says `Startup Complete`.

Start Kafka:
```bash
docker-compose -f kafka/docker-compose.yml up -d
```

Kafka exposes a Web-UI at [http://localhost:9000](http://localhost:9000), which is used to create the Kafka cluster.<br>
The REST-Interface between Kafka and Cassandra is available at [http://localhost:8083](http://localhost:8083).

Make sure to create `twitter/keys.py` and add your API keys. Then, you can start the producer:
```bash
docker-compose -f twitter/docker-compose.yml up -d
```

Sanity check that all containers are running with `docker ps -a`.<br>
Verify the output of the producer with `docker logs -f twitter`.

All data that gets streamed to the `twittersink` topic will be propagated to Cassandra for storage.

Verify that Cassandra is receiving data:
```bash
docker exec -it cassandra bash

# inside the container, run:
cqlsh --cqlversion=3.4.5 127.0.0.1

select * from kafkapipeline.twitter;
```
