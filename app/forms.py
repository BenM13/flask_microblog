from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, BooleanField, 
    SubmitField, TextAreaField)
from wtforms.validators import (ValidationError, DataRequired, Email, 
    EqualTo, Length)
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    '''
    New user registration form. Prompts new user for username, email, password,
    and confirmation of password. 
    '''
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        '''
        Username must be unique. Checks if username already exists in database
        and raises a validation error if it does. 
        '''
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username already exists; please use another')
        
    def validate_email(self, email):
        '''
        Email must be unique. Checks if email already exists in database and 
        raises a validation error if it does. 
        '''
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Emaiil already exists: please use another.')

class EditProfileForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
    
    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Username already exists; please use another')

class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')