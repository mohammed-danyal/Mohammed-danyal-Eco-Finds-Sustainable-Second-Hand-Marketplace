import sqlite3
import os
import difflib

# ------------------ DB Connection ------------------

def get_db_connection():
    conn = sqlite3.connect("product.db")
    conn.row_factory = sqlite3.Row
    return conn

# ------------------ Create Table ------------------

def create_product_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price TEXT,
            location TEXT,
            category TEXT,
            description TEXT,
            image_url TEXT,
            seller_name TEXT,
            seller_since TEXT,
            seller_phone TEXT,
            seller_email TEXT,
            seller_photo TEXT
        )
    ''')
    conn.commit()
    conn.close()

# ------------------ Add Product ------------------

def add_product(product):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO products (
            title, price, location, category, description, image_url,
            seller_name, seller_since, seller_phone, seller_email, seller_photo
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        product['title'],
        product['price'],
        product['location'],
        product['category'],
        product['description'],
        product['image'],
        product['seller']['name'],
        product['seller']['member_since'],
        product['seller']['phone'],
        product['seller']['email'],
        product['seller']['photo']
    ))
    conn.commit()
    conn.close()

# ------------------ Search Product ------------------

def search_products(keyword):
    conn = get_db_connection()
    cursor = conn.cursor()
    keyword_like = f"%{keyword.lower()}%"
    cursor.execute('''
        SELECT * FROM products 
        WHERE LOWER(title) LIKE ? OR LOWER(category) LIKE ? OR LOWER(description) LIKE ?
    ''', (keyword_like, keyword_like, keyword_like))
    results = cursor.fetchall()

    # Suggest similar titles if exact match fails
    if not results:
        cursor.execute("SELECT title FROM products")
        titles = [row["title"] for row in cursor.fetchall()]
        suggestions = difflib.get_close_matches(keyword, titles, n=5, cutoff=0.4)

        if suggestions:
            suggestion_like = [f"%{s.lower()}%" for s in suggestions]
            results = []
            for s in suggestion_like:
                cursor.execute('''
                    SELECT * FROM products WHERE LOWER(title) LIKE ?
                ''', (s,))
                results.extend(cursor.fetchall())

    conn.close()
    return results

# ------------------ Get All Products ------------------

def get_all_products():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()
    conn.close()
    return rows

# ------------------ Delete Product ------------------

def delete_product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
    conn.commit()
    conn.close()


