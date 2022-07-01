def retrieve_books():
    conn = sqlite3.connect('books.db')
    c = conn.cursor()

    c.execute("SELECT * FROM books")
    b = c.fetchall()

    conn.commit()
    conn.close()
    return b

def retrieve_purchases():
    conn = sqlite3.connect('books.db')
    c = conn.cursor()

    c.execute("SELECT * FROM purchases")
    b = c.fetchall()

    conn.commit()
    conn.close()
    return b

def retrieve_users():
    conn = sqlite3.connect('books.db')
    c = conn.cursor()

    c.execute("SELECT * FROM users")
    b = c.fetchall()

    conn.commit()
    conn.close()
    return b
