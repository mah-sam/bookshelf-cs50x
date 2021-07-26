'''
Stores the structures (models) of the tables and retreives them when imported.
'''

from application import db, login_manager, app, search
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


# Many-to-many link between users and their fav books
users_favs = db.Table('users_favs',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('book_id', db.Integer, db.ForeignKey('books.id'), primary_key=True)
)


# Many-to-many link between users and the books with certain status
user_book_status = db.Table('user_book_status',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('book_id', db.Integer, db.ForeignKey('books.id'), primary_key=True),
    db.Column('status', db.String(1))
)



# A table where user information is stored
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    image = db.Column(db.String(20), nullable=False, default="user.jpg")
    password = db.Column(db.String(60), nullable=False)
    fav_books = db.relationship("Books", secondary=users_favs, lazy="dynamic", backref=db.backref('fav_adders', lazy="dynamic"))
    books_status = db.relationship("Books", secondary=user_book_status, lazy="dynamic", backref=db.backref('status_adders', lazy="dynamic"))
    '''completed_books = db.relationship("Books", secondary=users_completed, lazy="dynamic", backref=db.backref('completed_adders', lazy="dynamic"))
    reading_books = db.relationship("Books", secondary=users_reading, lazy="dynamic", backref=db.backref('completed_adders', lazy="dynamic"))
    planned_books = db.relationship("Books", secondary=users_planned, lazy="dynamic", backref=db.backref('completed_adders', lazy="dynamic"))'''

    def __repr__(self):
        return f"Users({self.username}, {self.email}, {self.image})"


# A table to represent many-to-many relationship between the authors and the books
authors_books = db.Table('authors_books',
    db.Column('author_id', db.Integer, db.ForeignKey('authors.id'), primary_key=True),
    db.Column('book_id', db.Integer, db.ForeignKey('books.id'), primary_key=True)
)


# A table where all book info is stored
class Books(db.Model):
    __searchable__ = ["title", "year", "rating", "isbn", "written_by[0].name"]

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    # isbn13
    isbn = db.Column(db.String(13), unique=True)
    num_ratings = db.Column(db.Integer)
    image_url = db.Column(db.String(60))
    # Add the relationship to authors table
    written_by = db.relationship("Authors", lazy="dynamic", secondary=authors_books, backref=db.backref('books_written', lazy="dynamic"))

    def __repr__(self):
        return f"Books({self.title}, {self.isbn}, {self.rating})"


# Authors' names
class Authors(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f"Authors({self.name})"