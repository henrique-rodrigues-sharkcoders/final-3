import sqlite3

DB = "vintelligence.db"


def init_db():

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS listings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        brand TEXT,
        price REAL,
        url TEXT UNIQUE,
        estimated_value REAL,
        profit REAL,
        roi REAL,
        score REAL
    )
    """)

    conn.commit()
    conn.close()


def save(listings):

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    for item in listings:

        try:
            c.execute("""
            INSERT OR IGNORE INTO listings (
                title, brand, price, url,
                estimated_value, profit, roi, score
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, item)

        except:
            continue

    conn.commit()
    conn.close()