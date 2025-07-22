#!/bin/bash

/elasticsearch/bin/elasticsearch &

echo "Aguardando Elasticsearch iniciar..."
until curl -s http://localhost:9200 >/dev/null; do
  sleep 2
done

curl -X PUT "http://localhost:9200/products" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "retail_price": { "type": "float" },
      "discounted_price": { "type": "float" },
      "product_rating": { "type": "float" },
      "overall_rating": { "type": "float" },
      "is_FK_Advantage_product": { "type": "boolean" }
    }
  }
}
'

tail -n +2 /usr/share/elasticsearch/products.csv | while IFS=',' read -r product_url product_name product_category_tree pid retail_price discounted_price image is_FK_Advantage_product description product_rating overall_rating brand product_specifications
do
  curl -X POST "http://localhost:9200/products/_doc" -H 'Content-Type: application/json' -d "{
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
    \"brand\": \"$brand\",
    \"product_specifications\": \"$product_specifications\"
  }"
done

wait
