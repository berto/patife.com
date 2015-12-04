# -*- coding: utf-8 -*-
"""
    Patife.com website

"""
from __builtin__ import unicode

from flask import Flask, request, session, redirect, url_for, abort, \
    render_template, flash, _app_ctx_stack  # Import Flask libraries and features
from flaskext.mysql import MySQL
from datetime import datetime, date, time
# Import flask-mysql. It need to be installed additionally: pip2 install flask-mysql. Only works with Python2 for now
import MySQLdb.cursors
from flask_sqlalchemy import SQLAlchemy

# Configuration for our Flask application
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# Configuration for DB
MYSQL_DATABASE_HOST = '127.0.0.1'
MYSQL_DATABASE_DB = 'test'
MYSQL_DATABASE_USER = 'root'
MYSQL_DATABASE_PASSWORD = ''

SQLALCHEMY_DATABASE_URI = 'mysql://root:root@127.0.0.1/test'

# Creating the application
app = Flask(__name__)
# Configuring the application using default naming
app.config.from_object(__name__)

db = SQLAlchemy(app)

# Initializing MySQL application
mysql = MySQL(cursorclass=MySQLdb.cursors.DictCursor)
mysql.init_app(app)


class Category(db.Model):
    """
    This is blog entry's category
    """
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    title_en = db.Column(db.Text, nullable=False)
    title_pt = db.Column(db.Text, nullable=False)
    weight = db.Column(db.Integer, nullable=False)

    def __init__(self, title_en, title_pt, weight):
        self.title_en = title_en
        self.title_pt = title_pt
        self.weight = weight

    def __repr__(self):
        return '<Category {}({})>'.format(self.title_en, self.title_pt)


class Entry(db.Model):
    """
    This is blog entry's category
    """
    __tablename__ = 'entries'

    id = db.Column(db.Integer, primary_key=True)
    title_en = db.Column(db.Text, nullable=False)
    title_pt = db.Column(db.Text, nullable=False)
    text_en = db.Column(db.Text, nullable=False)
    text_pt = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.Date, nullable=False, default=date.today)
    date_updated = db.Column(db.Date, nullable=False, onupdate=date.today)
    category_id = db.Column(db.Integer)

    category = db.relationship('Category',
                               backref=db.backref('entries', lazy='dynamic'))

    def __init__(self, title_en, title_pt, text_en, text_pt, category=None):
        self.title_en = title_en
        self.title_pt = title_pt
        self.text_en = text_en
        self.text_pt = text_pt
        self.category = category

    def __repr__(self):
        return '<Entry {}({})>'.format(self.title_en, self.title_pt)


# def get_db():
#     """Opens a new database connection if there is none yet for the
#     current application context.
#     """
#     top = _app_ctx_stack.top  # Get top element in application context stack
#     if not hasattr(top, 'mysql_db'):  # If we have not connected to DB - connect
#         top.mysql_db = mysql.connect()
#     return top.mysql_db


def init_db():
    """Creates the database tables."""
    db.create_all()
    # with app.app_context():
    #     db = get_db()
    #     request = ""  # Reading schema.sql and setting for request
    #     with app.open_resource('schema.sql', mode='r') as f:
    #         request += f.read() + " "
    #     # Executing request
    #     cursor = db.cursor()
    #     cursor.execute(request)
    #     cursor.close()
    #     # Commiting changes to DB
    #     db.commit()


# @app.teardown_appcontext
# def close_db_connection(exception):
#     """Closes the database again at the end of the request."""
#     top = _app_ctx_stack.top  # Get top element in application context stack
#     # If we have a connection to DB - close it
#     if hasattr(top, 'mysql_db'):
#         top.mysql_db.close()


@app.route('/')
def home_view():
    return redirect(url_for('view_entries'))


@app.route('/entries/')
def view_entries():
    # # Getting cursor and selecting all entries from DB
    # cursor = get_db().cursor()
    # cursor.execute('SELECT * FROM entries ORDER BY date_created DESC')
    # entries = cursor.fetchall()
    # cursor.execute('SELECT * FROM categories ORDER BY weight DESC')
    # categories = cursor.fetchall()
    # # MySQL need cursors to be closed immediately after we execute request
    # cursor.close()
    entries = Entry.query.order_by(Entry.date_created).all()
    categories = Category.query.order_by(Category.weight).all()
    # Rendering index page
    return render_template('entry_read_all.html',
                           entries=entries, categories=categories)


@app.route('/entries/<int:entry_id>/')
def view_entry(entry_id):
    # # Getting cursor and selecting entry from DB
    # cursor = get_db().cursor()
    # # we use * to get all fields from entries, otherwise we'd have to call them one by one
    # query = "SELECT * FROM entries WHERE id={0}".format(id)
    # cursor.execute(query)
    # entry = cursor.fetchone()
    # cursor.close()
    # Rendering edit page
    entry = Entry.query.get(entry_id)
    return render_template('entry_read.html', entry=entry)


@app.route('/entries/new')
def new_entry():
    # cursor = get_db().cursor()
    # query = "SELECT * FROM categories ORDER BY weight DESC".format(id)
    # cursor.execute(query)
    # categories = cursor.fetchall()
    # cursor.close()

    categories = Category.query.order_by(Category.weight).all()

    # just displaying the blank template to add
    return render_template('entry_create.html', categories=categories, current_time=date.today())


@app.route('/entries/add', methods=['POST'])
def add_entry():
    # If we are not logged in - abort request
    if not session.get('logged_in'):
        abort(401)
    # Getting cursor and executing insert query with title and text
    db = get_db()
    cursor = db.cursor()
    # you can have {0}, {1}, {2}, {3} instead of "{}" if you plan to reuse them multiple times and refer to them multiple times too
    # we use u before the MySQL query to denote unicode, so that we can use international characters such as "á"
    query = u'INSERT INTO entries (title_en, text_en, title_pt, text_pt, date_created, date_updated, category_id) VALUES ("{}", "{}", "{}", "{}", "{}", "{}", {})'.format(
        unicode(request.form['title_en']), unicode(request.form['text_en']), unicode(request.form['title_pt']), unicode(request.form['text_pt']), request.form['date_created'],
        request.form['date_updated'], request.form['category_id'])
    cursor.execute(query)
    cursor.close()
    # Commiting changes to DB
    db.commit()
    # Return index page with successful message
    flash('New entry was successfully posted')
    return redirect(url_for('home_view'))


@app.route('/entries/<int:entry_id>/edit')
def edit_entry(entry_id):
    # Getting cursor and selecting entry for edit from DB
    # cursor = get_db().cursor()
    # # we use * to get all fields from entries, otherwise we'd have to call them one by one
    # query = "SELECT * FROM entries WHERE id={0}".format(id)
    # cursor.execute(query)
    # entry = cursor.fetchone()
    # query = "SELECT * FROM categories ORDER BY weight DESC"
    # cursor.execute(query)
    # categories = cursor.fetchall()
    # cursor.close()

    entry = Entry.query.get(entry_id)
    categories = Category.query.order_by(Category.weight).all()
    # Rendering edit page
    return render_template('entry_update_and_delete.html', entry=entry, categories=categories,
                           current_time=date.today())


@app.route('/entries/update', methods=['POST'])
def update_entry():
    # If we are not logged in - abort request
    if not session.get('logged_in'):
        abort(401)
    # Getting cursor and search, if we have record with this ID
    db = get_db()
    cursor = db.cursor()
    query = 'SELECT id FROM entries WHERE id={0}'.format(request.form['id'])
    cursor.execute(query)
    data = cursor.fetchone()
    cursor.close()
    # If we have not record with this ID - return 404 error
    if data is not None:
        # Update record, using new text and title
        cursor = db.cursor()
        query = u'UPDATE entries SET title_en="{}", text_en="{}", title_pt="{}", text_pt="{}", date_created="{}", date_updated="{}", category_id={} WHERE id={}'.format(
            unicode(request.form['title_en']), unicode(request.form['text_en']), unicode(request.form['title_pt']), unicode(request.form['text_pt']), request.form['date_created'],
            request.form['date_updated'], request.form['category_id'], request.form['id'])
        # app.logger.info(query)
        cursor.execute(query)
        # abort(500)
        cursor.close()
        db.commit()
        # Return index page with successful message
        flash('Entry was successfully updated')
        return redirect(url_for('view_entries'))
    else:
        abort(404)


@app.route('/entries/delete', methods=['POST'])
def delete_entry():
    # If we are not logged in - abort request
    if not session.get('logged_in'):
        abort(401)
    # Getting cursor and search, if we have record with this ID
    db = get_db()
    cursor = db.cursor()
    query = "SELECT id FROM entries WHERE id={0}".format(request.form['id'])
    cursor.execute(query)
    data = cursor.fetchone()
    cursor.close()
    # If we have not record with this ID - return 404 error
    if data is not None:
        # Update record, using new text and title
        cursor = db.cursor()
        query = 'DELETE FROM entries WHERE id={}'.format(request.form['id'])
        cursor.execute(query)
        cursor.close()
        db.commit()
        # Return index page with successful message
        flash('Entry was successfully deleted')
        return redirect(url_for('home_view'))
    else:
        abort(404)


@app.route('/categories/')
def view_categories():
    # Getting cursor and selecting all entries from DB
    cursor = get_db().cursor()
    cursor.execute('SELECT * FROM categories ORDER BY weight DESC')
    categories = cursor.fetchall()
    # MySQL need cursors to be closed immediately after we execute request
    cursor.close()
    # Rendering index page
    return render_template('category_read_all.html', categories=categories)


@app.route('/categories/<int:id>/')
def view_category(id):
    # Getting cursor and selecting category from DB
    cursor = get_db().cursor()
    # we use * to get all fields from entries, otherwise we'd have to call them one by one
    query = "SELECT * FROM categories WHERE id={0}".format(id)
    cursor.execute(query)
    category = cursor.fetchone()
    cursor.close()
    # Rendering edit page
    return render_template('category_read.html', category=category)


@app.route('/categories/new')
def new_category():
    cursor = get_db().cursor()
    query = "SELECT * FROM categories ORDER BY weight DESC".format(id)
    cursor.execute(query)
    categories = cursor.fetchall()
    cursor.close()

    # just displaying the blank template to add
    return render_template('category_create.html', categories=categories)


@app.route('/categories/add', methods=['POST'])
def add_category():
    # If we are not logged in - abort request
    if not session.get('logged_in'):
        abort(401)
    # Getting cursor and executing insert query with title and weight
    db = get_db()
    cursor = db.cursor()
    # we use u before the MySQL query to denote unicode, so that we can use international characters such as "á"
    query = u'INSERT INTO categories (title_en, title_pt, weight) VALUES ("{}","{}", {})'.format(unicode(request.form['title_en']), unicode(request.form['title_pt']), request.form['weight'])
    cursor.execute(query)
    cursor.close()
    # Commiting changes to DB
    db.commit()
    # Return index page with successful message
    flash('New category was successfully posted')
    return redirect(url_for('view_categories'))


@app.route('/categories/<int:id>/edit')
def edit_category(id):
    # Getting cursor and selecting entry for edit from DB
    cursor = get_db().cursor()
    # we use * to get all fields from entries, otherwise we'd have to call them one by one
    query = "SELECT * FROM categories WHERE id={0}".format(id)
    cursor.execute(query)
    category = cursor.fetchone()
    cursor.close()
    # Rendering edit page
    return render_template('category_update_and_delete.html', category=category)


@app.route('/categories/update', methods=['POST'])
def update_category():
    # If we are not logged in - abort request
    if not session.get('logged_in'):
        abort(401)
    # Getting cursor and search, if we have record with this ID
    db = get_db()
    cursor = db.cursor()
    query = 'SELECT id FROM categories WHERE id={0}'.format(request.form['id'])
    cursor.execute(query)
    data = cursor.fetchone()
    cursor.close()
    # If we have not record with this ID - return 404 error
    if data is not None:
        # Update record, using new title and weight
        cursor = db.cursor()
        query = u'UPDATE categories SET title_en="{}", title_pt="{}", weight={} WHERE id={}'.format(
            unicode(request.form['title_en']), unicode(request.form['title_pt']), request.form['weight'], request.form['id'])
        # app.logger.info(query)
        cursor.execute(query)
        # abort(500)
        cursor.close()
        db.commit()
        # Return index page with successful message
        flash('Category was successfully updated')
        return redirect(url_for('view_categories'))
    else:
        abort(404)


@app.route('/categories/delete', methods=['POST'])
def delete_category():
    # If we are not logged in - abort request
    if not session.get('logged_in'):
        abort(401)
    # Getting cursor and search, if we have record with this ID
    db = get_db()
    cursor = db.cursor()
    query = 'SELECT id FROM categories WHERE id={0}'.format(request.form['id'])
    cursor.execute(query)
    data = cursor.fetchone()
    cursor.close()
    # If we have not record with this ID - return 404 error
    if data is not None:
        # Delete record
        cursor = db.cursor()
        query = 'DELETE FROM categories WHERE id={}'.format(request.form['id'])
        cursor.execute(query)
        cursor.close()
        db.commit()

        # Now that the category doesn't exist, remove it from entries whose category_id matches
        cursor = db.cursor()
        query = 'UPDATE entries SET category_id=NULL WHERE category_id={}'.format(request.form['id'])
        cursor.execute(query)
        cursor.close()
        db.commit()

        # success message
        flash('Category was successfully deleted and related Entries updated')

        return redirect(url_for('home_view'))
    else:
        abort(404)


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


@app.route('/test')
def test_css():
    #test CSS
    return render_template('CSSplayground.html')

if __name__ == '__main__':
    # un-comment the init_db below if you want to start without any db setup.
    # init_db()
    app.run()  # Execute app
