# Connect database through SQL
import sqlite3

try:
    with sqlite3.connect("my.db") as conn:
        pass
except sqlite3.OperationalError as e:
    print("Failed to open database:", e)
