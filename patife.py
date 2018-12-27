# -*- coding: utf-8 -*-
"""
    Patife.com website

"""
from datetime import datetime
import os

from flask import (Flask, request, session, redirect, url_for, abort, render_template, flash, make_response)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
import pytz
import markdown


# Configuration for our Flask application
# To have debug variable true for dev, better set env variable

SECRET_KEY = os.environ['SECRET_KEY']

# Gets the database url inc user and password from environment variable
# On production server the variable is set, on the local dev machine we can use pyCharm to configure it
SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
SQLALCHEMY_TRACK_MODIFICATIONS = True
PASSWORD = os.environ['ADMIN_PASSWORD']
DEBUG = os.environ.get('DEBUG', 'False') in ('True', 'true', '1')
USERNAME = os.environ['ADMIN_USER']

# Creating the application
app = Flask(__name__)
# Configuring the application using default naming
app.config.from_object(__name__)

db = SQLAlchemy(app)


class Category(db.Model):
    """
    This is a category
    """

    # Define the table name within database
    __tablename__ = 'categories'

    # Define the contents of each row in the database
    id = db.Column(db.Integer, primary_key=True)
    title_en = db.Column(db.Text, nullable=False)
    weight = db.Column(db.Integer, nullable=False)

    entries = db.relationship('Entry', order_by='Entry.date_created.desc()')

    # Define how a row is created
    def __init__(self, title_en, weight):
        self.title_en = title_en
        self.weight = weight

    # returns representation of itself
    def __repr__(self):
        return '<Category {}({})>'.format(self.title_en)

    @property
    def title(self):
        # language setting dependent property for title
        if request.cookies.get('lang', 'en') == 'en':
            return self.title_en
        else:
            return self.title_en


class Entry(db.Model):
    """
    This is an entry
    """
    __tablename__ = 'entries'

    id = db.Column(db.Integer, primary_key=True)
    title_en = db.Column(db.Text, nullable=False)
    text_en = db.Column(db.Text, nullable=False)
    html_en = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.Date, nullable=False, default=datetime.today)
    date_updated = db.Column(db.Date, nullable=False, default=datetime.today, onupdate=datetime.today)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))

    # Define method to get entry.category, and a reverse method to get category.entries
    category = db.relationship('Category')

    def __init__(self, title_en, text_en, html_en, category_id=None, date_created=None, date_updated=None):
        self.title_en = title_en
        self.text_en = text_en
        self.html_en = html_en
        self.category_id = category_id
        self.date_created = date_created
        self.date_updated = date_updated

    def __repr__(self):
        return '<Entry {}({})>'.format(self.title_en)

    @property
    def title(self):
        # language setting dependent property for title
        if request.cookies.get('lang', 'en') == 'en':
            return self.title_en
        else:
            return self.title_en

    @property
    def text(self):
        # language setting dependent property for text
        if request.cookies.get('lang', 'en') == 'en':
            return self.text_en
        else:
            return self.text_en

    @property
    def html(self):
        # language setting dependent property for text
        if request.cookies.get('lang', 'en') == 'en':
            return self.html_en
        else:
            return self.html_en

def init_db():
    """Creates the database tables."""
    db.create_all()


@app.route('/')
def home_view():
    return redirect(url_for('view_categories'))


@app.route('/entries/')
def view_entries():
    # Selecting all entries and categories from DB, get newer on top
    entries = Entry.query.order_by(desc(Entry.date_created)).all()
    categories = Category.query.order_by(Category.weight).all()
    # Rendering index page
    return render_template('entry_read_all.html', entries=entries, categories=categories)


@app.route('/entries/<int:entry_id>/')
def view_entry(entry_id):
    # Getting entry from DB
    entry = Entry.query.get(entry_id)
    if entry is None:
        abort(404)
    return render_template('entry_read.html', entry=entry)


@app.route('/entries/new')
def new_entry():
    categories = Category.query.order_by(Category.weight).all()
    # just displaying the blank template to add
    return render_template('entry_create.html', categories=categories, current_time=datetime.today())


@app.route('/entries/add', methods=['POST'])
def add_entry():
    # If we are not logged in - abort request
    if not session.get('logged_in'):
        abort(401)

    entry = Entry(
        title_en=request.form['title_en'],
        text_en=request.form['text_en'],
        html_en=markdown.markdown(request.form['text_en'], extensions=['nl2br','tables']),
        category_id=request.form['category_id'],
        date_created=request.form['date_created'],
        date_updated=request.form['date_updated'],
    )

    db.session.add(entry)
    db.session.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('home_view'))


@app.route('/entries/<int:entry_id>/edit')
def edit_entry(entry_id):
    # Getting entry and categories from DB
    entry = Entry.query.get(entry_id)
    categories = Category.query.order_by(Category.weight).all()
    # Rendering edit page
    return render_template('entry_update_and_delete.html', entry=entry, categories=categories,
                           current_time=datetime.today())


@app.route('/entries/update', methods=['POST'])
def update_entry():
    # If we are not logged in - abort request
    if not session.get('logged_in'):
        abort(401)

    entry = Entry.query.get(request.form['id'])
    # If no entry with such ID - abort request
    if entry is None:
        abort(404)
    entry.title_en = request.form['title_en']
    entry.text_en = request.form['text_en']
    entry.html_en = markdown.markdown(request.form['text_en'], extensions=['nl2br','tables']),
    entry.category_id = request.form['category_id']
    entry.date_created = request.form['date_created']
    entry.date_updated = request.form['date_updated']

    db.session.add(entry)
    db.session.commit()
    flash('Entry was successfully updated')
    return redirect(url_for('home_view'))


@app.route('/entries/delete', methods=['POST'])
def delete_entry():
    # If we are not logged in - abort request
    if not session.get('logged_in'):
        abort(401)

    entry = Entry.query.get(request.form['id'])
    # If no entry with such ID - abort request
    if entry is None:
        abort(404)

    db.session.delete(entry)
    db.session.commit()
    flash('Entry was successfully deleted')
    return redirect(url_for('home_view'))


@app.route('/categories/')
def view_categories():
    categories = Category.query.order_by(Category.weight).all()
    # Rendering index page
    return render_template('category_read_all.html', categories=categories, current_time=datetime.utcnow().replace(tzinfo=pytz.UTC))


@app.route('/categories/new')
def new_category():
    categories = Category.query.order_by(Category.weight).all()
    # just displaying the blank template to add
    return render_template('category_create.html', categories=categories)


@app.route('/categories/add', methods=['POST'])
def add_category():
    # If we are not logged in - abort request
    if not session.get('logged_in'):
        abort(401)

    category = Category(
        title_en=request.form['title_en'],
        weight=request.form['weight'],
    )

    db.session.add(category)
    db.session.commit()
    # # Return index page with successful message
    flash('New category was successfully posted')
    return redirect(url_for('home_view'))


@app.route('/categories/<int:category_id>/edit')
def edit_category(category_id):
    category = Category.query.get(category_id)
    if category is None:
        abort(404)
    # Rendering edit page
    return render_template('category_update_and_delete.html', category=category)


@app.route('/categories/update', methods=['POST'])
def update_category():
    # If we are not logged in - abort request
    if not session.get('logged_in'):
        abort(401)
    category = Category.query.get(request.form['id'])
    # If no category with such ID - abort request
    if category is None:
        abort(404)
    category.title_en = request.form['title_en']
    category.weight = request.form['weight']

    db.session.add(category)
    db.session.commit()

    return redirect(url_for('home_view'))


@app.route('/categories/delete', methods=['POST'])
def delete_category():
    # If we are not logged in - abort request
    if not session.get('logged_in'):
        abort(401)

    category = Category.query.get(request.form['id'])
    # If no category with such ID - abort request
    if category is None:
        abort(404)

    db.session.delete(category)
    db.session.commit()

    flash('Category was successfully deleted and related Entries updated')
    return redirect(url_for('home_view'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    # If we made POST request - check username and password
    # Else - return login page
    if request.method == 'POST':
        # First check username, then password
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            # If correct - set True to session in browser
            session['logged_in'] = True
            # Return index page with successful message
            flash('Logged in')
            return redirect(url_for('home_view'))
    return render_template('login_view.html', error=error)


@app.route('/logout')
def logout():
    # Delete logged_in option from session in browser
    session.pop('logged_in', None)
    # Delete logged_in option from session in browser
    flash('See you buddy! You were logged out')
    return redirect(url_for('home_view'))


@app.route('/config_db')
def config_db():
    # call this function to reset the whole database. eheheheh
    # If we are not logged in - abort request
    if not session.get('logged_in'):
        abort(401)
    init_db()
    return redirect(url_for('home_view'))


@app.route('/rss/<lang>')
def view_feed(lang):
    # Selecting all entries and categories from DB, get newer on top
    entries = Entry.query.order_by(desc(Entry.date_created)).all()
    # Reder feed
    if lang not in ('en', 'pt'):
        lang = 'en'
    return render_template('rss.xml', entries=entries, lang=lang)


@app.route('/lang/<lang>')
def set_lang(lang):
    # language switching, store in cookie
    if lang not in ('en', 'pt'):
        lang = 'en'
    resp = make_response(redirect(request.referrer))
    one_year = 60 * 60 * 24 * 365
    resp.set_cookie('lang', lang, max_age=one_year)
    return resp


if __name__ == '__main__':
    # un-comment the init_db below if you want to start without any db setup.
    # init_db()
    app.run()  # Execute app
