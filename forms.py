from flask_wtf import Form
from wtforms import StringField, PasswordField, DateField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, ValidationError, Email, Length, EqualTo
from models import User


def email_exists(form, field):
    if User.select().where(User.email == field.data).exists():
        raise ValidationError('User with that email already exists.')


class RegisterForm(Form):
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
            email_exists
        ])
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=2),
            EqualTo('password2', message='Passwords must match')
        ])
    password2 = PasswordField(
        'Confirm Password',
        validators=[DataRequired()]
    )


class LoginForm(Form):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])


class EntryForm(Form):
    title = StringField('Title', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    time_spent = IntegerField('Time spent (minutes)',
                              validators=[DataRequired()])
    what_you_learned = TextAreaField(
        'What I learnined', validators=[DataRequired()])
    resources_to_remember = TextAreaField(
        'Resources to Remember', validators=[DataRequired()])
    tags = StringField(
        'Tags (seperate by a comma)',
        validators=[DataRequired()
                    ])
