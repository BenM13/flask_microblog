from app import app, db
from app.models import User, Post

@app.shell_context_processor
def make_shell_context():
    '''
    This function is invoked when the flask shell command is executed in bash.
    Gives the ability to work with database entities in the shell without using 
    import statemtns at the beginning of each shell session.
    '''
    return {'db': db, 'User': User, 'Post': Post}