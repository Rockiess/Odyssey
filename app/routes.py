from flask import Flask, render_template, flash, redirect, url_for
from app import app
#
from flask_login import current_user, login_user #User module
from flask_login import logout_user #user logout
from app.models import User #Database
from flask_login import login_required #flask_login's login required
from app import db
from app.l_form import RegistrationForm 
#
from werkzeug.urls import url_parse
from flask import request
from app.l_form import LoginForm
#
from app.chart import returnChartVal

@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', title='Home')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        
        #Obtain user information from the username
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            #User doesn't exist
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        
        return redirect(url_for('index'))
    return render_template('l_form.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    value, date = returnChartVal(user.devices.first(), 3600)
    return render_template('user.html', value=value, date=date, user=user, device_name=str(user.devices.first().name))

