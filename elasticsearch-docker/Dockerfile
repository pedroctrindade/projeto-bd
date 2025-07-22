FROM docker.elastic.co/elasticsearch/elasticsearch:8.13.4

# Copia o CSV para dentro do container
COPY flipkart_convertido.csv /usr/share/elasticsearch/products.csv

# Copia o entrypoint
COPY entrypoint.sh /usr/local/bin/entrypoint.sh

# Variáveis de ambiente para modo single-node, heap e desabilitar segurança
ENV discovery.type=single-node
ENV ES_JAVA_OPTS="-Xms512m -Xmx512m"
ENV xpack.security.enabled=false
ENV xpack.security.http.ssl.enabled=false

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]