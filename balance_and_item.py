def getBalance(dataobj, conn, addr):
    email = dataobj['email']
    conndb = sqlite3.connect('books.db')
    c = conndb.cursor()

    c.execute("SELECT cash FROM users WHERE email = '{}'".format(email.lower()))
    result = c.fetchone()

    data_obj = result[0]
    dicto = {'balance': str(data_obj)}
    json_obj = json.dumps(dicto)
    send(json_obj, conn, addr)
    conndb.commit()
    conndb.close()


def deposit(data_obj, conn, addr):
    email = data_obj['email']
    amount = int(data_obj['amount'])
    conndb = sqlite3.connect('books.db')
    c = conndb.cursor()
    user_lock.acquire()
    c.execute("UPDATE users SET cash = cash + '{}' WHERE email = '{}'".format(amount, email.lower()))
    user_lock.release()
    getBalance(data_obj, conn, addr)
    conndb.commit()
    conndb.close()
    
 def getItems(dataobj, conn, addr):

    conndb = sqlite3.connect('books.db')
    c = conndb.cursor()
    c.execute("SELECT * FROM books")
    list = c.fetchall()

    dicto = {"response": 'here you are', "items": list}
    # dicto = {'items': list}
    json_obj = json.dumps(dicto)
    send(json_obj,conn,addr)
    conndb.commit()
    conndb.close()
    
 def getProfile(data_obj, conn, addr):
    email = data_obj['email']
    conndb = sqlite3.connect('books.db')
    c = conndb.cursor()
    c.execute("SELECT fname, lname, email, cash FROM users WHERE email = '{}'".format(email.lower()))

    data_obj = c.fetchone()

    dicto = {'fname': data_obj[0], 'lname': data_obj[1], 'email': data_obj[2], 'cash': data_obj[3] }
    json_obj = json.dumps(dicto)
    send(json_obj, conn, addr)

    conndb.commit()
    conndb.close()
