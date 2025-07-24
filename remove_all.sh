#!/bin/bash
docker container prune -f
docker container stop es_db && docker container rm -f es_db || true
docker container stop pg_db && docker container rm -f pg_db || true
docker container stop python_ingest && docker container rm -f python_ingest || true
docker container stop neo4j-test && docker container rm -f neo4j-test || true
docker volume prune -f 
docker rmi -f $(docker images -q)