from flask import Flask, render_template, request, redirect, session, flash
from my_sql_connection import connectToMySQL
import re
from flask_bcrypt import Bcrypt
app = Flask(__name__)
        
bcrypt = Bcrypt(app)

app.secret_key = "quiet you might piss somebody off"

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

@app.route('/')
def registration():
    session.clear()
    return render_template("registration.html")

@app.route('/register', methods = ["POST"])
def process():
    is_valid = True
    if not EMAIL_REGEX.match(request.form['email']):# test whether a field matches the pattern
        is_valid = False
        flash("Invalid email address!")
    if len(request.form['fname']) < 1 :
        is_valid = False
        flash("please enter a valid first name")
    if len(request.form['lname']) < 1 :
        is_valid = False
        flash("please enter a valid last name")
    if len(request.form['pass']) < 5 :
        is_valid = False
        flash("please enter a valid password")
    if request.form['confirm_pass'] != request.form['pass']:
        is_valid = False
        flash("passwords do not match")
    if is_valid:
        pw_hash = bcrypt.generate_password_hash(request.form['pass']) 
        con_pw_hash = bcrypt.generate_password_hash(request.form['confirm_pass']) 
        print(pw_hash)
        db = connectToMySQL("basic_reg")
        query = "INSERT INTO users (first_name, last_name, password, confirm_password, email) VALUES (%(fn)s, %(ln)s, %(ps)s, %(cp)s, %(em)s);"
        data = {
            'fn' : request.form["fname"],
            'ln' : request.form["lname"],
            'em' : request.form["email"],
            'ps' : pw_hash,
            'cp' : con_pw_hash
        }
        user = db.query_db(query, data)
        flash("registration successfull")
    return redirect('/')

@app.route('/login', methods = ['POST'])
def login():
    mysql = connectToMySQL("basic_reg")
    query = "SELECT * FROM users WHERE email = %(em)s;"
    data = { "em" : request.form["log_email"] }
    result = mysql.query_db(query, data)
    if bcrypt.check_password_hash(result[0]['password'], request.form['log_pass']):
        session['userid'] = result[0]['id']
        return redirect('/success')
    flash("You could not be logged in")
    return redirect("/")

@app.route('/success')
def success():
    db = connectToMySQL("basic_reg")
    user_profiles = db.query_db(f'SELECT * FROM users where id = {session["userid"]}')
    return render_template("success.html", users = user_profiles)

if __name__ == "__main__":
    app.run(debug=True)