from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from datetime import datetime
from werkzeug.security import check_password_hash,generate_password_hash

app = Flask(__name__)

# Database Connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    auth_plugin="mysql_native_password")
cursor = conn.cursor()
#
cursor.execute("create database if not exists finance_db")
cursor.execute("use finance_db")
# create a table for all new user
cursor.execute("create table if not exists transactions (id int NOT NULL AUTO_INCREMENT Primary key,user varchar(254),date date,type varchar(254),category varchar(254),amount float,note varchar(254))")
# creating a table to store users password & usernames
cursor.execute("create table if not exists login (username varchar(255) primary key,password varchar(255))")
#To store user name 
user=""
# Home Page
@app.route("/")
def home():
    return render_template("logopage.html")
#login page
@app.route("/login",methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username= request.form["username"]
        password= request.form["password"]
        cursor.execute("select * from login where username='{}'".format(username))
        q=cursor.fetchone()
        if q and check_password_hash(q[1],password):
            global user
            user=username
            return redirect(url_for("Menu"))
        else:
            invaild="invaild passoword or username"
            return render_template("login.html",invaild=invaild)
    return render_template("login.html")
#sign up page 
@app.route("/signup",methods=['GET','POST'])
def signup():
    if request.method == "POST":
        username= request.form["username"]
        password= request.form["password"]
        cursor.execute("select * from login")
        s=cursor.fetchall()
        for i in s:
            if i[0]==username:
                if i[1]==password:
                    already="This account already exists"
                    return render_template("create.html",already=already)
                old="This username is already taken"
                return render_template("create.html",old=old)
        cursor.execute("insert into login values('{}','{}')".format(username,generate_password_hash(password)))
        conn.commit()
        return redirect("/login")
    return render_template("create.html")
#Menu
@app.route("/index")
def Menu():
    global user
    return render_template("index.html",namee=user)

#Add Transaction
@app.route("/add", methods=["GET", "POST"])
def add_transaction():
    # cursor.execute("select * from category")
    # q=cursor.fetchall()
    if request.method == "POST":
        t_type = request.form["type"]
        category = request.form["category"]
        amount = request.form["amount"]
        note = request.form["note"]
        date = datetime.now().strftime("%Y-%m-%d")

        global user
        sql = "INSERT INTO transactions (user,date, type, category, amount, note) VALUES ('{}','{}','{}','{}',{},'{}')".format(
            user,date, t_type, category, amount, note
        )
        cursor.execute(sql)
        conn.commit()

        return redirect("/view")
    return render_template("add.html")

#View All
@app.route("/view")
def view_all():
    global user
    cursor.execute("SELECT * FROM transactions where user='{}'ORDER BY date DESC".format(user))
    rows = cursor.fetchall()
    return render_template("view.html", rows=rows)

#Summary
@app.route("/summary")
def summary():
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='Income'and user='{}'".format(user))
    income = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='Expense' and user='{}'".format(user))
    expense = cursor.fetchone()[0] or 0

    balance = income - expense
    return render_template("summary.html", income=income, expense=expense, balance=balance)

#Delete
@app.route("/delete/<int:id>")
def delete(id):
    cursor.execute("DELETE FROM transactions WHERE id={}".format(id))
    conn.commit()
    return redirect("/view")

#clear all
@app.route("/clearall")
def clearall():
    global user
    cursor.execute('select id from transactions')
    r=cursor.fetchall()
    for i in r:
        cursor.execute("delete from transactions where id={} and user='{}'".format(i[0],user))
        conn.commit()
    return redirect("/view")


if __name__ == "__main__":
    app.run(debug=True)
