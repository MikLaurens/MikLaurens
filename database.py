# database.py (полная версия)
import sqlite3
from datetime import datetime


class Database:
    def __init__(self, db_name='meat_house.db'):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER DEFAULT 0
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS raw_materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            quantity INTEGER DEFAULT 0
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            sale_date DATE NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS production (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            production_date DATE NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
        ''')

        self.conn.commit()

    # Товары
    def add_product(self, name, price, stock=0):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO products (name, price, stock) VALUES (?, ?, ?)',
                       (name, price, stock))
        self.conn.commit()
        return cursor.lastrowid

    def get_products(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM products')
        return cursor.fetchall()

    def delete_product(self, product_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
        self.conn.commit()

    # Производство
    def add_production(self, product_id, quantity, production_date):
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO production (product_id, quantity, production_date)
        VALUES (?, ?, ?)
        ''', (product_id, quantity, production_date))

        cursor.execute('''
        UPDATE products SET stock = stock + ? WHERE id = ?
        ''', (quantity, product_id))

        self.conn.commit()
        return cursor.lastrowid

    def get_production(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT p.id, pr.name, p.quantity, p.production_date 
        FROM production p
        JOIN products pr ON p.product_id = pr.id
        ''')
        return cursor.fetchall()

    def get_production_by_period(self, start_date, end_date):
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT p.id, pr.name, p.quantity, p.production_date 
        FROM production p
        JOIN products pr ON p.product_id = pr.id
        WHERE p.production_date BETWEEN ? AND ?
        ORDER BY p.production_date
        ''', (start_date, end_date))
        return cursor.fetchall()

    # Продажи
    def add_sale(self, product_id, quantity, sale_date):
        cursor = self.conn.cursor()

        cursor.execute('SELECT stock FROM products WHERE id = ?', (product_id,))
        stock = cursor.fetchone()[0]

        if stock < quantity:
            raise ValueError("Недостаточно товара на складе")

        cursor.execute('''
        INSERT INTO sales (product_id, quantity, sale_date)
        VALUES (?, ?, ?)
        ''', (product_id, quantity, sale_date))

        cursor.execute('''
        UPDATE products SET stock = stock - ? WHERE id = ?
        ''', (quantity, product_id))

        self.conn.commit()
        return cursor.lastrowid

    def get_sales(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT s.id, p.name, s.quantity, p.price, s.sale_date 
        FROM sales s
        JOIN products p ON s.product_id = p.id
        ''')
        return cursor.fetchall()

    def get_sales_by_period(self, start_date, end_date):
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT s.id, p.name, s.quantity, p.price, s.sale_date 
        FROM sales s
        JOIN products p ON s.product_id = p.id
        WHERE s.sale_date BETWEEN ? AND ?
        ORDER BY s.sale_date
        ''', (start_date, end_date))
        return cursor.fetchall()

    # Отчеты
    def get_stock_report(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, name, stock, price FROM products')
        return cursor.fetchall()

    def update_product(self, product_id, name, price, stock):
        cursor = self.conn.cursor()
        cursor.execute('''
        UPDATE products 
        SET name = ?, price = ?, stock = ?
        WHERE id = ?
        ''', (name, price, stock, product_id))
        self.conn.commit()