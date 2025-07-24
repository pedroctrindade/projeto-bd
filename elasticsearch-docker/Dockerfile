FROM docker.elastic.co/elasticsearch/elasticsearch:8.13.4

# Instala Python e pip
USER root
RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/*

# Copia o script Python e instala dependências
COPY ingest.py /usr/share/elasticsearch/ingest.py
COPY requirements.txt /usr/share/elasticsearch/requirements.txt
COPY flipkart_com-ecommerce_sample.csv flipkart_com-ecommerce_sample.csv
RUN pip install --no-cache-dir -r /usr/share/elasticsearch/requirements.txt

USER elasticsearch

ENV discovery.type=single-node
ENV ES_JAVA_OPTS="-Xms512m -Xmx512m"
ENV xpack.security.enabled=false
ENV xpack.security.http.ssl.enabled=false

# Executa Elasticsearch e depois o script
CMD /bin/bash -c "/usr/share/elasticsearch/bin/elasticsearch & \
    sleep 20 && \
    python3 /usr/share/elasticsearch/ingest.py && \
    wait"