def addToCart(data_obj, conn, addr):
    email = data_obj['email']
    item_name = data_obj['name']
    quantity = data_obj['quantity']
    conndb = sqlite3.connect('books.db')
    c = conndb.cursor()
    purchases_lock.acquire()
    c.execute("INSERT INTO purchases(email,item_name , status, quantity) values ('{}' , '{}', '{}','{}')".format(email.lower(), item_name, 0,quantity))
    purchases_lock.release()
    dicto = {'response': "OK"}
    json_obj = json.dumps(dicto)
    send(json_obj, conn, addr)
    conndb.commit()
    
    
def purchase(data_obj, conn, addr):
    email = data_obj['email']
    quantity = data_obj['quantity']
    itemname=data_obj['item']
    conndb = sqlite3.connect('books.db')
    c = conndb.cursor()
    c.execute("SELECT quantity FROM purchases WHERE email = '{}' and item_name = '{}'".format(email.lower(),itemname))
    orginalQuantity = c.fetchall()
    list = orginalQuantity[0]
    q = int(list[0])
    new_quanity = q-quantity
    c.execute("UPDATE purchases set quantity = '{}' WHERE item_name = '{}'".format(new_quanity, itemname))
    c.execute("UPDATE purchases set status = '{}' WHERE email = '{}'".format(1, email.lower()))
    c.execute("SELECT price FROM books WHERE name = '{}'".format(itemname))
    orginalPrice = c.fetchall()
    l = orginalPrice[0]
    price = int(l[0])

    c.execute("SELECT cash FROM users WHERE email = '{}'".format(email.lower()))
    orginalCash = c.fetchall()
    i = orginalQuantity[0]
    balance = int(list[0])
    new_cash=balance-quantity*price
    c.execute("UPDATE users set cash = '{}' WHERE email = '{}'".format(new_cash, email.lower()))
    conndb.commit()
    conndb.close()    
