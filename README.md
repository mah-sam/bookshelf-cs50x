# Bookshelf: CS50x Final Project

Bookshelf is a web app for browsing and managing books.
Users can add and remove books from their library and label each book with a status,
choosing between "completed", "reading" and "planned".

**Video Demo:** https://youtu.be/jHiIy6f7nE8  
**Deployment:** https://bookshelf-ms.herokuapp.com

## Description

### Specifications

The app is using Flask for the backend (a python framework),  
and many other Flask dependent libraries (like Flask-SQLAlchemy) see requirements.txt for the full list.  
For the frontend, it's using Jinja to render HTML templates along with Bootstrap CSS classes.  
Modular design using Python packaging for easier navigation between functionalities.  
This github app uses sqlite to modify the database, but it's using postgresql for the deployed version.

### Features

- You can Register, Login, and remain remembered for the longest while, all thanks to flask-login package.
- A completely responsive frontend design for all screens using bootstrap breakpoints.
- Database maintaining 10,000 books' information.
- To reduce redundancy, we used Many-to-Many relationships, which were a bit tricky.
- A user can flawlessly add, remove any book from multiple personal libraries.
- A user can edit their profile picture and their Email/Username.
- A modern frontend design using Bootstrap HTML components.
- The ability to search books by title, author and year easily thanks to msearch package.
- The ability to browse all books while sorting by most popular,  highest rated, alphabetical order, and the year of publication.
- Any HTML template displaying all the books in the database is paginated.
- The ability to reset/remove user's account (Only on deployed ver).
- Integration of Google analytics (Only on deployed ver).

## Usage

### Running the app

First install all the dependencies in requirements.txt,  
then while being in the same directory as this file in the command line, run:
```bash
flask run
```
or
```bash
python app.py
```

### Resetting the database

To reset the database and recreate the tables and  rows, execute:
```bash
python reset_db.py
```

## Files Map

### Main directory

- **app.py:** The main executable to launch the web app

- **reset_db.py:** Resets the database, recreating the tables and adding the books

- **books.csv:** The file that has all the books' information that the above file uses to reset the books.

- **credit.txt:** credit attribution where credit is due

### /application

- **\_\_init\_\_.py:** Contains the app's configuration for all the libraries and packages

- **routes.py:** Contains the flask routes that render all the HTML pages

- **database.py:** Contains SQLAlchmey models (the structures)

- **forms.py:** Contains the classes for multiple HTML forms using Flask WTForms

- **site.db:** The main database the web app is using, which effectively contains all the books and users and authors and the relationships between them

### /application/static

- **main.css:** The file that contains any CSS used besides Bootstrap

- **assets:** Contains the images used for the design

- **favicon:** Contains the favicon files/images suitable for most browsers

- **profile_pics:** Contains the compressed profile pictures of the users and the default profile picture "user.jpg"

### /application/templates

- **book.html:** The HTML template to display any book in the database

- **discover.html:** The HTML template to display all the database books sorted according to the user's choice

- **home.html:** The home page

- **layout.html:** The page layout for all the similar elements in all the HTML templates

- **login.html:** Page for logging in users

- **register.html:** Page for registering users

- **mylibrary.html:** Where users can browse the books they added

- **search.html:** Displays search results for books

- **settings.html:** Where users can change their profile information

## Finally

This project took me a while to complete, but it taught me valuable lessons.  
I thank Harvard's CS50 for this fruitful learning opportunity.

### Mahmoud Sameh
