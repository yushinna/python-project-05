import datetime

from flask import request, Flask, g, render_template, flash, redirect, url_for
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from slugify import slugify

import forms
import models


DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = 'this is our super secret key.'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.select().where(
            models.User.id == int(userid)
        ).get()
    except models.DoesNotExist:
        return None


@app.before_request
def before_request():
    g.db = models.db
    g.db.connect(reuse_if_open=True)
    g.user = current_user


@app.after_request
def after_request(response):
    g.db.close()
    return response


@app.route('/register', methods=('GET', 'POST'))
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        models.User.create_user(
            email=form.email.data,
            password=form.password.data
        )
        flash("Thanks for registering!")
        user = models.User.get(models.User.email == form.email.data)
        login_user(user)
        flash("You've been logged in!", "success")
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash("Your email or password doesn't match!", "error")
        else:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You've been logged in!", "success")
                return redirect(url_for('index'))
            else:
                flash("Your email or password doesn't match!", "error")
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash("You've been logged out! Come back soon!", "success")
    return redirect(url_for('index'))


@app.route('/')
def index():
    entries = models.Entry.select().order_by(
        models.Entry.id.desc()
    ).limit(10)
    return render_template('index.html', entries=entries)


@app.route('/search/<tag>')
def search_results(tag):
    entries = models.Entry.select().where(models.Entry.tag == tag).order_by(
        models.Entry.id.desc()
    ).limit(10)
    return render_template('index.html', entries=entries)


@app.route('/new', methods=('GET', 'POST'))
@login_required
def create_entry():
    form = forms.EntryForm()
    if form.validate_on_submit():
        models.Entry.create(
            user=g.user.id,
            title=form.title.data,
            slug=slugify(form.title.data, separator="-", lowercase=True),
            date=form.date.data,
            time_spent=form.time_spent.data,
            what_you_learned=form.what_you_learned.data,
            resources_to_remember=form.resources_to_remember.data,
            tag=form.tag.data
        )
        flash("Create new entry!", "success")
        return redirect(url_for('index'))

    form.date.data = datetime.datetime.now()
    return render_template('new.html', form=form)


@app.route('/entries/<slug>', methods=['GET'])
def show_entry(slug):
    entry = models.Entry.get(models.Entry.slug == slug)
    return render_template('detail.html', entry=entry)


@app.route('/entries/<slug>/edit', methods=['GET', 'POST'])
@login_required
def edit_entry(slug):
    entry = models.Entry.get(models.Entry.slug == slug)
    form = forms.EntryForm()
    if form.validate_on_submit():
        entry.title = form.title.data
        entry.slug = slugify(form.title.data, separator="-", lowercase=True)
        entry.date = form.date.data
        entry.time_spent = form.time_spent.data
        entry.what_you_learned = form.what_you_learned.data
        entry.resources_to_remember = form.resources_to_remember.data
        entry.tag = form.tag.data
        entry.save()
        flash("Update entry!", "success")
        return redirect(url_for('show_entry', slug=entry.slug))

    form.title.data = entry.title
    form.date.data = entry.date
    form.time_spent.data = entry.time_spent
    form.what_you_learned.data = entry.what_you_learned
    form.resources_to_remember.data = entry.resources_to_remember
    form.tag.data = entry.tag
    return render_template('edit.html', entry=entry, form=form)


@app.route('/entries/<slug>/delete', methods=['GET'])
@login_required
def delete_entry(slug):
    entry = models.Entry.get(models.Entry.slug == slug)
    entry.delete_instance()
    flash("Delete entry!", "success")
    return redirect(url_for('index'))


if __name__ == "__main__":
    models.initialize()
    app.run(debug=DEBUG, host=HOST, port=PORT)
