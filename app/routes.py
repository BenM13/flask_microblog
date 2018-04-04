from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm
from app.models import User
from werkzeug.urls import url_parse
from datetime import datetime

# pylint: disable=no-member

@app.before_request
def before_request():
    '''
    Checks if current user is logged in. If True, sets the last_seen 
    field to the current time.
    '''
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/')
@app.route('/index')
@login_required # users must be logged in to view this page
def index():
    '''
    Renders index template. Final product will display most recent posts.
    Currently displays hard-coded posts below.
    '''
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Why is it cold on the first day of spring?'
        },
        {
            'author': {'username': 'Emily'},
            'body': 'I got my boyfriend into Grey\'s Anatomy. I feel accomplished!'
        },
        {
            'author': {'username': 'Ben'},
            'body': 'Seriously, how did I get into Grey\'s so quickly?'
        }
    ]
    return render_template('index.html', title='Home', posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    '''
    Renders the login template. First checks if users are already logged into app 
    and redirects to index if True. Upon submission, queries database for user. 
    If password or username mismatch, reloads the login page and displays error
    message. If credentials are correct, login_usser() function is called and 
    newly logged in user is redirected to the index page. 
    '''
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    '''
    Logs the user out and redirects to index page
    '''
    logout_user()
    return redirect(url_for('index'))

# pylint: disable=no-member
@app.route('/register', methods=['GET', 'POST'])
def register():
    '''
    Renders the registration form template. Once submission is validated,
    creates a new user and commits the addition to the users db model.
    Redirects to login page when completed.
    '''
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You are now a registered user! Please login below:')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    '''
    Renders the edit_profile template. If validate_on_submit() returns True,
    database is updated with data from the form and a message is displayed. 
    If validate_on_submit() returns False, checks if it was a GET request in which 
    case the initial version of the form template is provided. 
    '''
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                            form=form)

@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f'User {username} not found.')
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(f'You are now following {username}!')
    return redirect (url_for('user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f'User {username} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(f'You are no longer following {username}.')
    return redirect(url_for('user'))
