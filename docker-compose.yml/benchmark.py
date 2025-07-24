import time
import psycopg2
from elasticsearch import Elasticsearch
from neo4j import GraphDatabase

def benchmark_postgres():
    print("PostgreSQL:")

    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()

    # Query 1: campo description sem índice
    query1 = """SELECT uniq_id, product_name FROM products 
                WHERE to_tsvector('english', coalesce(description, '')) 
                @@ plainto_tsquery('english', 'solid shorts');"""
    start1 = time.time()
    cur.execute(query1)
    r1 = cur.fetchall()
    d1 = time.time() - start1

    # Query 2: campo text_search com índice FTS
    query2 = """SELECT uniq_id, product_name FROM products 
                WHERE text_search @@ plainto_tsquery('portuguese', 'solid shorts');"""
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
            "match": {
                "description": "solid shorts"
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
                "text_search": "bsolid shorts"
            }
        }
    }
    start2 = time.time()
    r2 = es.search(index="products", body=query2)
    d2 = time.time() - start2

    print(f"  Query 1 (description): {r1['hits']['total']['value']} resultados em {d1:.4f} s")
    print(f"  Query 2 (text_search): {r2['hits']['total']['value']} resultados em {d2:.4f} s\n")


def benchmark_neo4j(uri, name):
    print(f"Neo4j ({name}):")
    driver = GraphDatabase.driver(uri, auth=("neo4j", "test"))

    # Query 1 – campo description (sem índice direto)
    query1 = """
    MATCH (p:Product)
    WHERE p.description CONTAINS 'solid' AND p.description CONTAINS 'shorts'
    RETURN p.uniq_id, p.product_name
    """
    with driver.session() as session:
        start1 = time.time()
        r1 = list(session.run(query1))
        d1 = time.time() - start1

    # Query 2 – campo text_search (com estratégia de indexação invertida ou atributo)
    query2 = """
    MATCH (p:Product)
    WHERE p.text_search CONTAINS 'bicicleta' AND p.text_search CONTAINS 'feminina' AND p.text_search CONTAINS 'algodão'
    RETURN p.uniq_id, p.product_name
    """
    with driver.session() as session:
        start2 = time.time()
        r2 = list(session.run(query2))
        d2 = time.time() - start2

    print(f"  Query 1 (description): {len(r1)} resultados em {d1:.4f} s")
    print(f"  Query 2 (text_search): {len(r2)} resultados em {d2:.4f} s\n")
    driver.close()


if __name__ == "__main__":
    print("Benchmarking queries:\n")

    benchmark_postgres()
    benchmark_elasticsearch()
    #benchmark_neo4j("bolt://localhost:7687", "attribute-strategy")
    #benchmark_neo4j("bolt://localhost:7688", "inverted-index-strategy")
