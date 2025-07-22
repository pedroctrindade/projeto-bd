# Multi-Database Query Benchmark

Este projeto compara o desempenho de consultas no campo `description` usando três bancos de dados diferentes:

- 🔵 PostgreSQL
- 🟣 Neo4j
- 🟡 Elasticsearch

## Estrutura

- `postgres-docker/`: carrega o CSV em uma tabela relacional.
- `neo4j-docker/`: cria nós com os campos do CSV.
- `elasticsearch-docker/`: indexa os dados para consulta full-text.
- `query-tester/`: container Python que compara os tempos de resposta.
- `docker-compose.yml`: orquestra tudo.

## Como usar

```bash
docker compose up --build
```

## Resultado Esperado

O container `tester` imprimirá algo como:

```
PostgreSQL: 0.0321 s | 1 rows
Elasticsearch: 0.0105 s | 1 docs
Neo4j: 0.0457 s | 1 nodes
```

Você pode alterar os dados no CSV para novos testes.

---

Criado para comparar a performance de consulta textual entre tecnologias.
