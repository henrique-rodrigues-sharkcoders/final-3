import sqlite3

DB_NAME = "vintelligence.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS listings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        brand TEXT,
        price REAL,
        url TEXT,
        estimated_value REAL,
        profit REAL,
        roi REAL,
        score REAL
    )
    """)

    conn.commit()
    conn.close()


def save(listings):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("DELETE FROM listings")

    c.executemany("""
        INSERT INTO listings (
            title, brand, price, url,
            estimated_value, profit, roi, score
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, listings)

    conn.commit()
    conn.close()