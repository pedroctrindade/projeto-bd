#!/bin/bash

# Cria a network se não existir
docker network inspect db_network >/dev/null 2>&1 || docker network create db_network

cd postgres-docker
docker container stop pg_db && docker container rm -f pg_db || true
docker build -t pg_db_img:1.0 .
docker run --name pg_db --network db_network -d -p 5432:5432 pg_db_img:1.0

cd ../elasticsearch-docker
docker container stop es_db && docker container rm -f es_db || true
docker build -t es_db_img:1.0 .
docker run --name es_db --network db_network -d -p 9200:9200 -p 9300:9300 es_db_img:1.0

cd ../python-ingest
docker container stop python_ingest && docker container rm -f python_ingest || true
docker build -t python_ingest_img:1.0 .
docker run --name python_ingest --network db_network python_ingest_img:1.0
