from flask import render_template
from . import main
from ..models import User
# view functions for index page
# unfinished

@main.route('/')
def index():
    return render_template('index.html')


@main.route('/user/<username>')
def user():
    users = User.query.filter_by(username=username).first_or_404
    return render_template('user.html', user=users)
