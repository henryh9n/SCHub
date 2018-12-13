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


class Projects(Model):
    """ Class for defining the structure for projects.

    """

    def __init__(self):
        self.table_name = 'projects'
        self.fields = {
            'id': {'rdonly': True},
            'name': None,
            'description': None,
            'owner': None,
            'status': None,
            'date_added': {'rdonly': True},
        }

        super().__init__()

    def create(self, name, description):
        """Method to create a new project."""
        data = {
            'name': name,
            'description': description,
            'owner': g.user.id
        }
        return self.add(data)

    def get_top_projects(self, user_id: int, limit: int = 4, page: int = 1):
        """Get the projects with most contributions."""
        self.attr_list.append('COUNT(*) AS count')
        self.join('revisions', 'id=project_id', ['project_id'])
        res = self.select_page('contributor_id=%(user_id)s',
                               {'user_id': user_id}, group_by='id',
                               order_by='count DESC', limit=limit, page=page)
        self.clear()
        return res
