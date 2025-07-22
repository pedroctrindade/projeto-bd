CREATE TABLE products (
  product_url TEXT,
  product_name TEXT,
  product_category_tree TEXT,
  pid TEXT,
  retail_price NUMERIC,
  discounted_price NUMERIC,
  image TEXT,
  is_FK_Advantage_product BOOLEAN,
  description TEXT,
  product_rating NUMERIC,
  overall_rating NUMERIC,
  brand TEXT,
  product_specifications TEXT
);

COPY products FROM '/docker-entrypoint-initdb.d/products.csv' DELIMITER ',' CSV HEADER;
