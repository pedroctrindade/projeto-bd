import time
import psycopg2
from elasticsearch import Elasticsearch
from neo4j import GraphDatabase
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

def benchmark_postgres():
    print("PostgreSQL:")

    conn = psycopg2.connect(
        dbname="products_db",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()

    # Query 1: campo description sem índice
    query1 = """SELECT uniq_id, product_name FROM products 
                WHERE to_tsvector('english', coalesce(description, '')) 
                @@ plainto_tsquery('english', 'short short short short short short short');"""
    start1 = time.time()
    cur.execute(query1)
    r1 = cur.fetchall()
    d1 = time.time() - start1

    # Query 2: campo text_search com índice FTS
    query2 = """SELECT uniq_id, product_name FROM products 
                WHERE text_search @@ plainto_tsquery('english', 'short short short short short short short');"""
    start2 = time.time()
    cur.execute(query2)
    r2 = cur.fetchall()
    d2 = time.time() - start2


    print(f"  Query 1 (description): {len(r1)} resultados em {d1:.4f} s")
    print(f"  Query 2 (text_search): {len(r2)} resultados em {d2:.4f} s\n")
    cur.close()
    conn.close()


def benchmark_elasticsearch():
    print("Elasticsearch:")
    es = Elasticsearch("http://localhost:9200")

    # Query 1 – match no campo description (sem FTS especial)
    query1 = {
        "query": {
            "regexp": {
                "description": {
                    "value": ".*short.*",
                    "case_insensitive": True
                }
            }
        }
    }

    start1 = time.time()
    r1 = es.search(index="products", body=query1)
    d1 = time.time() - start1

    # Query 2 – match no campo text_search (indexado por FTS)
    query2 = {
        "query": {
            "match": {
                "text_search": "short"
            }
        }
    }
    start2 = time.time()
    r2 = es.search(index="products", body=query2)
    d2 = time.time() - start2

    print(f"  Query 1 (description): {r1['hits']['total']['value']} resultados em {d1:.4f} s")
    print(f"  Query 2 (text_search): {r2['hits']['total']['value']} resultados em {d2:.4f} s\n")


def benchmark_neo4j_words(uri, name):
    print(f"Neo4j Word Strategy ({name}):")
    driver = GraphDatabase.driver(uri, auth=("neo4j", "produtounicamp"))

    # Query 1 – campo description (sem índice direto)
    query1 = """
        WITH ["short"] AS input_words
        MATCH (w:Word)-[r]->(p:Product)
        WHERE w.word IN input_words
        WITH p, count(w) AS matched_words
        RETURN p, matched_words
        ORDER BY matched_words DESC
    """
    with driver.session() as session:
        start1 = time.time()
        r1 = list(session.run(query1))
        d1 = time.time() - start1

    print(f"  Query 1 (word strategy): {len(r1)} resultados em {d1:.4f} s")
    driver.close()

def benchmark_neo4j_attribute(uri, name):
    print(f"Neo4j ({name}):")
    driver = GraphDatabase.driver(uri, auth=("neo4j", "produtounicamp"))

    # Query 2 – campo text_search (com estratégia de indexação invertida ou atributo)
    query2 = """
        CALL db.index.fulltext.queryNodes("full_text_search_index", "short") YIELD node, score
        RETURN node.name, score
        ORDER BY score DESC
    """

    with driver.session() as session:
        start2 = time.time()
        r2 = list(session.run(query2))
        d2 = time.time() - start2

    print(f"  Query 2 (text_search): {len(r2)} resultados em {d2:.4f} s\n")
    driver.close()


if __name__ == "__main__":
    print("Benchmarking queries:\n")

    benchmark_postgres()
    benchmark_elasticsearch()
    benchmark_neo4j_words("bolt://localhost:7688", "inverted-index-strategy")
    benchmark_neo4j_attribute("bolt://localhost:7687", "attribute-strategy")

