FROM postgres:16

ENV POSTGRES_DB=products_db
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres

COPY init.sql /docker-entrypoint-initdb.d/
