from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, current_user, login_required
import datetime

from app import db, bcrypt
from app.models import User

main = Blueprint('main', __name__)

host = 'http://127.0.0.1:5000'
@main.route('/home', methods=['GET', 'POST'])
def home():
    return render_template('home.html')


@main.route('/', methods=['GET', 'POST'])
@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    #token = jwt.encode({'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, current_app.config['SECRET_KEY'])
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and bcrypt.check_password_hash(user.password, request.form.get('password')):
            login_user(user, remember=True)
            return redirect(url_for('main.home'))
        flash('Invalid name or password', 'error')

    return render_template('login.html', title='Log in')

@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user:
            flash('Username already taken!', 'error')
        elif request.form.get('password') == request.form.get('confirm_password'):
            hashed_pw = bcrypt.generate_password_hash(request.form.get('password')).decode('utf-8')
            user = User(username=request.form.get('username'), password=hashed_pw)
            db.session.add(user)
            db.session.commit()
            flash('Created new account', 'success')
            return redirect(url_for('main.login'))
        else:
            flash('passwords must be same', 'error')

    return render_template('signup.html', title='Sign up')


@main.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('main.login'))
