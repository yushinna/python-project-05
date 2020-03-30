import pytest
import app
from models import User, Entry
from peewee import *

test_db = SqliteDatabase(':memory:')
MODELS = (User, Entry)


class TestApp():
    def create_users(self, count=2):
        for i in range(count):
            User.create_user(
                email='test_{}@example.com'.format(i),
                password='password'
            )

    def test_create_users(self):
        with test_db.bind_ctx(MODELS):
            test_db.create_tables(MODELS)
            self.create_users()
            assert User.select().count() == 2
            assert User.select().get().password != 'password'

    def test_create_duplicate_users(self):
        with pytest.raises(Exception):
            with test_db.bind_ctx(MODELS):
                User.create_user(
                    email='test_1@example.com',
                    password='password'
                )

    def test_create_entry(self):
        with test_db.bind_ctx(MODELS):
            user = User.select().get()
            Entry.create(
                title='Python Test Driven Development',
                date='2020/03/30',
                time_spent=60,
                what_you_learnined='How to use Pytest',
                resources_to_remember='Python Testing with pytest',
                tag='python',
                user=user
            )
            entry = Entry.select().get()
            assert entry.select().count() == 1
            assert entry.user == user

    def test_edit_entry(self):
        pass

    def test_delete_entry(self):
        pass

    def test_good_login(self):
        pass

    def test_bad_login(self):
        pass

    def test_logout(self):
        pass

    def test_logged_out_menu(self):
        pass

    def test_logged_in_menu(self):
        pass
