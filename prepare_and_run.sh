#!/bin/bash

cd postgres-docker
docker container stop pg_db && docker container rm -f pg_db || true
docker build -t pg_db_img:1.0 .
docker run --name pg_db -d -p 5432:5432 pg_db_img:1.0

cd ../elasticsearch-docker
docker container stop es_db && docker container rm -f es_db || true
docker build -t es_db_img:1.0 .
docker run --name es_db -d -p 9200:9200 -p 9300:9300 es_db_img:1.0
