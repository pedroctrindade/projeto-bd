CREATE TABLE products (
  uniq_id TEXT,
  product_name TEXT,
  product_category_tree TEXT,
  description TEXT,
  product_specifications TEXT
);

COPY products FROM '/docker-entrypoint-initdb.d/products.csv' DELIMITER ';' CSV HEADER;
