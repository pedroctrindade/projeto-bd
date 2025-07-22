#!/bin/bash

/usr/share/elasticsearch/bin/elasticsearch &

echo "Aguardando Elasticsearch iniciar..."
until curl -s http://localhost:9200 >/dev/null; do sleep 2; done

echo "Criando índice products com mapeamentos..."
curl -X PUT "http://localhost:9200/products" -H 'Content-Type: application/json' -d '
{
  "mappings": {
    "properties": {
      "uniq_id": { "type": "keyword" },
      "crawl_timestamp": { "type": "date", "format": "yyyy-MM-dd HH:mm:ss Z||strict_date_optional_time||epoch_millis" },
      "product_url": { "type": "text" },
      "product_name": { "type": "text" },
      "product_category_tree": { "type": "text" },
      "pid": { "type": "keyword" },
      "retail_price": { "type": "float" },
      "discounted_price": { "type": "float" },
      "image": { "type": "text" },
      "is_FK_Advantage_product": { "type": "boolean" },
      "description": { "type": "text" },
      "product_rating": { "type": "float" },
      "overall_rating": { "type": "float" },
      "brand": { "type": "keyword" }
    }
  }
}'

echo "Importando dados do CSV..."

tail -n +2 /usr/share/elasticsearch/products.csv | while IFS=';' read -r uniq_id crawl_timestamp product_url product_name product_category_tree pid retail_price discounted_price image is_FK_Advantage_product description product_rating overall_rating brand
do
  # Normalize boolean
  is_FK_Advantage_product=$(echo "$is_FK_Advantage_product" | tr '[:upper:]' '[:lower:]')
  if [[ "$is_FK_Advantage_product" != "true" ]]; then
    is_FK_Advantage_product="false"
  fi

  # Campos numéricos ou nulos
  null_if_invalid() {
    if [[ "$1" == "No rating available" || -z "$1" ]]; then
      echo null
    else
      echo "$1"
    fi
  }

  retail_price=$(null_if_invalid "$retail_price")
  discounted_price=$(null_if_invalid "$discounted_price")
  product_rating=$(null_if_invalid "$product_rating")
  overall_rating=$(null_if_invalid "$overall_rating")

  # Datas
  if [[ -z "$crawl_timestamp" ]]; then
    crawl_timestamp=null
  else
    crawl_timestamp="\"$crawl_timestamp\""
  fi

  # uniq_id nulo
  if [[ -z "$uniq_id" ]]; then
    uniq_id=null
  else
    uniq_id="\"$uniq_id\""
  fi

  # Função para escapar aspas e barras para JSON
  escape_json() {
    echo "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'
  }

  product_url=$(escape_json "$product_url")
  product_name=$(escape_json "$product_name")
  product_category_tree=$(escape_json "$product_category_tree")
  pid=$(escape_json "$pid")
  image=$(escape_json "$image")
  description=$(escape_json "$description")
  brand=$(escape_json "$brand")


  # Inserção do documento
  curl  -X POST "http://localhost:9200/products/_doc" \
    -H 'Content-Type: application/json' \
    -d "{
      \"uniq_id\": $uniq_id,
      \"crawl_timestamp\": $crawl_timestamp,
      \"product_url\": \"$product_url\",
      \"product_name\": \"$product_name\",
      \"product_category_tree\": \"$product_category_tree\",
      \"pid\": \"$pid\",
      \"retail_price\": $retail_price,
      \"discounted_price\": $discounted_price,
      \"image\": \"$image\",
      \"is_FK_Advantage_product\": $is_FK_Advantage_product,
      \"description\": \"$description\",
      \"product_rating\": $product_rating,
      \"overall_rating\": $overall_rating,
      \"brand\": \"$brand\"
    }"
done

wait
