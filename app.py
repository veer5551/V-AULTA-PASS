import os
import sqlite3
from flask import Flask, request, g, redirect, url_for, render_template, flash, session
from functools import wraps
import pandas as pd
from sqlite3 import Error

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'myPassowrdDatabase.db'),
    DEBUG=True,
    SECRET_KEY='v-aulta_pass',
    USERNAME='admin',
    PASSWORD='admin'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash(' You need to login first.')
            return redirect(url_for('login'))

    return wrap


def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r')as f:
            db.cursor().executescript(f.read())
            db.commit()


def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        if request.form['add'] == "ADD":
            print("in add")
            print(request)

            website = request.form['website']
            username = request.form['username']
            password = request.form['password']
            notes = request.form['notes']
            db = get_db()

            if len(website) ==0:
                flash("  **Website Required**", category='alert-danger')
                return render_template('add.html')
            try:
                db.execute('insert into passwordmanager(website,username,password,notes) values(?,?,?,?)',
                       [website, username, password, notes])
                db.commit()
                flash(' Details added', category='alert-success')
            except:
                flash("  Cannot add Details.\n  Please check for Duplication", category='error')

    return render_template('add.html')


@app.route('/view', methods=['GET', 'POST'])
@login_required
def view():
    db = get_db()
    cur = db.execute('select * from passwordmanager')
    entries = cur.fetchall()
    return render_template('view.html', entries=entries)


@app.route('/search', methods=['GET', 'POST'])
def search():
    df = pd.read_sql_query("SELECT * from passwordmanager", get_db())
    col_one_list = df['website'].tolist()
    if request.method == 'POST':
        if request.form['search'] == "SEARCH":
            db = get_db()
            cur = db.execute('select * from passwordmanager where website = ? ', (request.form['website'],))
            entries = cur.fetchall()
            return render_template('view_single.html', entries=entries)
    if request.method == "GET":
        languages = col_one_list
        return render_template("search.html", languages=languages)
    return render_template('search.html')


@app.route('/update', methods=['GET', 'POST'])
@login_required
def update():
    df = pd.read_sql_query("SELECT * from passwordmanager", get_db())
    col_one_list = df['website'].tolist()
    if request.method == 'POST':
        if request.form['search_update'] == "SEARCH_UPDATE":

            # website = request.form['website']
            # username = request.form['username']
            # password = request.form['password']
            # notes = request.form['notes']

            db = get_db()
            cur = db.execute('select * from passwordmanager where website = ? ', (request.form['website_to_update'],))
            entries = cur.fetchall()
            return render_template('update.html', entries=entries)

            # print("Connected to SQLite")
            # sql_update_query = """Update passwordmanager set username=?, password = ?,notes =? where website = 4"""
            # db.execute(sql_update_query,(username, password, notes, website))
            # db.commit()
            # print("Record Updated successfully ")
            # cursor.close()

    if request.method == "GET":
        languages = col_one_list
        return render_template("search2.html", languages=languages)
    return render_template('search2.html')

@app.route('/update2', methods=['GET', 'POST'])
@login_required
def update2():
    if request.method == 'POST':
        if request.form['update'] == "update":
            print("in update")
            print(request)

            website = request.form['website']
            username = request.form['username']
            password = request.form['password']
            notes = request.form['notes']
            db = get_db()

            if len(website) ==0:
                flash("  **Website Required**", category='alert-danger')
                return render_template('update.html')
            try:
                sql = ''' UPDATE passwordmanager
                          SET username = ? ,
                              password = ? ,
                              notes = ?
                          WHERE website = ?'''
                task = [username, password, notes, website]
                # db.execute('insert into passwordmanager(website,username,password,notes) values(?,?,?,?)',
                #        [username, password, notes, website])
                db.execute(sql,task)
                db.commit()
                flash(' Details Updated!',category='alert-success')
            except:
                flash("  Cannot Update Details.\n  Please check for Valid Entries", category='error')

    return render_template('add.html')


@app.route('/delete', methods=['GET', 'POST'])
@login_required
def delete():
    df = pd.read_sql_query("SELECT * from passwordmanager", get_db())
    col_one_list = df['website'].tolist()
    if request.method == 'POST':
        if request.form['delete'] == "delete":
            print("haaaaaaaaaaai")
            print(request.form['website_to_delete'])
            db = get_db()
            cur = db.execute('delete from passwordmanager where website = ? ', (request.form['website_to_delete'],))
            db.commit()
            cur.close()
            flash('Sucessfully Deleted')

    if request.method == "GET":
        languages = col_one_list
        return render_template("delete.html", languages=languages)
    return render_template('delete.html')


@app.route('/', methods=['GET', 'POST'])
def home():
    df = pd.read_sql_query("SELECT * from passwordmanager", get_db())
    col_one_list = df['website'].tolist()

    if request.method == 'POST':
        if request.form['opt'] == "LOGIN":
            return redirect(url_for('login'))
        if request.form['opt'] == "LOGOUT":
            return redirect(url_for('logout'))

        if request.form['search'] == "SEARCH":
            db = get_db()
            cur = db.execute('select * from passwordmanager where website = ? ', (request.form['website'],))
            entries = cur.fetchall()
            return render_template('view_single.html', entries=entries)

    if request.method == "GET":
        languages = col_one_list
        return render_template("home.html", languages=languages)

    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = "username"
        elif request.form['password'] != app.config['PASSWORD']:
            error = "password"
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('home'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash(' You were logged out')
    return redirect(url_for('home'))


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


if __name__ == '__main__':
    init_db()
    PORT = 5000
    app.run(debug=True, port=PORT)
