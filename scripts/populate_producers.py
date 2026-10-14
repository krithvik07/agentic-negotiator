import mysql.connector
import random
import json
from faker import Faker
from datetime import datetime

fake = Faker()

# Connection settings
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "AbhinavRAS"  # Replace with your MySQL root password
DB_NAME = "negotiation_db"

def server_connect():
    return mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD)

def db_connect():
    return mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)

def reset_and_create_schema():
    print(f"This will DROP and recreate the database '{DB_NAME}' and all tables.")
    confirm = input("Type 'reset' to proceed, or press Enter to skip: ").strip().lower()
    if confirm != 'reset':
        print("Skipping DB reset. Proceeding to seed into existing schema (expects domain column in products).")
        return

    # Connect without selecting a database
    srv = server_connect()
    scur = srv.cursor()
    scur.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
    scur.execute(f"CREATE DATABASE {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    scur.close(); srv.close()

    # Connect to the newly created DB and create tables
    conn_schema = db_connect()
    cur = conn_schema.cursor()
    # users
    cur.execute(
        """
        CREATE TABLE users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            role VARCHAR(20) NOT NULL,
            password_hash VARCHAR(200) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB
        """
    )
    # products with domain
    cur.execute(
        """
        CREATE TABLE products (
            id INT AUTO_INCREMENT PRIMARY KEY,
            producer_id INT,
            name VARCHAR(100) NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            quantity INT NOT NULL,
            specs JSON,
            domain VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_products_domain (domain),
            CONSTRAINT fk_products_producer FOREIGN KEY (producer_id) REFERENCES users(id)
        ) ENGINE=InnoDB
        """
    )
    # requests
    cur.execute(
        """
        CREATE TABLE requests (
            id INT AUTO_INCREMENT PRIMARY KEY,
            consumer_id INT,
            product_name VARCHAR(100),
            quantity INT NOT NULL,
            budget DECIMAL(10,2),
            specs JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_requests_consumer FOREIGN KEY (consumer_id) REFERENCES users(id)
        ) ENGINE=InnoDB
        """
    )
    # negotiations
    cur.execute(
        """
        CREATE TABLE negotiations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            producer_id INT,
            consumer_id INT,
            round INT NOT NULL,
            offer JSON,
            consumer_satisfaction DECIMAL(5,2),
            producer_satisfaction DECIMAL(5,2),
            status VARCHAR(20) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_neg_producer FOREIGN KEY (producer_id) REFERENCES users(id),
            CONSTRAINT fk_neg_consumer FOREIGN KEY (consumer_id) REFERENCES users(id)
        ) ENGINE=InnoDB
        """
    )
    conn_schema.commit()
    cur.close(); conn_schema.close()
    print("Database reset and schema created successfully.")

# Optionally reset and create schema
reset_and_create_schema()

# Connect to MySQL DB for seeding
conn = db_connect()
cursor = conn.cursor()

# Settings
num_producers_per_domain = 50
products_per_producer = [1, 2, 3]  # each producer has 1–3 products

# Domain-specific product catalogs and origins
DOMAINS = {
    "agriculture": {
        "product_names": ["Wheat", "Rice", "Corn", "Barley", "Cotton", "Soybeans", "Sugarcane", "Tea", "Coffee"],
        "origins": ["Punjab", "Haryana", "Rajasthan", "Madhya Pradesh", "Uttar Pradesh"]
    },
    "construction": {
        "product_names": ["Cement", "Steel Rods", "Bricks", "Sand", "Aggregate", "Plywood", "Tiles", "Glass"],
        "origins": ["Gujarat", "Maharashtra", "Karnataka", "Odisha", "Chhattisgarh"]
    },
    "handicrafts": {
        "product_names": ["Handmade Pottery", "Wooden Carvings", "Bamboo Crafts", "Handloom Shawls", "Terracotta Art"],
        "origins": ["Jaipur", "Saharanpur", "Kutch", "Kolkata", "Varanasi"]
    },
    "pharmaceuticals": {
        "product_names": ["Paracetamol Tablets", "Amoxicillin Capsules", "Vitamin C Tablets", "Ibuprofen Tablets", "Antiseptic Solution"],
        "origins": ["Hyderabad", "Ahmedabad", "Mumbai", "Baddi", "Pune"]
    },
    "textiles": {
        "product_names": ["Cotton Fabric", "Silk Fabric", "Denim", "Wool Yarn", "Polyester Fabric"],
        "origins": ["Tiruppur", "Surat", "Ludhiana", "Bangalore", "Varanasi"]
    }
}

# Helper to insert a producer user
def insert_producer_user(name: str, email: str, password_hash: str, created_at: str) -> int:
    cursor.execute(
        "INSERT INTO users (name, email, role, password_hash, created_at) VALUES (%s, %s, %s, %s, %s)",
        (name, email, "producer", password_hash, created_at)
    )
    return cursor.lastrowid

# Seed producers and products for each domain
for domain, data in DOMAINS.items():
    product_names = data["product_names"]
    origins = data["origins"]

    print(f"Seeding domain: {domain} with {num_producers_per_domain}+ producers...")

    for i in range(num_producers_per_domain):
        name = f"{domain.capitalize()}Producer{i+1}"
        email = f"{domain}_producer{i+1}@example.com"
        password_hash = fake.sha256(raw_output=False)
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Insert producer
        producer_id = insert_producer_user(name, email, password_hash, created_at)

        # Insert 1–3 random products for each producer
        for _ in range(random.choice(products_per_producer)):
            product_name = random.choice(product_names)
            price = round(random.uniform(20, 100), 2)  # aligned with app ranges
            quantity = random.randint(100, 1000)       # aligned with app ranges
            specs = {"quality": random.choice(["A", "B", "C"]), "origin": random.choice(origins)}
            specs_json = json.dumps(specs)

            cursor.execute(
                "INSERT INTO products (producer_id, name, price, quantity, specs, domain, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (producer_id, product_name, price, quantity, specs_json, domain, created_at)
            )

# Commit changes and close connection
conn.commit()
cursor.close()
conn.close()

print(f"Seeded {num_producers_per_domain} producers per domain across {len(DOMAINS)} domains.")
