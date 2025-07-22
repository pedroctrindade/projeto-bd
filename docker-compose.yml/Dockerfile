version: '3.8'

services:
  postgres:
    build: ./postgres-docker
    ports:
      - "5432:5432"

  neo4j:
    build: ./neo4j-docker
    ports:
      - "7474:7474"
      - "7687:7687"

  elasticsearch:
    build: ./elasticsearch-docker
    ports:
      - "9200:9200"

  tester:
    build: ./query-tester
    depends_on:
      - postgres
      - neo4j
      - elasticsearch
