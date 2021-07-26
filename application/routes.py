'''
Where all the routes to pages are declared and configured
'''

import os
import secrets
from re import sub
from urllib.parse import urlencode, quote_plus
from PIL import Image
from flask import render_template, redirect, url_for, flash, request
from application import app, db, bcrypt
from application.forms import *
from application.database import *
from flask_login import login_user, current_user, logout_user, login_required
from random import randint


def extract(char, string):
    '''
    Removes specifiers that are not important to names or titles
    if char is "a" it denominates authors, if "t" the title of a book
    '''
    if char == "a":
        return string.replace("Authors(", "").replace(")", "")
    if char == "t":
        return string.split("(")[0].strip()
    else:
        raise "Something went wrong"


# The main page
@app.route("/")
@app.route("/home")
def home():
    '''The home page'''
    # Pick a random year from an arbitrary interval
    year = 2015 #randint(2012, 2017)
    # Select the first 8 books for a certain year and order them by the rating from high to low
    twenty_books = Books.query.filter_by(year=year).order_by(Books.rating.desc()).limit(8).all()
    return render_template("home.html", books=twenty_books, extract=extract, year=year)


@app.route("/book/<int:book_id>")
def book(book_id):
    '''A page where books can be viewd by getting the book's id from URL'''
    book = Books.query.get_or_404(book_id)
    fav = None
    status = None
    if current_user.is_authenticated:
        # Get the current status of the book from the table manually
        status = db.engine.execute(f'''SELECT status FROM user_book_status
                                    WHERE user_id = {current_user.id} AND book_id = {book_id};''').first()
        if book.fav_adders.filter_by(id=current_user.id).first():
            fav = True
    # Query the author of the book
    author = book.written_by.first()
    # Query other books of the same author except the current book
    related_books = author.books_written.filter(Books.id != book.id).limit(4).all()
    # Set the parameter of an automatic duckduckgo search result
    # Rmove all the non alphanumeric characters except white space
    q = { "q" : "!" + sub("[^a-zA-Z0-9_\s]+", "",rf"ducky {book.title} by {author.name} ") + "site:books.google.com" }
    # The url of the book on google books through duckduckgo search
    more_url = "https://duckduckgo.com/?" + urlencode(q) + "&kl=us-en"
    return render_template("book.html", book=book, related_books=related_books,
                           status=status, more_url=more_url, fav=fav, extract=extract, title=book.title)


@app.route("/book/<int:book_id>/update")
@login_required
def update(book_id):
    '''For updating users libraries. Updating status, adding to favourite, etc.'''
    book = Books.query.get_or_404(book_id)
    # c for completed, h for have read, p for planned (will read), f for favourites
    lib = request.args.get("lib")
    if lib in ("r", "c", "p"):
        # If it has a status, update it, else create it
        status_query = current_user.books_status.filter_by(id=book.id).first()
        if status_query:
            db.engine.execute(f'''UPDATE user_book_status SET status = "{lib}"
                                WHERE user_id = {current_user.id} AND book_id = {book.id};''')
        else:
            current_user.books_status.append(book)
            db.session.commit()
            db.engine.execute(f'''UPDATE user_book_status SET status = "{lib}"
                                  WHERE user_id = {current_user.id} AND book_id = {book.id};''')
        db.session.commit()
        flash("Book status has been updated successfully!", "success")
    elif lib == "f":
        # Switches from adding to removing whenever called
        fav_query = book.fav_adders.filter_by(id=current_user.id).first()
        if fav_query:
            db.engine.execute(f'''DELETE FROM users_favs
                            WHERE user_id = {current_user.id} AND book_id = {book.id};''')
            flash("Book has been removed from your favourites.", "secondary")
        else:
            current_user.fav_books.append(book)
            flash("Book has been added to your favourites!", "success")
        db.session.commit()
    else:
        flash("Non-existent argument", "danger")
    return redirect(url_for("book", book_id=book_id))


@app.route("/book/<int:book_id>/rem_lib")
@login_required
def rem_lib(book_id):
    '''To remove a book from the status library'''
    book = Books.query.get_or_404(book_id)
    db.engine.execute(f'''DELETE FROM user_book_status
                                WHERE user_id = {current_user.id} AND book_id = {book.id};''')
    return redirect(url_for("book", book_id=book.id))


@app.route("/search")
def search():
    '''Searches the titles, years, names in the database'''
    q = request.args.get("q", "")
    page = request.args.get("page", 1, type=int)
    books = None
    if q:
        books = Books.query.msearch(q, fields=["title", "year"]).paginate(per_page=12, page=page)
        if not books.items:
            authors = Authors.query.msearch(q, fields=["name"]).all()
            authors = [author.name for author in authors]
            # Query the books from the authors in the above variable and paginate
            books = Books.query.filter(Books.written_by.any(Authors.name.in_(authors))).paginate(per_page=12, page=page)
    return render_template("search.html", title=q, q=q, books=books, extract=extract)


@app.route("/discover")
def discover():
    '''Where all the books can be displayed'''
    page = request.args.get("page", 1, type=int)
    sort = request.args.get("sort", "most_popular", type=str)
    # Querying highest rated
    if sort == "highest_rated":
        books = Books.query.order_by(Books.rating.desc()).paginate(per_page=12, page=page)

    # Querying most popular books
    elif sort == "most_popular":
        books = Books.query.order_by(Books.num_ratings.desc()).paginate(per_page=12, page=page)

    # Querying alphabetically
    elif sort == "alphabetical":
        books = Books.query.order_by(Books.title).paginate(per_page=12, page=page)

    # Querying by the latest in the database
    elif sort == "latest":
        books = Books.query.filter(Books.year != "").order_by(Books.year.desc()).paginate(per_page=12, page=page)
    else:
        return redirect(url_for("discover"))
    return render_template("discover.html", extract=extract, sort=sort, books=books, title="Discover")


@app.route("/mylibrary", defaults={"library": "favorites"})
@app.route("/mylibrary/<string:library>")
@login_required
def mylibrary(library):
    '''Where users can see their saved books'''
    page = request.args.get("page", 1, type=int)
    books = None
    # Querying favourite books
    if library == "favorites" or not library:
        books = current_user.fav_books.paginate(per_page=12, page=page)

    # Querying a certain status' books
    elif library in ("completed", "planned", "reading"):
        book_ids_query = db.engine.execute(f'''SELECT book_id FROM user_book_status
                                            WHERE user_id = {current_user.id} AND status = "{library[0]}";''').all()
        book_ids = [book_id[0] for book_id in book_ids_query]
        books = current_user.books_status.filter(Books.id.in_(book_ids)).paginate(per_page=12, page=page)
    else:
        return redirect(url_for("mylibrary"))
    return render_template("mylibrary.html", extract=extract, library=library, books=books, title="My Library")


@app.route("/register", methods=["GET", "POST"])
def register():
    '''The registeration page'''
    # Check if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    # Get the form from the imported forms
    form = RegistrationForm()
    if form.validate_on_submit():
        # Make a hashed password and decode it to a string
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf8")
        # Add the info to the users table
        user = Users(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        # Display a success message
        flash("Your account has been created successfully!", "success")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    '''The login page'''
    # Check if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    # Get the form from the imported forms
    form = LoginForm()
    if form.validate_on_submit():
        # Store the user in the variable
        user = Users.query.filter_by(email=form.email.data).first()
        # if the user exists and the password is correct
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            # login the user using the flask_login library
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("home"))
        else:
            # An alert if unsuccessful
            flash("Login unsuccessful. Please check your credentials.", "danger")
    return render_template("login.html", title="Login", form=form)


def save_image(form_image):
    '''
    Creates a random name for the image and compresses its size
    and saves it in the specified path
    '''
    random_hex = secrets.token_hex(8)
    name_ext = form_image.filename.split(".")[1]
    filename = random_hex + "." + name_ext
    image_path = os.path.join(app.root_path, "static/profile_pics", filename)

    # Save a small size of the image
    output_size = (125, 125)
    i = Image.open(form_image)
    i.thumbnail(output_size)
    i.save(image_path)
    return filename


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    '''Where a user can edit his/her picture and account info'''
    # Changing the username and email process
    form = UpdateAccountForm()
    if form.validate_on_submit():
        # Easily change the username and email on the database
        if current_user.username != form.username.data or current_user.email != form.email.data:
            current_user.username = form.username.data
            current_user.email = form.email.data
            db.session.commit()
            flash("Your Username/Email has been updated!", "success")
            return redirect(url_for("settings"))
    # To fill the fields with account info
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email

    # Changing the image process
    image_form = UpdateImageForm()
    if image_form.validate_on_submit():
        if image_form.image.data:
            # If the previous image isn't the default delete it
            if current_user.image != "user.jpg":
                os.remove(os.path.join(app.root_path, "static/profile_pics", current_user.image))
            filename = save_image(image_form.image.data)
            current_user.image = filename
            db.session.commit()
            flash("Your profile picture has been updated!", "success")
        return redirect(url_for("settings"))

    return render_template("settings.html", form=form, image_form=image_form, title="Settings")


@app.route("/rempic")
@login_required
def rempic():
    '''To remove the profile pic of a user'''
    current_user.image = "user.jpg"
    db.session.commit()
    return redirect(url_for("settings"))


@app.route("/logout")
@login_required
def logout():
    '''The logout process'''
    logout_user()
    return redirect(url_for("home"))
