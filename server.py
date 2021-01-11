#Shopify image repo
from flask import Flask, render_template, redirect, url_for, request
import sqlite3 as sql

logged_in = False
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

@app.route("/") #homepage
def home_page():
    if not logged_in:
        return render_template("info.html",info="please log-in first")

# Route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    (cur, conn) = get_cursor()
    error = None
    if request.method == 'POST':
        cur.execute("SELECT * FROM users WHERE (ID=%s AND password=%s)"%(request.form['username'],request.form['password']))
        result = cur.fetchhone()
        
        if not result:
            return render_template("info.html",info="incorrect login")
        (_,_,vendor)=result

        if vendor:
            return render_template("vendor.html")
        if not vendor:
            return render_template("index.html")
        else:
            return render_template("info.html",info="something went wrong")
    return render_template('login.html', error=error) 