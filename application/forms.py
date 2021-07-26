from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from application.database import Users
from flask_login import current_user


class RegistrationForm(FlaskForm):
    # Make a username field and create its conditions
    username = StringField("Username", validators=[DataRequired(), Length(min=2, max=20)])
    # Make an email field and create its conditions
    email = StringField("Email", validators=[DataRequired(), Email()])
    # Make a password and a confirmation field and create their conditions
    password = PasswordField("Password", validators=[DataRequired(), Length(min=4, max=35)])
    confirmation = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    # The submit button
    submit = SubmitField("Register")

    def validate_username(self, username):
        '''Check if the username is already in the database'''
        user = Users.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("This username already exists.")

    def validate_email(self, email):
        '''Check if the email is already in the database'''
        email = Users.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError("This email already exists.")


class LoginForm(FlaskForm):
    # Make an email field and create its conditions
    email = StringField("Email", validators=[DataRequired(), Email()])
    # Make a password field and create it's conditions
    password = PasswordField("Password", validators=[DataRequired(), Length(min=4, max=35)])
    remember = BooleanField("Remember Me")
    # The submit button
    submit = SubmitField("Login")


class UpdateAccountForm(FlaskForm):
    # Make a username field and create its conditions
    username = StringField("Username", validators=[DataRequired(), Length(min=2, max=20)])
    # Make an email field and create its conditions
    email = StringField("Email", validators=[DataRequired(), Email()])
    # The submit button
    submit = SubmitField("Save changes")

    def validate_username(self, username):
        '''Check if the username is already in the database'''
        if username.data != current_user.username:
            user = Users.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError("This username already exists.")

    def validate_email(self, email):
        '''Check if the email is already in the database'''
        if email.data != current_user.email:
            email = Users.query.filter_by(email=email.data).first()
            if email:
                raise ValidationError("This email already exists.")


class UpdateImageForm(FlaskForm):
    # Make a picture field and create its conditions
    image = FileField("Change Profile Picture", validators=[FileAllowed(["jpg", 'png'])])
    # The submit button
    submit = SubmitField("Save changes")

