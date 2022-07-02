
import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QWidget
import socket
import json


HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "192.168.1.2"
ADDR = (SERVER, PORT)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)
LOGIN = "LOGIN"
CREATE_ACCOUNT = "CREATE_ACCOUNT"
DEPOSIT = "DEPOSIT"
GET_BALANCE = "GET_BALANCE"
GET_ITEMS = "GET_ITEMS"
GET_PROFILE = "GET_PROFILE"
ADD_ITEM = "ADD_ITEM"
GET_CART = "GET_CART"
email = ""
PURCHASE = "PURCHASE"



def send(msg):
    message = msg.encode(FORMAT) # byte format encoded msg #  '123' => bytes b'x/ab24' => ['4'.encode => 15bytes]
    msg_length = len(message) # bytes(encoded msg) format length 2
    send_length = str(msg_length).encode(FORMAT) # encoded length of bytes msg as string
    send_length += b' ' * (HEADER - len(send_length)) # for padding till 64 of header
    client.send(send_length)  # to send header
    client.send(message) # massage
    # client receive response from server
    response_length = client.recv(HEADER).decode(FORMAT)  # '4'
    if response_length:
        response_length = int(float(response_length))  # 4
        response_msg = client.recv(response_length)
        response_msg_json = response_msg.decode(FORMAT)  # json
        response_msg_json = json.loads(response_msg_json) # json -> dicto
        # print(f"[SERVER RESPONSE] {response_msg_json}")  # some number of bytes

    result = json.loads(response_msg.decode('utf-8'))
    return result



class WelcomeScreen(QDialog):
    def __init__(self):
        super(WelcomeScreen, self).__init__()
        loadUi("welcomescreen.ui",self)
        self.login.clicked.connect(self.gotologin)
        self.signup.clicked.connect(self.gotocreate)

    def gotologin(self):
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def gotocreate(self):
        create = CreateAccScreen()
        widget.addWidget(create)
        widget.setCurrentIndex(widget.currentIndex() + 1)



class LoginScreen(QDialog):
    def __init__(self):
        super(LoginScreen, self).__init__()
        loadUi("login.ui",self)
        self.passwordField.setEchoMode(QtWidgets.QLineEdit.Password)
        self.login.clicked.connect(self.loginfunction)

    def loginfunction(self):
        global email
        email = self.emailField.text()
        password = self.passwordField.text()

        if len(email)==0 or len(password)==0:
            self.error.setText("Please input all fields.")

        else:

            dicto = {'email': email, 'password': password}
            dicto['request'] = LOGIN
            json_obj = json.dumps(dicto)  # dumps: convert to json
            dic = send(json_obj)
            status = dic['response']
            if status == "OK":
                create = MainWindow()
                widget.addWidget(create)
                widget.setCurrentIndex(widget.currentIndex() + 1)

            elif status == "Password is incorrect":
                self.error.setText("Password is incorrect")
            else:
                self.error.setText("This Account Doesn't exist")




class MainWindow(QDialog):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("MainWindow.ui",self)
        self.tableWidget.setColumnWidth(0,60)
        self.tableWidget.setColumnWidth(1,200)
        self.tableWidget.setColumnWidth(2,100)
        self.tableWidget.setColumnWidth(3, 100)

        self.tableWidget_2.setColumnWidth(0,180)
        self.tableWidget_2.setColumnWidth(1, 110)

        # retrieve_items(self)
        self.deposit_Button.clicked.connect(self.goToDeposit)
        self.check_Balance_Button.clicked.connect(self.goToCheckBalance)
        self.addButton.clicked.connect(self.goToAdd)
        self.ViewCartButton.clicked.connect(self.goToViewCart)
        self.buyButton.clicked.connect(self.goToBuy)
        self.refreshButton.clicked.connect(self.retrieve_item)
        while (self.tableWidget.rowCount() > 0):
            self.tableWidget.removeRow(0)
        dicto2 = {"email": email}
        dicto2['request'] = GET_ITEMS
        json_obj = json.dumps(dicto2)
        query = send(json_obj)
        list = query['items']
        
        names = []
        ids = []
        quantities = []
        price = []
        
        for inner in list:
            names.append(inner[0])
            price.append(inner[1])
            quantities.append(inner[2])
            ids.append(inner[3])
        
        for i in range(len(ids)):
            rowPosition = self.tableWidget.rowCount()
            self.tableWidget.insertRow(rowPosition)
            self.tableWidget.setItem(i, 0, QtWidgets.QTableWidgetItem(str(ids[i])))
            self.tableWidget.setItem(i, 1,QtWidgets.QTableWidgetItem(names[i]))
            self.tableWidget.setItem(i, 2, QtWidgets.QTableWidgetItem(str(price[i])))
            self.tableWidget.setItem(i, 3, QtWidgets.QTableWidgetItem(str(quantities[i])))
            
    def goToDeposit(self):
        amount = self.depositField.text()
        dicto = {'email': email, 'amount': amount}
        dicto['request'] = DEPOSIT
        json_obj = json.dumps(dicto)
        send(json_obj)


    def retrieve_item(self):
        while (self.tableWidget.rowCount() > 0):
            self.tableWidget.removeRow(0)
        dicto2 = {"email": email}
        dicto2['request'] = GET_ITEMS
        
        json_obj = json.dumps(dicto2)
        query = send(json_obj)
        list = query['items']
        
        names = []
        ids = []
        quantities = []
        price = []
        
        for inner in list:
            names.append(inner[0])  
            price.append(inner[1])
            quantities.append(inner[2])
            ids.append(inner[3])
        
        for i in range(len(ids)):
            rowPosition = self.tableWidget.rowCount()
            self.tableWidget.insertRow(rowPosition)
            self.tableWidget.setItem(i, 0, QtWidgets.QTableWidgetItem(str(ids[i])))
            self.tableWidget.setItem(i, 1,QtWidgets.QTableWidgetItem(names[i]))
            self.tableWidget.setItem(i, 2, QtWidgets.QTableWidgetItem(str(price[i])))
            self.tableWidget.setItem(i, 3, QtWidgets.QTableWidgetItem(str(quantities[i])))

    
    def goToViewCart(self):
        while (self.tableWidget_2.rowCount() > 0):
                self.tableWidget_2.removeRow(0)

        dicto = {'email': email}
        dicto['request'] = GET_CART 
        json_obj = json.dumps(dicto)
        rv = send(json_obj)
        result = rv['items']
        name = []
        quantity = []

        for inner in result:
            name.append(inner[0])
            quantity.append(inner[1])
            
        for i in range(len(name)):
            rowPosition = self.tableWidget_2.rowCount()
            self.tableWidget_2.insertRow(rowPosition)

            self.tableWidget_2.setItem(i, 0, QtWidgets.QTableWidgetItem(name[i]))
            self.tableWidget_2.setItem(i, 1,QtWidgets.QTableWidgetItem(str(quantity[i])))

            
    def goToBuy(self):
        quantity = self.QuantityField.text()
        book_name = self.bookNameField.text()
        dicto={'email':email,'name':book_name, 'quantity':int(quantity)}
        dicto['request']=PURCHASE
        json_obj = json.dumps(dicto)
        send(json_obj)
        

    def goToCheckBalance(self):
        dicto = {'email': email}
        dicto['request'] = GET_BALANCE
        json_obj = json.dumps(dicto)
        rv = send(json_obj)
        result = rv['balance']
        self.balanceLabel.setText(str(result))


    def goToAdd(self):
        bookname = self.bookNameField.text()
        quantity=self.QuantityField.text()
        dicto={'email':email ,'name':bookname, 'quantity':int(quantity)}
        dicto['request']=ADD_ITEM
        json_obj = json.dumps(dicto)
        send(json_obj)


class CreateAccScreen(QDialog):
    def __init__(self):
        super(CreateAccScreen, self).__init__()
        loadUi("createacc.ui",self)
        self.passwordField.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirmField.setEchoMode(QtWidgets.QLineEdit.Password)
        self.signup.clicked.connect(self.signupfunction)


    def signupfunction(self):
        email = self.emailField.text()
        password = self.passwordField.text()
        confirmpassword = self.confirmField.text()
        fname = self.fnameField.text()
        lname = self.lnameField.text()

        if len(email)==0 or len(password)==0 or len(confirmpassword)==0:
            self.error.setText("Please fill in all inputs.")

        elif password!=confirmpassword:
            self.error.setText("Passwords do not match.")
        else:
            dicto = {'fname': fname, 'lname': lname, 'email': email, 'password': password, 'cash': 0}
            dicto['request'] = CREATE_ACCOUNT
            json_obj = json.dumps(dicto)  # dumps: convert to json
            dic = send(json_obj)
            status = dic['response']
            if status== "NO":
                self.error.setText("You have an account")
            else:
                self.error.setText("Account created Successfully")
                back = WelcomeScreen()
                widget.addWidget(back)
                widget.setCurrentIndex(widget.currentIndex()+1)




# main
app = QApplication(sys.argv)
welcome = WelcomeScreen()
widget = QtWidgets.QStackedWidget()
widget.addWidget(welcome)
widget.setFixedHeight(800)
widget.setFixedWidth(1200)
widget.show()
try:
    sys.exit(app.exec_())
except:
    dicto = {'request' : "!DISCONNECT"}
    json_obj = json.dumps(dicto)
    send(json_obj)
    print("Exiting")
