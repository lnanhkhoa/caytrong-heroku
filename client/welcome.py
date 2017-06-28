# coding=utf-8
import os
from client import app
from flask import flash, session, render_template, request

app.secret_key = "sercet-Key"
# session['logged_in'] = False


@app.route('/<path:path>')
def catch_all(path):
    """
    :param path: any path
    :return: String
    """
    return 'You want path: %s' % path


# ! The index page is initially show.
@app.route('/', methods=['GET', 'POST'])
def welcome():
    """

    :return:
    """
    return render_template('index.html')


@app.route('/editseasons')
def editseasons():
    """
    :return:
    """

    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template("editseasons.html")


@app.route('/login', methods=['POST'])
def do_admin_login():
    if request.form['password'] == 'password' and request.form['username'] == 'admin':
        session['logged_in'] = True
    else:
        flash('wrong password!')
    return editseasons()


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return welcome()


@app.route('/about')
def about():
    """

    :return:
    """
    return render_template("about.html")


@app.route('/contact')
def contact():
    """

    :return:
    """
    return render_template("contact.html")

@app.route('/session',methods=['POST'])
def check_session():
    if request.method == 'POST':
        if not session['logged_in']:
            return "0"
        return "1"
    return "Error"

@app.route('/database')
def database():
    """

    :return:
    """
    return render_template("databasepage.html")
