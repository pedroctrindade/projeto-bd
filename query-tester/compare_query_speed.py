import time
import psycopg2
from elasticsearch import Elasticsearch
from neo4j import GraphDatabase

def query_postgres():
    conn = psycopg2.connect(
        dbname="products_db",
        user="postgres",
        password="postgres",
        host="postgres",
        port=5432
    )
    cur = conn.cursor()
    start = time.time()
    cur.execute("SELECT * FROM products WHERE description ILIKE '%camera%'")
    rows = cur.fetchall()
    end = time.time()
    cur.close()
    conn.close()
    return end - start, len(rows)

def query_neo4j():
    driver = GraphDatabase.driver("bolt://neo4j:7687", auth=("neo4j", "test"))
    query = """
    MATCH (p:Product)
    WHERE toLower(p.description) CONTAINS 'camera'
    RETURN p
    """
    start = time.time()
    with driver.session() as session:
        result = session.run(query)
        records = list(result)
    end = time.time()
    driver.close()
    return end - start, len(records)

def query_elasticsearch():
    es = Elasticsearch("http://elasticsearch:9200")
    query = {
        "query": {
            "match": {
                "description": "camera"
            }
        }
    }
    start = time.time()
    res = es.search(index="products", body=query)
    end = time.time()
    return end - start, res['hits']['total']['value']

if __name__ == "__main__":
    print("Running queries on all databases...\n")

    pg_time, pg_hits = query_postgres()
    print(f"PostgreSQL: {pg_time:.4f} s | {pg_hits} rows")

    es_time, es_hits = query_elasticsearch()
    print(f"Elasticsearch: {es_time:.4f} s | {es_hits} docs")

    neo_time, neo_hits = query_neo4j()
    print(f"Neo4j: {neo_time:.4f} s | {neo_hits} nodes")
