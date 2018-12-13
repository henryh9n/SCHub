#!/usr/bin/env python3

"""Classes and methods to interact with users."""

__version__ = '0.0.1'
__author__ = 'hharutyunyan'
__copyright__ = 'Copyright 2018, hharutyunyan'
__license__ = 'All Rights Reserved'
__maintainer__ = 'hharutyunyan'
__status__ = "Production"

import re
import hashlib
from functools import wraps
from flask import g, redirect, url_for, session

from app import app
from app.lib.model import Model


class Users(Model):
    """ Class for defining the structure for users.

    """

    def __init__(self):
        self.table_name = 'users'
        self.fields = {
            'id': {'rdonly': True},
            'first_name': None,
            'second_name': None,
            'email': None,
            'password': None,
            'date_registered': {'rdonly': True},
        }

        self.id = ''
        self.first_name = ''
        self.second_name = ''
        self.email = ''

        super().__init__()

    def get_user_by_id(self, user_id):
        """Method to get user by id"""
        user = self.get(id=user_id)
        if user:
            self.id = user.get('id')
            self.first_name = user.get('first_name')
            self.second_name = user.get('second_name')
            self.email = user.get('email')
            
        return self

    def login_user(self, email: str, pwd: str):
        """Method to log a user in."""
        if not self._check_email(email):
            return 'wrong email format'
        
        user = self.get(email=email)
        if not user:
            return 'wrong login credentials'

        pwd = self._pwd_hash(email, pwd)
        if pwd != user.get('password'):
            return 'wrong login credentials'

        session['user_id'] = user.get('id')

    @staticmethod
    def _check_email(email: str):
        """Method to check if an email is in valid format."""
        email_regex = re.compile(
            r"^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@"
            "((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-"
            "0-9]+\.)+[a-zA-Z]{2,}))$")
        return email_regex.match(email)

    @staticmethod
    def _check_pwd_strength(pwd: str):
        """Method to test if the password if strong."""
        pwd_regex = re.compile(
            r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#\$%\^&\*])(?=.{8,})")
        return pwd_regex.match(pwd)

    @staticmethod
    def _pwd_hash(email: str, pwd: str):
        """Method to generate hash for a password"""
        salt = app.config['SALT']
        return hashlib.sha256('{0}!{1}*{2}'.format(
            email, pwd, salt).encode('utf-8')).hexdigest()


def req_user_login():
    """Wrap the function to require authentication."""

    def decor_w(f):
        @wraps(f)
        def decor_function(*args, **kwargs):
            if g.user is None:
                return redirect(url_for('routes.login'))
            return f(*args, **kwargs)

        return decor_function

    return decor_w
