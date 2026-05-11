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
	mood = db.Column(db.String(100) , nullable = False)
	rating = db.Column(db.Float , nullable = False)



@app.route("/")
def home():
	books = Book.query.all()
	return render_template("index.html" , books = books)

@app.route("/add", methods = ["POST"])
def add_book():
	title = request.form["title"].title()
	author = request.form["author"].title()
	mood = request.form["mood"].title()
	rating = request.form["rating"].title()

	new_book = Book(title = title , 
				 author = author , 
				 mood = mood , 
				 rating = float(rating))
 
	db.session.add(new_book)
	db.session.commit()

	return redirect("/")

@app.route("/delete/<int:id>")
def delete_book(id):
	book = Book.query.get_or_404(id)
	db.session.delete(book)
	db.session.commit()
	return redirect("/")

@app.route("/edit/<int:id>",methods=["GET" , "POST"])
def edit_book(id):
	book = Book.query.get_or_404(id)
	if request.method == "POST":
		book.title = request.form["title"]
		book.author = request.form["author"]
		book.mood = request.form["mood"]
		book.rating = float(request.form["rating"])
		db.session.commit()
		return redirect("/")
	return render_template("edit.html",book=book)


with app.app_context():
	db.create_all()

if __name__ == "__main__":
	app.run(debug = True)