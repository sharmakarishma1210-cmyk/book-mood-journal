from datetime import datetime
from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user
)
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

app = Flask(__name__)
app.secret_key = "winneralways12"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///books.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# =========================
# DATABASE MODELS
# =========================

class User(UserMixin, db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(200),
        nullable=False
    )


class Book(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    author = db.Column(
        db.String(200),
        nullable=False
    )

    mood = db.Column(
        db.String(200),
        nullable=False
    )

    rating = db.Column(
        db.Float,
        nullable=False
    )

    favorite = db.Column(
        db.Boolean,
        default=False
    )

    quote = db.Column(db.Text)

    cover_url = db.Column(
        db.String(500)
    )

    created_at = db.Column(
        db.DateTime,
        default = datetime.utcnow
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )


# =========================
# LOGIN MANAGER
# =========================

@login_manager.user_loader
def load_user(user_id):

    return db.session.get(
        User,
        int(user_id)
    )


# =========================
# REGISTER
# =========================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        print("REGISTER ROUTE HIT")

        username = request.form[
            "username"
        ].strip().lower()

        password = request.form[
            "password"
        ].strip()

        existing_user = User.query.filter_by(
            username=username
        ).first()

        if existing_user:

            flash("Username already exists.")

            return redirect("/register")

        hashed_password = generate_password_hash(
            password
        )

        user = User(
            username=username,
            password=hashed_password
        )

        db.session.add(user)

        db.session.commit()

        print("USER SAVED")

        flash("Account created successfully 🎉")

        return redirect("/login")

    return render_template("register.html")


# =========================
# LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form[
            "username"
        ].strip().lower()

        password = request.form[
            "password"
        ].strip()

        user = User.query.filter_by(
            username=username
        ).first()

        print(user)

        if user and check_password_hash(
            user.password,
            password
        ):

            print("LOGIN SUCCESS")

            login_user(user)

            flash("Logged in successfully 🎉")

            return redirect("/")

        flash("Invalid username or password ❌")

        print("LOGIN FAILED!")

    return render_template("login.html")


# =========================
# LOGOUT
# =========================

@app.route("/logout")
@login_required
def logout():

    logout_user()

    flash("Logged out successfully 👋")

    return redirect("/login")


# =========================
# HOME PAGE
# =========================

@app.route("/")
@login_required
def home():

    search = request.args.get(
        "search",
        ""
    ).strip()

    mood_filter = request.args.get(
        "mood",
        "all"
    ).strip().lower()

    books_query = Book.query.filter_by(
        user_id=current_user.id
    )

    # =========================
    # SEARCH
    # =========================

    if search:

        clean_search = search.replace(
            ".",
            ""
        ).lower()

        books_query = books_query.filter(

            func.replace(
                func.lower(Book.title),
                ".",
                ""
            ).contains(clean_search)

            |

            func.replace(
                func.lower(Book.author),
                ".",
                ""
            ).contains(clean_search)
        )

    # =========================
    # MOOD FILTER
    # =========================

    if mood_filter != "all":

        books_query = books_query.filter(
            Book.mood.ilike(
                f"%{mood_filter}%"
            )
        )

    books = books_query.order_by(
        Book.favorite.desc(),
        Book.id.desc()
    ).all()

    # =========================
    # STATS
    # =========================

    total_books = len(books)

    favorite_books = len(
        [book for book in books if book.favorite]
    )

    average_rating = round(

        sum(book.rating for book in books)
        / total_books,

        1

    ) if books else 0

    # =========================
    # TOP MOOD
    # =========================

    mood_data = {}

    for book in books:

        moods = book.mood.lower().split(",")

        for mood in moods:

            mood = mood.strip()

            if mood:

                mood_data[mood] = (
                    mood_data.get(mood, 0) + 1
                )

    top_mood = (

        max(
            mood_data,
            key=mood_data.get
        )

        if mood_data else "None"

    )

    all_moods = set()
    for book in Book.query.filter_by(
        user_id = current_user.id
    ).all():
        moods = book.mood.split(",")
        for mood in moods:
            cleaned_mood = mood.strip().lower()
            if cleaned_mood:
                all_moods.add(cleaned_mood)
    all_moods = sorted(all_moods)


    return render_template(
        "index.html",
        books=books,
        total_books=total_books,
        favorite_books=favorite_books,
        average_rating=average_rating,
        top_mood=top_mood,
        all_moods =all_moods
    )


# =========================
# ANALYTICS PAGE
# =========================

@app.route("/analytics")
@login_required
def analytics():

    books = Book.query.filter_by(
        user_id=current_user.id
    ).all()

    # =========================
    # MOOD DATA
    # =========================

    mood_data = {}

    for book in books:

        moods = book.mood.lower().split(",")

        for mood in moods:

            mood = mood.strip()

            if mood:

                mood_data[mood] = (
                    mood_data.get(mood, 0) + 1
                )

    # =========================
    # RATING DATA
    # =========================

    rating_data = {
        "1 ⭐": 0,
        "2 ⭐": 0,
        "3 ⭐": 0,
        "4 ⭐": 0,
        "5 ⭐": 0,
    }

    for book in books:

        rounded_rating = round(book.rating)

        rating_key = f"{rounded_rating} ⭐"

        if rating_key in rating_data:

            rating_data[rating_key] += 1

    # =========================
    # FAVORITES
    # =========================

    favorite_count = len(
        [book for book in books if book.favorite]
    )

    # =========================
    # AVERAGE RATING
    # =========================

    average_rating = round(

        sum(book.rating for book in books)
        / len(books),

        1

    ) if books else 0

    # =========================
    # HIGHEST RATED
    # =========================

    highest_rated = max(

        books,

        key=lambda book: book.rating

    ) if books else None

    # =========================
    # TOP AUTHOR
    # =========================

    author_data = {}

    for book in books:

        author_data[book.author] = (
            author_data.get(book.author, 0) + 1
        )

    top_author = (

        max(
            author_data,
            key=author_data.get
        )

        if author_data else "None"

    )

    # =========================
    # FAVORITE PERCENTAGE
    # =========================

    favorite_percentage = round(

        (favorite_count / len(books)) * 100,

        1

    ) if books else 0

    return render_template(
        "analytics.html",

        mood_labels=list(mood_data.keys()),
        mood_values=list(mood_data.values()),

        rating_labels=list(rating_data.keys()),
        rating_values=list(rating_data.values()),

        favorite_count=favorite_count,

        average_rating=average_rating,

        highest_rated=highest_rated,

        top_author=top_author,

        favorite_percentage=favorite_percentage
    )


# =========================
# ADD BOOK
# =========================

@app.route("/add", methods=["POST"])
@login_required
def add_book():

    title = request.form[
        "title"
    ].title().strip()

    author = request.form[
        "author"
    ].title().strip()

    mood = request.form[
        "mood"
    ].lower().strip()

    rating = float(
        request.form["rating"]
    )

    if rating < 1 or rating > 5:

        flash("Rating must be between 1 and 5")

        return redirect("/")

    quote = request.form[
        "quote"
    ].strip()

    cover_url = request.form["cover_url"]
    new_book = Book(
        title=title,
        author=author,
        mood=mood,
        rating=rating,
        favorite=False,
        quote=quote,
        cover_url = cover_url,
        user_id=current_user.id
    )

    db.session.add(new_book)

    db.session.commit()

    flash("Book added successfully 📚")

    return redirect("/")


# =========================
# DELETE BOOK
# =========================

@app.route("/delete/<int:id>")
@login_required
def delete_book(id):

    book = Book.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(book)

    db.session.commit()

    flash("Book deleted")

    return redirect("/")


# =========================
# EDIT BOOK
# =========================

@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_book(id):

    book = Book.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    if request.method == "POST":

        rating = float(
            request.form["rating"]
        )

        if rating < 1 or rating > 5:

            flash("Rating must be between 1 and 5")

            return redirect(f"/edit/{id}")

        book.title = request.form[
            "title"
        ].title().strip()

        book.author = request.form[
            "author"
        ].title().strip()

        book.mood = request.form[
            "mood"
        ].lower().strip()

        book.rating = rating

        book.quote = request.form[
            "quote"
        ].strip()

        db.session.commit()

        flash("Book updated successfully ✏️")

        return redirect("/")

    return render_template(
        "edit.html",
        book=book
    )


# =========================
# FAVORITE BOOK
# =========================

@app.route("/favorite/<int:id>")
@login_required
def favorite_book(id):

    book = Book.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    book.favorite = not book.favorite

    db.session.commit()

    return redirect("/")


# =========================
# CREATE DATABASE
# =========================

with app.app_context():

    db.create_all()


# =========================
# RUN APP
# =========================

if __name__ == "__main__":
    app.run(debug=True)

