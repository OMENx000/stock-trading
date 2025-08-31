import sqlite3

# open schema.sql
with open("schema.sql") as f:
    schema = f.read()

# connect to finance.db
conn = sqlite3.connect("finance.db")
conn.executescript(schema)
conn.close()

print("Database initialized ✅")