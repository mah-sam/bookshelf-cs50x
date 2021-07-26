from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_msearch import Search


# Configure flask
app = Flask(__name__)
app.config["SECRET_KEY"] = "8642dcdc3c531869a48b646a88903d0a"
# Decide where the database is
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["DEBUG"] = True
db = SQLAlchemy(app)
# For hashing passwords
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
# Specify the functions that has the login page in "routes.py"
login_manager.login_view = "login"
# The alert message that appears when trying to access login required pages
login_manager.login_message_category = "info"
# Database search
search = Search()
search.init_app(app)


from application import routes