from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///books.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)

    author = db.Column(db.String(200), nullable=False)

    mood = db.Column(db.String(100), nullable=False)

    rating = db.Column(db.Float, nullable=False)

    favorite = db.Column(db.Boolean , default = False)

    quote = db.Column(db.Text)


@app.route("/")
def home():
    search = request.args.get("search", "").strip()

    mood = request.args.get("mood", "all").strip().lower()

    books = Book.query

    if search:
        books = books.filter(
            Book.title.ilike(f"%{search}%") |
            Book.author.ilike(f"%{search}%")
        )

    if mood != "all":
        books = books.filter(
            Book.mood.ilike(f"%{mood}%")
        )

    books = books.order_by(Book.favorite.desc()).all()
    total_books = len(books)
    favorite_books = len(
        [book for book in books if book.favorite]
    )
    if books:
        average_rating = round(
            sum(book.rating for book in books)/total_books,1
        )
    else:
        average_rating = 0


    mood_count = {}
    for book in books:
        moods = book.mood.lower().split(",")
        for mood in moods:
            mood = mood.strip()
            mood_count[mood] = mood_count.get(mood , 0)+1

    if mood_count:
        top_mood = max(
            mood_count,key=mood_count.get
        )
    else:
        top_mood = "None"


    return render_template(
        "index.html",
        books=books,
        total_books = total_books,
        favorite_books = favorite_books,
        average_rating = average_rating,
        top_mood = top_mood
    )


@app.route("/add", methods=["POST"])
def add_book():
    title = request.form["title"].title().strip()

    author = request.form["author"].title().strip()

    mood = request.form["mood"].lower().strip()

    rating = float(request.form["rating"])

    quote = request.form["quote"]

    new_book = Book(
        title=title,
        author=author,
        mood=mood,
        rating=rating,
        favorite = False,
        quote = quote)
    

    db.session.add(new_book)

    db.session.commit()

    return redirect("/")


@app.route("/delete/<int:id>")
def delete_book(id):
    book = Book.query.get_or_404(id)

    db.session.delete(book)

    db.session.commit()

    return redirect("/")


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_book(id):
    book = Book.query.get_or_404(id)

    if request.method == "POST":
        book.title = request.form["title"].title().strip()

        book.author = request.form["author"].title().strip()

        book.mood = request.form["mood"].lower().strip()

        book.rating = float(request.form["rating"])

        db.session.commit()

        return redirect("/")

    return render_template(
        "edit.html",
        book=book
    )
@app.route("/favorite/<int:id>")
def favorite_book(id):
    book = Book.query.get_or_404(id)
    book.favorite = not book.favorite
    db.session.commit()
    return redirect("/")

with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)