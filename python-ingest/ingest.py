import pandas as pd
import psycopg2
import json
import re
from elasticsearch import Elasticsearch, helpers

es = Elasticsearch("http://es_db:9200")
pg_host = "pg_db"

INDEX_NAME = "products"

# Mapping do índice com os campos e tipos que queremos
mapping = {
    "mappings": {
        "properties": {
            "product_name": {"type": "text"},
            "product_category_tree": {"type": "text"},
            "description": {"type": "text"},
            "product_specification": {  "type": "text" },
            "text_search": {
                "type": "text",
                "analyzer": "english"
            }
        }
    }
}

words_to_remove = {
    "I", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them", "my", "your", "his", "its", "our",
    "their", "mine", "yours", "hers", "ours", "theirs", "this", "that", "these", "those", "who", "whom", "whose",
    "which", "what", "where", "when", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other",
    "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "about", "above", "across",
    "after", "against", "along", "among", "around", "at", "before", "behind", "below", "beneath", "beside", "between",
    "beyond", "but", "by", "concerning", "despite", "down", "during", "except", "for", "from", "in", "inside", "into",
    "like", "near", "of", "off", "on", "onto", "out", "outside", "over", "past", "regarding", "since", "through",
    "throughout", "till", "to", "toward", "under", "underneath", "until", "up", "upon", "with", "within", "without"
}

def remove_stopwords(text):
    if text is None or (isinstance(text, float) and pd.isna(text)):
        return ''
    if isinstance(text, (list, dict)):
        text = json.dumps(text)
    text = str(text)
    words = re.findall(r'\b\w+\b', text.lower())
    filtered = [word for word in words if word not in words_to_remove]
    return ' '.join(filtered)

def create_index():
    if es.indices.exists(index=INDEX_NAME):
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
        #specs = parse_product_specifications(row["product_specifications"]) if row["product_specifications"] else []
        yield {
            "_index": INDEX_NAME,
            "_id": row["uniq_id"],
            "_source": {
                "product_name": remove_stopwords(row["product_name"]),
                "product_category_tree": remove_stopwords(row["product_category_tree"]),
                "description": remove_stopwords(row["description"]),
                "product_specifications": remove_stopwords(row["product_specifications"]),
                "text_search": remove_stopwords(f"{row['product_name']} {row['product_category_tree']} {row['description']} {row['product_specifications']}")
            }
        }

def elasticsearch_ingest():

    create_index()

    df = pd.read_csv("flipkart_com-ecommerce_sample.csv", sep=";", usecols=["uniq_id", "product_name", "product_category_tree", "description", "product_specifications"])
    df.fillna("", inplace=True)

    success, _ = helpers.bulk(es, generate_docs(df))
    print(f"Importação concluída com {success} documentos indexados.")

def postgresql_ingest():
    try:
        # Caminho para o CSV
        csv_path = 'flipkart_com-ecommerce_sample.csv'
        
        # Ler o CSV
        df = pd.read_csv(csv_path, sep=";", usecols=["uniq_id", "product_name", "product_category_tree", "description", "product_specifications"])

        for col in df.columns:
            if col != 'uniq_id':
                df[col] = df[col].apply(remove_stopwords)

        # Conectar ao PostgreSQL
        conn = psycopg2.connect(
            dbname='products_db',
            user='postgres',
            password='postgres',
            host=pg_host,
            port='5432'
        )
        cur = conn.cursor()

        # Criar tabela (remover se já existir)
        cur.execute("""
            DROP TABLE IF EXISTS products;
            CREATE TABLE products (
                uniq_id TEXT,
                product_name TEXT,
                product_category_tree TEXT,
                description TEXT,
                product_specifications TEXT,
                text_search tsvector GENERATED ALWAYS AS (
                    to_tsvector(
                        'english',
                        coalesce(product_name, '') || ' ' ||
                        coalesce(product_category_tree, '') || ' ' ||
                        coalesce(description, '') || ' ' ||
                        coalesce(product_specifications, '')
                    )
                ) STORED
            );
            CREATE INDEX idx_text_search ON products USING GIN (text_search);
        """)
        conn.commit()

        # Inserir dados linha por linha
        for _, row in df.iterrows():
            cur.execute("""
                INSERT INTO products (uniq_id, product_name, product_category_tree, description, product_specifications)
                VALUES (%s, %s, %s, %s, %s);
            """, tuple(row.fillna('')))
        conn.commit()

        cur.close()
        conn.close()
        print("Importação para PostgreSQL concluída com sucesso.")

    except Exception as e:
        print("Erro durante a ingestão:", e)
 
def main():
    postgresql_ingest()
    elasticsearch_ingest()


if __name__ == "__main__":
    main()
