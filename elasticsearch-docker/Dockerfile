FROM docker.elastic.co/elasticsearch/elasticsearch:8.13.4

# Variáveis de ambiente para modo single-node, heap e desabilitar segurança
ENV discovery.type=single-node
ENV ES_JAVA_OPTS="-Xms512m -Xmx512m"
ENV xpack.security.enabled=false
ENV xpack.security.http.ssl.enabled=false