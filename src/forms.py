from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from flask_login import current_user

from src.models.user import User


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


class UpdateProfileForm(FlaskForm):

    username = StringField('Username',
                           validators=[Length(min=3, max=25)])

    picture = FileField('Picture', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])


    submit = SubmitField('Update')


class PostForm(FlaskForm):
    caption = TextAreaField('Caption', validators=[Length(min=0, max=1000)])
    picture = FileField('Picture', validators=[DataRequired(), FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField('Post')