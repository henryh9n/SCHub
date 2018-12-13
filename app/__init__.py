#!/usr/bin/env python3

"""Initializing the application."""

__version__ = '1.0.0'
__author__ = 'hharutyunyan'
__copyright__ = 'Copyright 2018, hharutyunyan'
__license__ = 'All Rights Reserved'
__maintainer__ = 'hharutyunyan'
__status__ = "Production"

from flask import Flask, g, request, session, render_template
from datetime import datetime

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config.from_object('config')

# Importing after initializing the db to avoid cyclic import problems

from app.lib.db import DB

db = DB(app.config.get('DB_HOST'),
        app.config.get('DB_USER'),
        app.config.get('DB_PWD'),
        app.config.get('DB_NAME'))

from app.routes import routes
from app.models.users import Users


@app.before_request
def before_request():
    """Initialize globals before processing the request."""
    g.user = None
    # Checking of non static file is requested
    if '/static/' not in request.path:
        # initializing user id user_id is in session
        if 'user_id' in session:
            g.user = Users().get_user_by_id(session['user_id'])


@app.context_processor
def inject_date():
    """Method to pass current date to all templates."""
    return {'now': datetime.utcnow()}


# Registering the routes from routs.py
app.register_blueprint(routes)
