import sqlite3
import csv


class DatabaseManager:
    def __init__(self, db_name="project.db"):
        self.db_name = db_name

    def connect(self):
        return sqlite3.connect(self.db_name)

    def create_tables(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""CREATE TABLE IF NOT EXISTS users(
                        NAME TEXT,
                        EMAIL TEXT UNIQUE,
                        PASSWORD TEXT
                    )""")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stocks (
                    ticker TEXT NOT NULL,
                    name TEXT NOT NULL,
                    market_cap TEXT NOT NULL,
                    description TEXT NOT NULL,
                    user_email TEXT NOT NULL,
                    PRIMARY KEY (ticker, user_email)
                )
            """)


class UserManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def add_user(self, name, email, password):
        with self.db_manager.connect() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email,  password))
            except sqlite3.IntegrityError:
                return False
            else:
                conn.commit()
                return True

    def get_user(self, email):
        with self.db_manager.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE EMAIL = ?", (email,))
            return cursor.fetchone()

    def email_check(self, email):
        with self.db_manager.connect() as conn:
            cursor = conn.cursor()
            have_email = cursor.execute("SELECT COUNT(*) FROM users WHERE EMAIL = ?", (email,)).fetchone()[0]
            return have_email

    def get_password(self, email):
        with self.db_manager.connect() as conn:
            cursor = conn.cursor()
            database_password = cursor.execute(f"SELECT PASSWORD FROM users WHERE email = ?", (email,)).fetchone()[0]
            return database_password

    def get_name(self, email):
        with self.db_manager.connect() as conn:
            cursor = conn.cursor()
            name = cursor.execute(f"SELECT NAME FROM users WHERE EMAIL=\'" + email + "\'").fetchone()[0]
            return name

    def change_password(self, email, new_password):
        with self.db_manager.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(f"UPDATE users SET PASSWORD=? WHERE EMAIL=?", (new_password, email))
            conn.commit()


class StockManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def save_stock(self, ticker, name, market_cap, description, user_email):
        with self.db_manager.connect() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO stocks (ticker, name, market_cap, description, user_email) 
                    VALUES (?, ?, ?, ?, ?)
                """, (ticker, name, market_cap, description, user_email))
                conn.commit()
                print(f"Stock {ticker} saved successfully!")
            except sqlite3.IntegrityError:
                print(f"Stock {ticker} is already saved.")

    def delete_stock(self, ticker, email):
        with self.db_manager.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM stocks WHERE ticker = ? AND user_email = ?", (ticker, email))
            conn.commit()
            if cursor.rowcount > 0:
                print(f"Stock {ticker} deleted successfully!")
            else:
                print(f"Stock {ticker} not found.")

    def see_saved_stocks(self, email):
        with self.db_manager.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT ticker, name, market_cap, description FROM stocks WHERE  user_email = ?", (email,))
            stocks = cursor.fetchall()
            return stocks



