FROM docker.elastic.co/elasticsearch/elasticsearch:8.13.4

COPY products.csv /usr/share/elasticsearch/products.csv
COPY entrypoint.sh /usr/local/bin/entrypoint.sh

RUN chmod +x /usr/local/bin/entrypoint.sh

ENV discovery.type=single-node
ENV ES_JAVA_OPTS="-Xms512m -Xmx512m"

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
