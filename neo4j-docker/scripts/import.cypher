LOAD CSV WITH HEADERS FROM 'file:///products.csv' AS row
CREATE (:Product {
  product_url: row.product_url,
  product_name: row.product_name,
  product_category_tree: row.product_category_tree,
  pid: row.pid,
  retail_price: toFloat(row.retail_price),
  discounted_price: toFloat(row.discounted_price),
  image: row.image,
  is_FK_Advantage_product: row.is_FK_Advantage_product = 'true',
  description: row.description,
  product_rating: toFloat(row.product_rating),
  overall_rating: toFloat(row.overall_rating),
  brand: row.brand,
  product_specifications: row.product_specifications
});
