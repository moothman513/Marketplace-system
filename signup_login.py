def get_password(email):
    conn = sqlite3.connect('books.db')
    c = conn.cursor()

    c.execute("SELECT password FROM users WHERE email = '{}'".format(email.lower()))
    result = c.fetchone()
    password = result[0]
    conn.commit()
    conn.close()
    return password

  
def signup(dataobj, conn, addr):
    email = dataobj['email'].lower()
    password = dataobj['password']
    fName = dataobj['fname'].lower()
    lName = dataobj['lname'].lower()

    conndb = sqlite3.connect('books.db')
    c = conndb.cursor()
    c.execute("SELECT email FROM users WHERE email = '{}'".format(email.lower()))
    result = c.fetchone()


    if (result != None):    # Account already exist
        dicto = {"response": "NO"}  # Account already exist

    else:  # Doesnt exist
        user_lock.acquire()
        c.execute("INSERT INTO users values('{}','{}','{}','{}','{}')".format(fName ,lName,email,password,0))

        user_lock.release()
        dicto = {"response": "OK"}   # Account registered

    json_obj = json.dumps(dicto)  # JSON
    send(json_obj, conn, addr)

    conndb.commit()
    conndb.close()

    
def login(dataobj, conn, addr):
    email = dataobj['email']
    password = dataobj['password'] #string
    conndb = sqlite3.connect('books.db')
    c = conndb.cursor()

    c.execute("SELECT password FROM users WHERE email = '{}'".format(email.lower()))
    result = c.fetchone()

    if result != None:
        retrieved_password = result[0]
        if password == retrieved_password:
            dicto = {"response": 'OK'}
        else:
            dicto = {"response": "Password is incorrect"}
    else:
        dicto = {"response": "This Account Doesnt exist"}


    json_obj = json.dumps(dicto)
    send(json_obj, conn, addr)
    conndb.commit()
    conndb.close()
