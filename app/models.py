from datetime import datetime
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5


# pylint: disable=no-member

class User(UserMixin, db.Model):
    '''
    Creates a user database model.
    '''
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        '''
        Given a user inputed password, this function uses Werkzeug
        to create a password hash for that user. 
        '''
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        '''
        Given a user inputed password, this function takes the previously
        generated password hash and returns True if provided password mathes
        and False if otherwise.
        '''
        return check_password_hash(self.password_hash, password)
    
    def avatar(self, size):
        '''
        Returns the URL of the user's avatar image from Gravatar.
        If user does not have an avatar, a Gravatar 'identicon' is generated.
        Converts email to lowercase, encodes to bytes, then generates an MD5 
        hash.
        '''
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

class Post(db.Model):
    '''
    Creates a post database. Maps the author of the post to the user
    with user_id as a foreign key.
    '''
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))