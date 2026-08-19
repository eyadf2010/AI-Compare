import sqlite3
import re


def normalize_words(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)

    return set(text.split())

def get_snapitee_product(product_name):
    connection = sqlite3.connect("products.db")
    cursor = connection.cursor()

    cursor.execute("""
    SELECT product_name, price_aed, available
    FROM products
    """)

    products = cursor.fetchall()
    connection.close()

    input_words = normalize_words(product_name)

    if not input_words:
        return None

    best_match = None
    best_score = 0

    for database_name, price, available in products:
        database_words = normalize_words(database_name)

        if not database_words:
            continue

        matching_words = input_words & database_words

        input_coverage = len(matching_words) / len(input_words)
        database_coverage = len(matching_words) / len(database_words)

        # Every word from the user's name must match.
        if input_coverage < 1.0:
            continue

        # At least 60% of the database name must also match.
        if database_coverage < 0.60:
            continue

        score = database_coverage

        if score > best_score:
            best_score = score
            best_match = {
                "product_name": database_name,
                "price": price,
                "available": bool(available)
            }

    return best_match


def get_database_info(product_names):
        database_info = []

        for product_name in product_names:
            product = get_snapitee_product(product_name)

            if product:
                database_info.append({
                    "product_name": product_name,
                    "snapitee_price": product["price"],
                    "available": product["available"],
                    "found_in_database": True
                })
            else:
                database_info.append({
                    "product_name": product_name,
                    "snapitee_price": None,
                    "available": None,
                    "found_in_database": False
                })

        return database_info


if __name__ == "__main__":
    connection = sqlite3.connect("products.db")
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        price_aed REAL NOT NULL,
        available INTEGER NOT NULL
    )
    """)

    products = [
        ("iPhone 17 Pro Max", 5099, 1),
        ("Galaxy S26 Ultra", 5099, 1),
        ("MacBook Air M5 13-inch", 4299, 1),
        ("iPhone 17", 3699, 0),
        ("Galaxy S26", 3499, 1)
    ]

    cursor.executemany("""
    INSERT INTO products (product_name, price_aed, available)
    VALUES (?, ?, ?)
    """, products)

    connection.commit()
    connection.close()

    print("Sample price database created!")
