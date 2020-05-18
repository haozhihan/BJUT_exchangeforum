from flask import Blueprint

transaction = Blueprint('transaction', __name__)

from . import views