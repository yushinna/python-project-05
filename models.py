from flask_bcrypt import Bcrypt
from flask_login import UserMixin
from flask import Flask
from peewee import *

db = SqliteDatabase('entry.db')

app = Flask(__name__)
bcrypt = Bcrypt(app)


class User(UserMixin, Model):
    email = CharField(unique=True)
    password = CharField(max_length=100)

    class Meta:
        database = db

    @classmethod
    def create_user(cls, email, password):
        try:
            with db.transaction():
                cls.create(
                    email=email,
                    password=bcrypt.generate_password_hash(password)
                )
        except IntegrityError:
            raise ValueError("User already exists")


class Entry(Model):
    title = CharField()
    slug = CharField(unique=True)
    date = DateTimeField()
    time_spent = IntegerField()
    what_you_learned = TextField()
    resources_to_remember = TextField()
    tag = CharField()
    user = ForeignKeyField(
        User,
        backref='entry')

    class Meta:
        database = db


def initialize():
    db.connect()
    db.create_tables([User, Entry], safe=True)
    db.close()
