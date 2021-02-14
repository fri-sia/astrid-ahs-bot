
import sqlite3 as sql

def with_db():
    conn = sql.connect('astrid.db')
    c = conn.cursor()
    return (conn, c)
