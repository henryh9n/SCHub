#!/usr/bin/env python3

"""Classes and methods to interact with users."""

__version__ = '0.0.1'
__author__ = 'hharutyunyan'
__copyright__ = 'Copyright 2018, hharutyunyan'
__license__ = 'All Rights Reserved'
__maintainer__ = 'hharutyunyan'
__status__ = "Production"

from flask import g

from app.lib.model import Model


class Revisions(Model):
    """ Class for defining the structure for projects.

    """

    def __init__(self):
        self.table_name = 'revisions'
        self.fields = {
            'project_id': None,
            'revision_id': None,
            'contributor_id': None,
            'comment': None,
            'diff': None,
            'tag': None,
            'date_added': {'rdonly': True},
        }

        super().__init__()
