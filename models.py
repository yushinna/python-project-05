from flask_bcrypt import Bcrypt
from flask_login import UserMixin
from flask import Flask
from peewee import *

db = SqliteDatabase('entry.db')

app = Flask(__name__)
bcrypt = Bcrypt(app)


class BaseModel(Model):
    class Meta:
        database = db


class User(UserMixin, BaseModel):
    email = CharField(unique=True)
    password = CharField(max_length=100)

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


class Entry(BaseModel):
    title = CharField(max_length=100)
    slug = CharField(unique=True)
    date = DateTimeField()
    time_spent = IntegerField()
    what_you_learned = TextField()
    resources_to_remember = TextField()
    user = ForeignKeyField(User)


class Tag(BaseModel):
    tag = CharField(max_length=50)
    entry = ForeignKeyField(Entry)


def initialize():
    db.connect()
    db.create_tables([User, Entry, Tag], safe=True)
    db.close()
