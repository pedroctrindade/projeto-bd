FROM postgres:16

ENV POSTGRES_DB=products_db
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres

COPY flipkart_convertido.csv /docker-entrypoint-initdb.d/products.csv
COPY init.sql /docker-entrypoint-initdb.d/init.sql
