CREATE TABLE products (
  uniq_id TEXT,
  crawl_timestamp TIMESTAMP,
  product_url TEXT,
  product_name TEXT,
  product_category_tree TEXT,
  pid TEXT,
  retail_price NUMERIC,
  discounted_price NUMERIC,
  image TEXT,
  is_FK_Advantage_product BOOLEAN,
  description TEXT,
  product_rating TEXT,
  overall_rating TEXT,
  brand TEXT
);

COPY products FROM '/docker-entrypoint-initdb.d/products.csv' DELIMITER ';' CSV HEADER;
