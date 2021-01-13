#Shopify image repo
from flask import Flask, render_template, redirect, url_for, request
import sqlite3 as sql

logged_in = False
user=()
app = Flask(__name__)

def get_cursor():
    conn=sql.connect("Database.db")
    cur=conn.cursor
    return (cur,conn)

def initialize():
    cur,conn=get_cursor()

    #populate the database with basic info

    #users
    """
    contains user login info to conditionally render different versions of the webpage 
    for different users.
    """
    cur.execute("DROP TABLE IF EXISTS users")
    cur.execute("CREATE TABLE users (ID TEXT, password TEXT, vendor BOOLEAN)")
    cur.execute("INSERT INTO users (ID, password, vendor) VALUES\
        ('defaultUser','1234',false)\
        ('defaultVendor','4321',true)")

    #images
    cur.execute("DROP TABLE IF EXISTS images")
    cur.execute("CREATE TABLE images (name TEXT, path TEXT, price FLOAT, stock INTEGER, vendorID TEXT)")
    cur.execute("INSERT INTO images (name, path, price, stock, vedorID) VALUES\
        ('Microphone','images/mic.jpg'),500.00,5, defaultVendor)\
        ('Chair','images/chair.jpg'),40.00,20, defaultVendor)\
        ('5x5 cube','images/5x5 cube.jpg',20.00,10, defaultVendor)")
    
    #transactions
    cur.execute("DROP TABLE IF EXISTS transactions")
    cur.execute("CREATE TABLE transactions (name TEXT, amount FLOAT, userID TEXT)")

    conn.commit()
    print("Database created")

@app.route("/") #homepage, default market, same for both users
def home_page():
    if not logged_in:
        return render_template("info.html",info="please log-in first")

# Route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    global logged_in,user
    (cur, conn) = get_cursor()
    error = None
    if request.method == 'POST':
        cur.execute("SELECT * FROM users WHERE (ID=%s AND password=%s)"%(request.form['username'],request.form['password']))
        result = cur.fetchone()
        
        if not result:
            return render_template("info.html",info="incorrect login")
        (user,_,vendor)=result

        logged_in=True

        if vendor:
            return render_template("vendor.html")
        if not vendor:
            return render_template("index.html")
        else:
            return render_template("info.html",info="something went wrong")
    return render_template('login.html', error=error) 

@app.route("/vendor") # page specifically for a vendor to see what theyre selling
def vendor_page():
    global user
    (cur, conn) = get_cursor()
    #get all the products offered
    cur.execute("SELECT * FROM images WHERE vendorID=%s",user)
    products = cur.fetchall() 
    offered_products = []

    #create json for table elements
    for product in products:
        offered_products.append({
            "id":    product[0],
            "name":  product[1],
            "src":   "/static/%s" % (product[2]),
            "price": "$%.2f" % (product[3]),
            "stock": "%d left" % (product[4]),
        })

    #get amount of money earned
    cur.execute("SELECT SUM(amount) FROM transactions WHERE vendorID=%s",user)
    result = cur.fetchone()[0]
    earnings = result if result else 0
    return render_template("vendor.html", products=offered_products, earnings=earnings)

@app.route("/buy/<product_id>")
def buy(name):
    if not name:
        return render_template("info.html", info="Invalid product")

    (cur, conn) = get_cursor()

    cur.execute("SELECT * FROM products WHERE rowid = ?", (name,))
    result = cur.fetchone()

    if not result:
        return render_template("info.html", info="Invalid product ID!")
    (name,_,price,stock,vendorID) = result

    if stock <= 0:
        return render_template("info.html", info="Insufficient stock!")

    cur.execute("INSERT INTO transactions (name,amount,userID) VALUES " + \
        "(?, ?, ?)", (name, price, vendorID))

    cur.execute("UPDATE images SET stock = stock - 1 WHERE name = ?", (name,))
    conn.commit()
    return render_template("info.html", info="Purchase successful!")