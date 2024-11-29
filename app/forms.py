from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    EqualTo,
    ValidationError,
    Regexp
)
from app.models.user import User


class RegistrationForm(FlaskForm):
    """
    Form for user registration.
    """
    username = StringField(
        'Username',
        validators=[
            DataRequired(message="Username is required."),
            Length(min=3, max=50,
                   message="Username must be between 3 and 50 characters."),
            Regexp(
                regex=r'^[A-Za-z][A-Za-z0-9_.]*$',
                message="Username must start with a letter and contain only letters, numbers, dots, or underscores."
            )
        ]
    )
    email = StringField(
        'Email',
        validators=[
            DataRequired(message="Email is required."),
            Email(message="Invalid email format."),
            Length(max=150,
                   message="Email must be less than 150 characters.")
        ]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message="Password is required."),
            Length(min=8,
                   message="Password must be at least 8 characters long."),
            Regexp(
                regex=r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$',
                message="Password must contain at least one letter and one number."
            )
        ]
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(message="Please confirm your password."),
            EqualTo('password', message="Passwords must match.")
        ]
    )
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        """
        Custom validator to check if the username is already taken.
        """
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                'This username is already taken. Please choose a different one.')

    def validate_email(self, email):
        """
        Custom validator to check if the email is already registered.
        """
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(
                'This email is already registered. Please choose a different one.')


class LoginForm(FlaskForm):
    """
    Form for user login.
    """
    email = StringField(
        'Email',
        validators=[
            DataRequired(message="Email is required."),
            Email(message="Invalid email format."),
            Length(max=150,
                   message="Email must be less than 150 characters.")
        ]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message="Password is required.")
        ]
    )
    submit = SubmitField('Log In')
