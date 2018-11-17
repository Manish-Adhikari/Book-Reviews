from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import csv

engine = create_engine("postgres://tbhpfvawuvwbop:5eec2e3c8ceb5f4ba9483fbf1ef94577a63c3e54e812afb6ed651a3d7b647345@ec2-54-204-46-60.compute-1.amazonaws.com:5432/d18j3m18dv9b70")

db = scoped_session(sessionmaker(bind=engine))

f = open('books.csv')
reader = csv.reader(f)

for isbn, ttl, aut, yr in reader:
    db.execute("INSERT INTO books(isbn,title,author,year) VALUES(:isbn,:title,:author,:year)",{"isbn":isbn,"title":ttl,"author":aut,"year":yr})
    print(f"{ttl} added")
db.commit()


