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
    mysql = connectToMySQL("basic_reg")
    query = "SELECT email FROM users where email = %(em)s"
    data = {
        'em' : request.form["email"]
    }
    result = mysql.query_db(query, data)
    print(result)
    if len(result) > 0:
        is_valid = False
        flash("that email is already in use")
        print("that email is already in use")
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
        print("registration successfull")
    return redirect('/')

@app.route('/login', methods = ['POST'])
def login():
    mysql = connectToMySQL("basic_reg")
    query = "SELECT * FROM users WHERE email = %(em)s;"
    data = { "em" : request.form["log_email"] }
    result = mysql.query_db(query, data)
    print(result)
    print(request.form)
    if result and bcrypt.check_password_hash(result[0]['password'], request.form['log_pass']):
        session['userid'] = result[0]['id']
        return redirect('/success')
    flash("You could not be logged in")
    return redirect("/")

@app.route('/success')
def success():
    db = connectToMySQL("basic_reg")
    user_profiles = db.query_db(f'SELECT * FROM users where id = {session["userid"]}')
    db = connectToMySQL("basic_reg")
    user_tweets = db.query_db('SELECT * from TWEETS join users on users_id = users.id')
    db = connectToMySQL("basic_reg")
    user_likes = db.query_db('SELECT * from LIKES join tweets on tweets.id = likes.tweets_id')
    return render_template("success.html", user = user_profiles[0], tweets = user_tweets, likes = user_likes)

@app.route('/tweets/create', methods = ["POST"])
def create_tweet():
    db = connectToMySQL("basic_reg")
    query = "INSERT INTO tweets (content, created_at, users_id) VALUES (%(ct)s, NOW(),%(uid)s);"
    data = {
        "ct" : request.form["make_tweet"],
        "uid" : session['userid']
    }
    result = db.query_db(query, data)
    print(result)
    return redirect("/success")

@app.route('/tweets/<tweets_id>/add_like')
def like(tweets_id):
    db = connectToMySQL("basic_reg")
    query = "INSERT INTO likes (users_id, tweets_id, liked_at) VALUES (%(uid)s, %(tid)s, NOW());"
    data = {
        'uid' : session['userid'],
        "tid" : tweets_id
    }
    print(data)
    result = db.query_db(query, data)
    print(result)
    return redirect("/success")

@app.route('/tweets/<tweets_id>/delete')
def delete(tweets_id):
    db = connectToMySQL("basic_reg")
    query = f'select tweets.users_id from tweets where tweets.users_id = {session["userid"]} and tweets.id = %(tid)s'
    data = {
        "tid" : tweets_id
    }
    result = db.query_db(query, data)
    print(result)
    if result and session["userid"] == result[0]["users_id"]:
        db = connectToMySQL("basic_reg")
        query = "delete from likes where likes.tweets_id = %(tid)s"
        db.query_db(query, data)
        db = connectToMySQL("basic_reg")
        query = "delete from tweets where tweets.id = %(tid)s"
        db.query_db(query, data)
        return redirect("/success")
    return redirect("/success")

@app.route('/tweets/<tweets_id>/edit')
def edit(tweets_id):
    print(tweets_id)
    db = connectToMySQL("basic_reg")
    query = f'SELECT * from TWEETS where tweets.id = %(tid)s'
    data = {
        "tid" : tweets_id
    }
    user_tweets = db.query_db(query, data)
    return render_template("edit.html", tweet = user_tweets[0])

@app.route('/tweets/<tweets_id>/update', methods = ["POST"])
def update(tweets_id):
    db = connectToMySQL("basic_reg")
    query = 'update tweets set content = %(ed)s where id = %(tid)s'
    data = {
        "ed" : request.form["edit_tweet"],
        "tid" : tweets_id
    }
    result = db.query_db(query, data)
    print(result)
    return redirect("/success")

if __name__ == "__main__":
    app.run(debug=True)