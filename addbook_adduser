def add_book(name,price,quantity):
    conn = sqlite3.connect('books.db')
    c = conn.cursor()

    c.execute("INSERT INTO books VALUES ('{}','{}','{}')".format(name,price,quantity))

    conn.commit()
    conn.close()
