from flask import render_template
from . import main
# view functions for index page
# unfinished

@main.route('/')
def index():
    return render_template('index.html')
