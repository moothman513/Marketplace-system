import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QWidget

import socket
import threading
import sqlite3
import json
import os

user_lock = threading.Lock()
purchases_lock = threading.Lock()
item_lock = threading.Lock()

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

CREATE_ACCOUNT = "CREATE_ACCOUNT"
LOGIN = "LOGIN"
DEPOSIT = "DEPOSIT"
GET_BALANCE = "GET_BALANCE"
GET_ITEMS = "GET_ITEMS"
GET_PROFILE = "GET_PROFILE"
ADD_ITEM = "ADD_ITEM"
GET_CART = "GET_CART"
PURCHASE = "PURCHASE"
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)



class ServerGui(QDialog):
    def __init__(self):
        super(ServerGui, self).__init__()
        loadUi("ServerGui.ui",self)
        self.addButton.clicked.connect(self.goToadd)
        self.reportButton.clicked.connect(self.goToReport)

    def goToadd(self):
        book_name = self.nameField.text()
        book_id = self.idField.text()
        book_quantity = self.quantityField.text()
        book_price = self.priceField.text()
        add_book(book_name,book_price,book_quantity,book_id)

    def goToReport(self):
        self.activeLabel.setText(str(get_active_clients_count()))
        self.booksNumberLabel.setText(str(retrieve_books_count()))
        self.usersNumberLabel.setText(str(retrieve_users_count()))




def get_password(email):
    conn = sqlite3.connect('books.db')
    c = conn.cursor()

    c.execute("SELECT password FROM users WHERE email = '{}'".format(email.lower()))
    result = c.fetchone()
    password = result[0]
    conn.commit()
    conn.close()
    return password


def send(json_obj, conn, addr):
    msg_to_send = json_obj.encode(FORMAT)
    msg_length = len(msg_to_send)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    conn.send(send_length)
    conn.send(msg_to_send)

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
    # getBalance(data_obj, conn, addr)
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


# def getProfile(data_obj, conn, addr):
#     email = data_obj['email']
#     conndb = sqlite3.connect('books.db')
#     c = conndb.cursor()
#     c.execute("SELECT fname, lname, email, cash FROM users WHERE email = '{}'".format(email.lower()))
#
#     data_obj = c.fetchone()
#
#     dicto = {'fname': data_obj[0], 'lname': data_obj[1], 'email': data_obj[2], 'cash': data_obj[3] }
#     json_obj = json.dumps(dicto)
#     send(json_obj, conn, addr)
#
#     conndb.commit()
#     conndb.close()


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
    conndb.close()




def add_book(name,price,quantity,id):
    conn = sqlite3.connect('books.db')
    c = conn.cursor()
    c.execute("SELECT name FROM books WHERE name = '{}'".format(name))
    data=c.fetchone()
    if data == None:
        c.execute("INSERT INTO books VALUES ('{}','{}','{}','{}')".format(name,price,quantity,id))
    else:
        c.execute("UPDATE books set quantity = quantity+'{}'".format(quantity))
    conn.commit()
    conn.close()

def add_user(fname,lname, email,password, cash):
    conn = sqlite3.connect('books.db')
    c = conn.cursor()

    c.execute("INSERT INTO users VALUES ('{}','{}','{}','{}','{}')".format(fname,lname,email,password, cash))

    conn.commit()
    conn.close()


def purchase(data_obj, conn, addr):
    email = data_obj['email']
    quantity = data_obj['quantity']
    item_name = data_obj['name']

    conndb = sqlite3.connect('books.db')
    c = conndb.cursor()

    c.execute("SELECT price FROM books WHERE name = '{}'".format(item_name))
    item_price = c.fetchone()[0]
    total_price = quantity * item_price

    user_lock.acquire()
    c.execute("UPDATE users SET cash = cash - '{}' WHERE email = '{}'".format(total_price,email))
    user_lock.release()

    item_lock.acquire()
    c.execute("UPDATE books SET quantity = quantity - '{}' WHERE name = '{}' ".format(quantity, item_name))
    item_lock.release()

    purchases_lock.acquire()
    c.execute("UPDATE purchases SET status = '{}', quantity = '{}' WHERE EMAIL= '{}' and item_name = '{}' and status = '{}'".format(1,0,email,item_name,0))
    purchases_lock.release()
    dicto = {'response': 'OK'}
    json_obj = json.dumps(dicto)
    send(json_obj, conn, addr)

    conndb.commit()
    conndb.close()

def retrieve_books():
    conn = sqlite3.connect('books.db')
    c = conn.cursor()

    c.execute("SELECT * FROM books")
    b = c.fetchall()

    conn.commit()
    conn.close()
    return b


def retrieve_books_count():
    conn = sqlite3.connect('books.db')
    c = conn.cursor()
    c.execute("SELECT count(*) FROM books")
    b = c.fetchone()
    conn.commit()
    conn.close()
    return b[0]

def retrieve_users_count():
    conn = sqlite3.connect('books.db')
    c = conn.cursor()
    c.execute("SELECT count(*) FROM users")
    b = c.fetchone()
    conn.commit()
    conn.close()
    return b[0]


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

def get_active_clients_count():
    return threading.activeCount() - 2

def handle_client(conn, addr):
    print(f"[CLIENT CONNECTED] {addr} connected.\n")
    connnected = True
    while(connnected):
        try:
            msg_length = conn.recv(HEADER).decode(FORMAT)
        except:
            print(f"[CONNECTION FAILED] connection with {addr} unexpectedly failed..\n")
            connnected = False
            break
        if msg_length:
            msg_length = int(msg_length)  # convert string (result of decode into number)
            msg = conn.recv(msg_length).decode(FORMAT)  # receive len of bytes and decode each one
            data_obj = json.loads(msg)  # load and return dictionary
            dis = data_obj['request']
            if dis == DISCONNECT_MESSAGE:  # if msg is !Disconect just leave connection with server
                dicto = {'response': "OK"}
                json_obj = json.dumps(dicto)
                send(json_obj, conn, addr)
                print(f"[CLIENT DISCONNECT] client of Address {addr} disconnected..\n")
                connnected = False
                break

            data_obj = json.loads(msg)


            print(f"[{addr}] {data_obj}\n")
            if data_obj['request'] == LOGIN:
                login(data_obj, conn, addr)
            elif data_obj['request'] == CREATE_ACCOUNT:
                signup(data_obj, conn, addr)
            elif data_obj['request'] == GET_ITEMS:
                getItems(data_obj, conn, addr)
            elif data_obj['request'] == GET_BALANCE:
                getBalance(data_obj, conn, addr)
            elif data_obj['request'] == DEPOSIT:
                deposit(data_obj, conn, addr)
            elif data_obj['request'] == ADD_ITEM:
                addToCart(data_obj, conn, addr)
            elif data_obj['request'] == GET_CART:
                showCart(data_obj, conn, addr)
            elif data_obj['request'] == PURCHASE:
                purchase(data_obj, conn, addr)

    conn.close()

# print(retrieve_purchases())



def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 2}")


#print("[STARTING] server is starting...")
#start()

# create_database()
# add_book("C HOW TO PROGRAM", 100,200,1)
# add_book("JAVA HOW TO PROGRAM", 120,350,2)
# add_book("Introduction To Java", 200,257,3)
# add_book("Clean Code", 60,5555,5)
# add_user("mahmoud","yasser", "mahmoudyasser@gmail.com", 1234, 1000)
# add_user("ali","khaled", "alikhaled@gmail.com", 12345, 1500)



def Clear_database(tableName):
    conn = sqlite3.connect('books.db')
    c = conn.cursor()
    c.execute("DELETE FROM '{}'".format(tableName))
    conn.commit()
    conn.close()
# Clear_database("books")
# Clear_database("purchases")
# print(retrieve_purchases())
# print(retrieve_users())

# conn = sqlite3.connect('books.db')
# c = conn.cursor()
#
# c.execute("""   DELETE FROM  purchases
#         """)

# c.execute("""   CREATE TABLE purchases(
#                 email text,
#                 item_name text,
#                 quantity integer,
#                 status integer
#             )
#         """)
#
# conn.commit()
# conn.close()
def showCart(dataobj, conn, addr):
    email = dataobj['email']
    conndb = sqlite3.connect('books.db')
    c = conndb.cursor()
    c.execute("SELECT  item_name , quantity FROM  purchases WHERE email = '{}' and (status = '{}' or (status='{}' and quantity >'{}'))".format(email.lower(),0,1,0))
    items=c.fetchall()
    dicto = {'items': items}
    json_obj = json.dumps(dicto)
    send(json_obj, conn, addr)


# print(retrieve_purchases())




server_thread = threading.Thread(target=start)
server_thread.start()

# main

app = QApplication(sys.argv)
welcome = ServerGui()
widget = QtWidgets.QStackedWidget()
widget.addWidget(welcome)
widget.setFixedHeight(800)
widget.setFixedWidth(1200)
widget.show()
try:
    sys.exit(app.exec_())
except:
    os.abort()
    print("Exiting")



