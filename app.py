from flask import Flask, render_template, request, redirect,url_for,session, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_session import Session
import requests

engine = create_engine("postgres://tbhpfvawuvwbop:5eec2e3c8ceb5f4ba9483fbf1ef94577a63c3e54e812afb6ed651a3d7b647345@ec2-54-204-46-60.compute-1.amazonaws.com:5432/d18j3m18dv9b70")

db = scoped_session(sessionmaker(bind=engine))

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route('/')
def index():
    return render_template("layout.html")

@app.route('/login',methods=["POST","GET"])
def login():
    if request.method == 'POST':
        usrname = request.form.get("username")
        paswrd = request.form.get("password")
        #paswrd = generate_password_hash(paswrd)
        user = db.execute("SELECT * FROM users WHERE username=:user AND password=:password",{'user':usrname,'password':paswrd}).fetchone()
        if user is None:
            return render_template("login.html",message="User doesnot exist")
        session['user_id']= user.id
        return redirect(url_for("profile"))
    
    return render_template("login.html")

@app.route('/signup', methods=["POST","GET"])
def signup():
    if request.method == 'POST':
        usrname = request.form.get("reg_username")
        paswrd = request.form.get("reg_password")
        email = request.form.get("reg_email")
        paswrd = generate_password_hash(paswrd)
        try:
            db.execute("INSERT INTO users(username,password,email) VALUES(:username,:password,:email)",{"username":usrname,"password":paswrd,"email":email})
            db.commit()
            return render_template("sucess.html",username=usrname)
        except:
            return render_template("signup.html",username=usrname)
    return render_template("signup.html")

@app.route('/profile',methods=["POST","GET"])
def profile():
    if 'user_id' in session:
        books = db.execute("SELECT * FROM books ORDER BY RANDOM() LIMIT 15").fetchall()
        user= db.execute("SELECT * FROM users WHERE id=:id", {"id":session["user_id"]}).fetchone()
        if request.method == "POST":
            text=request.form.get('text') 
            data=db.execute("SELECT * FROM books WHERE author iLIKE '%"+text+"%' OR title iLIKE '%"+text+"%' OR isbn iLIKE '%"+text+"%'").fetchall()
            return render_template("profile.html",books=data,user=user)
        return render_template("profile.html",books=books,user=user)

    return "<h1>Invalid Entry</h1>";

@app.route('/logout')
def logout():
    if session['user_id'] != None:
        del session['user_id']

    return redirect(url_for("login"))

@app.route('/book/<string:book_title>')
def book(book_title):
    if 'user_id' in session:
        book = db.execute("SELECT * FROM books WHERE title=:title",{"title":book_title}).fetchone()
        user = db.execute("SELECT username FROM users WHERE id=:id",{'id':session['user_id']}).fetchone()
        ratings = requests.get('https://www.goodreads.com/book/review_counts.json',params={'key':'O9dohPYJvkRNH7y4C6YLg','isbns':book.isbn})
        url = "https://www.googleapis.com/books/v1/volumes?q=isbn:"
        new_url = url + str(book.isbn)
        g = requests.get(new_url)
        s= g.json()
        img_url = s["items"][0]["volumeInfo"]["imageLinks"]["thumbnail"]
        description = s["items"][0]["volumeInfo"]["description"]
        rate = (ratings.json()["books"][0]["average_rating"])
        reviews = db.execute("SELECT comment, ratings, username FROM reviews JOIN users ON users.id=user_id WHERE book_title=:book_title LIMIT(4)",{"book_title":book_title})
        return render_template("book.html",user=user,book=book,gratings=rate,description= description, img_url=img_url,reviews=reviews)
    return "<h2> LOoop</h2>";

@app.route('/submit_comment/<string:book_title>', methods=["POST"])
def submit_comment(book_title):
    if 'user_id' in session:
        comm=request.form.get("commtxt")
        rate=request.form.get("starsrate")
        db.execute("INSERT INTO reviews(user_id,comment,book_title,ratings) VALUES (:user_id, :comment, :book_title, :ratings)",
        {"user_id": session['user_id'], "comment": comm, "book_title":book_title, "ratings": rate})
        db.commit()
        return redirect(url_for("book", book_title=book_title))

@app.route('/api/books/<int:book_id>')
def book_api(book_id):
    book = db.execute("SELECT * FROM books WHERE id=:id", {"id":book_id}).fetchone()
    if book is None:
        return jsonify({"Error 404": "This book does not exists"})
    return jsonify({
        "ISBNS": book.isbn,
        "Title": book.title,
        "Author": book.author,
        "Publication Year": book.year,
    })

if __name__ == '__main__':
    app.run()
