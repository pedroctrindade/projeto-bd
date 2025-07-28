import csv
import string
import json
from neo4j import GraphDatabase

def connect_to_neo4j(uri, user, password):
    """Establish connection to Neo4j."""
    driver = GraphDatabase.driver(uri, auth=(user, password))
    return driver

def clean_text(text):
    """Clean text by removing unwanted characters and normalizing."""
    translator = str.maketrans('', '', string.punctuation)
    return text.translate(translator).strip().lower()

def parse_product_category_tree(category_tree):
    """Clean and extract values from product_category_tree."""
    return [clean_text(value) for value in category_tree.strip("[]").split(">>") if value]

def parse_product_specifications(specifications):
    """Parse the product_specifications column into a single list of concatenated key-value pairs."""
    try:
        print(f"Parsing specifications: {specifications}")
        
        # Remove 'product_specification': from the string
        specifications = specifications.replace("'product_specification':", "")
        print(f"Specifications after removal: {specifications}")
        
        # Preprocess the input to replace '=>' with ':' for JSON compatibility
        specifications = specifications.replace('=>', ':')
        
        # Attempt to parse the input as JSON
        parsed_specs = json.loads(specifications)
        
        # Extract the list of specifications from the 'product_specification' key
        if isinstance(parsed_specs, dict) and 'product_specification' in parsed_specs:
            parsed_specs = parsed_specs['product_specification']
        
        # Ensure parsed_specs is a list of dictionaries
        if not isinstance(parsed_specs, list):
            print(f"Unexpected format for specifications: {parsed_specs}")
            return []
        
        pairs = []
        for spec in parsed_specs:
            print(f"spec ==>: {spec}")
            if isinstance(spec, dict):  # Ensure spec is a dictionary
                key = spec.get('key', '').strip()
                value = spec.get('value', '').strip()
                if key and value:
                    pairs.append(f"{key} {value}")  # Concatenate key and value
                elif key:
                    pairs.append(f"{key}")  # Include only the key if value is missing
                elif value:
                    pairs.append(f"{value}")  # Include only the value if key is missing
            else:
                print(f"Unexpected item in specifications: {spec}")
        return pairs
    except json.JSONDecodeError:
        print(f"Error parsing specifications: {specifications}")
        return []

def create_product_node(tx, product_id, product_name, category_tree_values, description, specification, text_search):
    """Create product node with cleaned attributes."""
    try:
        query = """
        MERGE (p:Product {id: $product_id})
        SET p.name = $product_name,
            p.category_tree = $category_tree_values,
            p.description = $description,
            p.specifications = $specification,
            p.text_search = $text_search
        """
        tx.run(query, product_id=product_id, product_name=product_name, category_tree_values=category_tree_values,
               description=description, specification=specification,text_search=text_search)
    except Exception as e:
        print(f"Error creating product node for {product_id}: {e}")
    


def process_csv(file_path, driver):
    """Process CSV and insert data into Neo4j."""
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        with driver.session() as session:
            i = 0
            for row in reader:
                i += 1
                if i % 20 == 0:  # Print every 1000 products processed
                    print(f"Processed {i} products so far.")
                product_id = row['uniq_id']
                product_name = row.get('product_name', '').strip()
                category_tree = row.get('product_category_tree', '').strip()
                description = row.get('description', '').strip()
                specifications = row.get('product_specifications', '').strip()

                # Clean and extract values
                category_tree_values = parse_product_category_tree(category_tree)
                specification = parse_product_specifications(specifications)

                #Create the full text search
                text_search = f"{product_name} {' '.join(category_tree_values)} {description} {' '.join(specification)}"

                # Write transaction to Neo4j
                session.write_transaction(create_product_node, product_id, product_name, category_tree_values,
                                          description, specification, text_search)
                
                # if i == 10:  # Limit processing to 10 rows for testing
                #     break
    #session.run("""
    #    CREATE FULLTEXT INDEX full_text_search_index
    #    FOR (n:Product) ON EACH [n.text_search]
    #    """)

if __name__ == "__main__":
    # Configuration
    uri = "bolt://localhost:7687"  # Adjust if necessary
    user = "neo4j"
    password = "produtounicamp"  # Replace with your Neo4j password
    csv_file_path = "flipkart_com-ecommerce_sample.csv"  # Replace with your CSV file path
    words_to_remove = {"I", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them", "my", "your", "his", "her", "its", "our", "their", "mine", "yours", "hers", "ours", "theirs", "this", "that", "these", "those", "who", "whom", "whose", "which", "what", "where", "when", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very",
  "about", "above", "across", "after", "against", "along", "among", "around", "at", "before", "behind", "below", "beneath", "beside", "between", "beyond", "but", "by", "concerning", "despite", "down", "during", "except", "for", "from", "in", "inside", "into", "like", "near", "of", "off", "on", "onto", "out", "outside", "over", "past", "regarding", "since", "through", "throughout", "till", "to", "toward", "under", "underneath", "until", "up", "upon", "with", "within", "without"}


    # Connect to Neo4j and process CSV
    driver = connect_to_neo4j(uri, user, password)
    try:
        process_csv(csv_file_path, driver)
    finally:
        driver.close()
