'''
- Resets the tables completely in "site.db", getting tables from the models in "database.py"
- Will reload the books from the file "books.csv" which is in the same dir
- Takes a bit too long to finish hehe
'''

from application.database import *
from csv import DictReader
from datetime import datetime

def repair_url(url):
    '''To return the largest image from the url'''
    if "nophoto" in url:
        return "/static/assets/no_cover.jpg"
    parts = url.split("/")
    # If that part represents medium image
    if parts[4].endswith("m"):
        # Make it l for large
        parts[4] = parts[4].replace("m", "l")
        return "/".join(parts)


db.reflect()
db.drop_all()
db.create_all()

try:
    with open("books.csv", "r") as books_file:
        books_csv = DictReader(books_file)
        # Add every book's info from csv to its table
        for book in books_csv:
            db_book = Books.query.filter_by(title=book["title"]).first()


            # If the book isn't already in the Books table
            if not db_book:
                if book["isbn13"] and len(book["isbn13"].strip()) <= 15:
                    isbn = book["isbn13"]
                elif book["isbn"] and len(book["isbn"].strip()) <= 15:
                    isbn = book["isbn"]
                else:
                    isbn = None
                db_book = Books(title=book["title"], year=book["original_publication_year"], rating=book["average_rating"],
                                isbn=isbn, num_ratings=book["ratings_count"], image_url=repair_url(book["image_url"]))
                db.session.add(db_book)


                # Multiple authors for a book are separated with "/"
                for author in book["authors"].split("/"):
                    # If the author isn't already in the Authors table
                    db_author = Authors.query.filter_by(name=author).first()
                    if not db_author:
                        db_author = Authors(name=author)
                        db.session.add(db_author)
                    # Append the relationship between the author and the book
                    db_author.books_written.append(db_book)
        db.session.commit()
except FileNotFoundError:
    print("books.csv must be in the same folder as this file")
    exit()

print("---The database was reset successfully---")