FROM neo4j:5.20.0-community

ENV NEO4J_AUTH=neo4j/test

COPY import /import
COPY scripts /scripts

ENV NEO4JLABS_PLUGINS='["apoc"]'
ENV NEO4J_dbms_security_procedures_unrestricted=apoc.*
ENV NEO4J_dbms_security_procedures_allowlist=apoc.*
ENV NEO4J_apoc_import_file_enabled=true

CMD ["sh", "-c", "neo4j & sleep 20 && cypher-shell -u neo4j -p test -f /scripts/import.cypher && tail -f logs/neo4j.log"]
