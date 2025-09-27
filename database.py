# database.py
import sqlite3

# Connect to DB
conn = sqlite3.connect("billing.db")
c = conn.cursor()

# Create table if not exists
c.execute("""CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            party TEXT,
            truck_no TEXT,
            item TEXT,
            qty REAL,
            payment_mode TEXT,
            date TEXT)""")
conn.commit()

def insert_bill(party, truck, item, qty, payment_mode, date):
    c.execute("INSERT INTO bills (party, truck_no, item, qty, payment_mode, date) VALUES (?, ?, ?, ?, ?, ?)",
              (party, truck, item, qty, payment_mode, date))
    conn.commit()
    return c.lastrowid
