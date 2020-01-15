from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError

from src.models.user import User

"""
def validate_username(username):
    user = User.get_by_username(username)
    if user:
        raise ValidationError("Username is taken.")
"""



class RegistrationForm(FlaskForm):

    username = StringField('Username',
                           validators=[DataRequired(), Length(min=3, max=25)])

    password = PasswordField('Password',
                             validators=[DataRequired()])

    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Sign up')



class LoginForm(FlaskForm):

    username = StringField('Username',
                           validators=[DataRequired(), Length(min=3, max=25)])

    password = PasswordField('Password',
                             validators=[DataRequired()])

    remember = BooleanField('Remember me')

    submit = SubmitField('Login')
