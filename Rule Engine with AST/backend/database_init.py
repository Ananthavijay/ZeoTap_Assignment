import sqlite3
import os

DATABASE_PATH = "./database/rules.db"

os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            rule_string TEXT,
            ast TEXT
        )
    ''')

    conn.commit()
    conn.close()
    print("Database and table created successfully!")

if __name__ == "__main__":
    init_db()
