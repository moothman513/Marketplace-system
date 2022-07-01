def add_book(name,price,quantity):
    conn = sqlite3.connect('books.db')
    c = conn.cursor()

    c.execute("INSERT INTO books VALUES ('{}','{}','{}')".format(name,price,quantity))

    conn.commit()
    conn.close()
    
    
    
    
def add_user(fname,lname, email,password, cash):
    conn = sqlite3.connect('books.db')
    c = conn.cursor()

    c.execute("INSERT INTO users VALUES ('{}','{}','{}','{}','{}')".format(fname,lname,email,password, cash))

    conn.commit()
    conn.close()
