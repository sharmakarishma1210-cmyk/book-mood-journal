from flask import Flask , render_template , request , redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///books.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Book(db.Model):
	id = db.Column(db.Integer , primary_key = True)
	title = db.Column(db.String(200) , nullable = False)
	author = db.Column(db.String(200),nullable = False)



@app.route("/")
def home():
	books = Book.query.all()
	return render_template("index.html" , books = books)

@app.route("/add", methods = ["POST"])
def add_book():
	title = request.form["title"]
	author = request.form["author"]

	new_book = Book(title = title , author = author)

	db.session.add(new_book)
	db.session.commit()

	return redirect("/")

with app.app_context():
	db.create_all()

if __name__ == "__main__":
	app.run(debug = True)