import pandas as pd
import json
import re
from elasticsearch import Elasticsearch, helpers

es = Elasticsearch("http://localhost:9200")

INDEX_NAME = "products"

# Mapping do índice com os campos e tipos que queremos
mapping = {
    "mappings": {
        "properties": {
            "product_name": {"type": "text"},
            "product_category_tree": {"type": "text"},
            "description": {"type": "text"},
            "product_specification": {
                "type": "nested",
                "properties": {
                    "key": {"type": "keyword"},
                    "value": {"type": "text"}
                }
            }
        }
    }
}

def create_index():
    if es.indices.exists(INDEX_NAME):
        print(f"Índice {INDEX_NAME} já existe. Apagando e recriando...")
        es.indices.delete(index=INDEX_NAME)
    es.indices.create(index=INDEX_NAME, body=mapping)
    print(f"Índice {INDEX_NAME} criado com mapping.")

def parse_product_specifications(spec_str):

    json_like = spec_str.replace('=>', ':')

    json_like = json_like.replace('""', '"')


    try:
        pattern = r'\{"product_specifications":\s*(\[.*\])\}'
        match = re.search(pattern, json_like)
        if match:
            specs_json = match.group(1)
            specs = json.loads(specs_json)
            return specs
        else:

            return []
    except Exception as e:
        print(f"Erro ao parsear product_specifications: {e}")
        return []

def generate_docs(df):
    for _, row in df.iterrows():
        specs = parse_product_specifications(row["product_specifications"]) if row["product_specifications"] else []
        yield {
            "_index": INDEX_NAME,
            "_id": row["uniq_id"],
            "_source": {
                "product_name": row["product_name"],
                "product_category_tree": row["product_category_tree"],
                "description": row["description"],
                "product_specifications": specs
            }
        }

def main():
    create_index()

    df = pd.read_csv("flipkart_com-ecommerce_sample.csv", sep=";", usecols=["uniq_id", "product_name", "product_category_tree", "description", "product_specifications"])
    df.fillna("", inplace=True)

    success, _ = helpers.bulk(es, generate_docs(df))
    print(f"Importação concluída com {success} documentos indexados.")

if __name__ == "__main__":
    main()
