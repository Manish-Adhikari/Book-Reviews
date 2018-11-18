from flask import Flask, render_template
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgres://tbhpfvawuvwbop:5eec2e3c8ceb5f4ba9483fbf1ef94577a63c3e54e812afb6ed651a3d7b647345@ec2-54-204-46-60.compute-1.amazonaws.com:5432/d18j3m18dv9b70")

db = scoped_session(sessionmaker(bind=engine))

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("layout.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/signup')
def signup():
    return render_template("signup.html")

if __name__ == '__main__':
    app.run()
