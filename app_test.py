import pytest
from app import app
import models
from peewee import *
from slugify import slugify


app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False
test_client = app.test_client()
models.initialize()

USER_DATA = {
    'email': 'test_0@example.com',
    'password': 'password'
}

ENTRY_DATA = {
    'title': 'Flask App',
    'slug': slugify('Flask App', separator="-", lowercase=True),
    'date': '2020-03-30',
    'time_spent': 60,
    'what_you_learned': 'How to use Flask',
    'resources_to_remember': 'Treehouse',
    'tag': 'flask'
}

EDIT_DATA = {
    'title': 'Flask App Development',
    'slug': slugify('Flask App Development', separator="-", lowercase=True),
    'date': '2020-04-01',
    'time_spent': 60,
    'what_you_learned': 'How to use Flask',
    'resources_to_remember': 'Treehouse',
    'tag': 'flask'
}


class TestUserModel():
    def create_users(self, count=2):
        for i in range(count):
            models.User.create_user(
                email='test_{}@example.com'.format(i),
                password='password'
            )

    def test_create_users(self):
        self.create_users()
        assert models.User.select().count() == 2
        assert models.User.select().get().password != 'password'

    def test_create_duplicate_users(self):
        with pytest.raises(Exception):
            models.User.create_user(
                email='test_1@example.com',
                password='password'
            )


class TestEntryModel():
    def test_entry_creation(self):
        user = models.User.select().get()
        models.Entry.create(
            title='Python Test',
            slug=slugify('Python Test', separator="-", lowercase=True),
            date='2020-03-30',
            time_spent=60,
            what_you_learned='How to use Pytest',
            resources_to_remember='Python Testing with pytest',
            tag='python',
            user=user
        )
        entry = models.Entry.select().get()
        assert entry.select().count() == 1
        assert entry.user == user


class TestUserViews():
    def test_registration(self):
        data = {
            'email': 'test@example.com',
            'password': 'password',
            'password2': 'password'
        }
        rv = test_client.post(
            '/register',
            data=data)
        assert rv.status_code == 302
        assert rv.location == 'http://localhost/'

    def test_good_login(self):
        rv = test_client.post('/login', data=USER_DATA)
        assert rv.status_code == 302
        assert rv.location == 'http://localhost/'

    def test_bad_login(self):
        rv = test_client.post('/login', data={
            'email': 'test_0@example.com',
            'password': 'invalid_password'
        })
        assert rv.status_code == 200

    def test_logout(self):
        rv = test_client.post('/login', data=USER_DATA)
        assert rv.status_code == 302
        assert rv.location == 'http://localhost/'

        rv = test_client.get('/logout')
        assert rv.status_code == 302
        assert rv.location == 'http://localhost/'


class TestEntryViews():
    def test_create_entry(self):
        test_client.post('/login', data=USER_DATA)
        ENTRY_DATA['user'] = models.User.select().get()
        rv = test_client.post('/new', data=ENTRY_DATA)
        assert rv.status_code == 302
        assert rv.location == 'http://localhost/'
        assert models.Entry.select().count() == 2

    def test_delete_entry(self):
        test_client.post('/login', data=USER_DATA)
        rv = test_client.get('/entries/flask-app/delete')
        rv = test_client.get('/entries/python-test/delete')
        assert rv.status_code == 302
        assert rv.location == 'http://localhost/'
        assert models.Entry.select().count() == 0

    def test_edit_entry(self):
        test_client.post('/login', data=USER_DATA)
        ENTRY_DATA['user'] = models.User.select().get()
        test_client.post('/new', data=ENTRY_DATA)
        EDIT_DATA['user'] = models.User.select().get()
        rv = test_client.post('/entries/flask-app/edit', data=EDIT_DATA)
        assert rv.status_code == 302
        assert rv.location == 'http://localhost/entries/flask-app-development'
        test_client.get('/entries/flask-app-development/delete')
        test_client.get('/logout')
        assert models.Entry.select().count() == 0
