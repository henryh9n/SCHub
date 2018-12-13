#!/usr/bin/env python3

"""Classes and methods to interact with issues."""

__version__ = '0.0.1'
__author__ = 'hharutyunyan'
__copyright__ = 'Copyright 2018, hharutyunyan'
__license__ = 'All Rights Reserved'
__maintainer__ = 'hharutyunyan'
__status__ = "Production"

from app.lib.model import Model


class Issues(Model):
    """ Class for defining the structure for projects.

    """

    def __init__(self):
        self.table_name = 'issues'
        self.fields = {
            'project_id': None,
            'issue_id': None,
            'name': None,
            'description': None,
            'status': None,
            'date_created': {'rdonly': True},
        }

        super().__init__()
