#!/usr/bin/env python3

"""Document description."""

__version__ = '0.0.1'
__author__ = 'hharutyunyan'
__copyright__ = 'Copyright 2018, hharutyunyan'
__license__ = 'All Rights Reserved'
__maintainer__ = 'hharutyunyan'
__status__ = "Production"

import json
from typing import Any, Iterable
from app import db
from psycopg2.extras import NamedTupleCursor


class DataView:
    """ Main class for database operations and data representation.

    """

    def __init__(self):
        self.link = db
        self.joins = []
        self.join_fields = []
        self.result = None

        self.update_fields()

        super().__init__()

    def column_name(self, key: str) -> str:
        """ Generate full column name (with alias if specified)

        Parameters
        ----------
        key : str
            Column name from mapping

        Returns
        -------
        str

        """
        if "alias" in self.fields[key]:
            return "{}.{} AS {}".format(self.table_name, key,
                                        self.fields[key]["alias"])
        return "{}.{}".format(self.table_name, key)

    def __encode_objects(self, key: str, value) -> str:
        """ Encode field flagged by "json"

        Parameters
        ----------
        key : str
            Column name from mapping
        value : variant
            Variant value

        Returns
        -------
        str
            JSON encoded string

        """
        # two ways from here: either json dumps you, either you're going back
        # with empty hands
        if self.fields[key].get('json', False) is True:
            return json.dumps(value, default=self.__date_handler)
        return value

    @staticmethod
    def __date_handler(obj: object) -> object:
        """ Generic method for handling the data during JSON encoding/decoding

        Parameters
        ----------
        obj : object

        Returns
        -------
        object
            Formatted date object or the same object

        """
        return obj.isoformat() if hasattr(obj, 'isoformat') else obj

    def join(self, table: str, on: str, fields: list, jtype: str = 'LEFT'):
        """ Add join statements

        Parameters
        ----------
        table : str
            Name of the table to join with
        on : str
            Join conditions
        fields : list
            Fields to be included
        jtype : str
            Join type eg.: LEFT, RIGHT, INNER

        """
        self.joins.append(" ".join((jtype.upper(), "JOIN", table, "ON", on)))
        self.join_fields.extend(fields)

    def clear_joins(self):
        """ Remove all previously specified joins

        """
        self.joins = []
        self.join_fields = []

    def clear(self):
        """ Clear SQL results

        """
        if self.result is not None:
            self.result.close()
            self.result = None

    def begin(self):
        """ Begin SQL transaction

        """
        self.link.transaction = True

    def commit(self):
        """ Commit previously begun SQL transaction

        """
        self.link.commit()

    def rollback(self):
        """ Rollback previously begun SQL transaction

        """
        self.link.rollback()

    def lock(self):
        """ Acquire lock on the current table

        """
        return self.link.execute('LOCK TABLE {}'.format(self.table_name))

    def select(self, where: str = '', values: dict = {}, group_by: str = '',
               order_by: str = '', limit: int = -1, offset: int = -1,
               count: bool = False, lock: bool = False) -> Iterable:
        """ Wrapper for SQL SELECT statement
        """
        query_tail = []
        if len(group_by) > 0:
            query_tail.append('GROUP BY %s' % group_by)
        if len(order_by) > 0:
            query_tail.append('ORDER BY %s' % order_by)
        if limit > 0:
            query_tail.append('LIMIT %(limit)s')
            values['limit'] = limit
        if offset > 0:
            query_tail.append('OFFSET %(offset)s')
            values['offset'] = offset
        if lock is True:
            query_tail.append('FOR UPDATE')
        if len(where) == 0:
            where = True

        fields = self.attr_list + self.join_fields

        if count:
            fields += ['count(*) OVER () as all_count']

        query = self.link.select % (", ".join(fields), self.table_name,
                                    " ".join(self.joins),
                                    where, " ".join(query_tail))

        self.result = self.link.execute(query, values)
        return self.result

    def find(self, where: str = '', values: dict = {}, order_by: str = '',
             lock: bool = False) -> object:
        """ Selects only one row with specified conditions
        """
        res = self.select(where, values, '', order_by, 1, lock=lock).fetchone()
        self.clear()
        return res

    def insert(self, values: dict) -> Any:
        """ Wrapper for SQL INSERT statement
        """
        values = {key: self.__encode_objects(key, values[key])
                  for key in values if key in self.fields}
        field_list = {key: "%%(%s)s" % key
                      for key in values if key in self.fields and
                      self.fields[key].get("rdonly", False) is False}

        query_tail = ''
        if len(field_list) == 0:
            return False

        query = self.link.insert % \
                (self.table_name, ", ".join(field_list.keys()),
                 ", ".join(field_list.values()), query_tail)

        self.result = self.link.execute(query, values)
        if self.result is None or self.result.rowcount != 1:
            return False

        res = self.result.rowcount

        self.clear()

        return res

    def update(self, values: dict, where=True, condition: dict = {}) -> Any:
        """ Wrapper for SQL UPDATE statement
        """
        values = {key: self.__encode_objects(key, values[key])
                  for key in values if key in self.fields}
        field_list = ["%s=%%(%s)s" % (key, key)
                      for key in values if key in self.fields and
                      self.fields[key].get("rdonly", False) is False]

        if len(field_list) == 0:
            return False

        query_tail = ''
        
        values = dict(list(values.items()) + list(condition.items()))

        query = self.link.update % \
                (self.table_name, ", ".join(field_list), where, query_tail)

        self.result = self.link.execute(query, values)

        # if no rows affected return false
        if self.result is None or self.result.rowcount < 1:
            return False

        res = self.result.fetchone()[0] if query_tail else self.result.rowcount
        self.clear()
        return res

    def truncate(self) -> Iterable:
        """ Truncates the table

        """
        return self.link.execute("TRUNCATE {}".format(self.table_name))

    def delete(self, where=True, values: dict = {}) -> int:
        """ Wrapper for SQL UPDATE statement
        """
        query = self.link.delete % (self.table_name, where)

        self.result = self.link.execute(query, values)
        if self.result is None or self.result.rowcount == 0:
            return False

        count = self.result.rowcount
        self.clear()
        return count

    def all(self, where: str = '', values: dict = {}, group_by: str = '',
            order_by: str = '', limit: int = -1, offset: int = -1) -> object:
        """ Select all records
        """
        result = self.select(where, values, group_by, order_by, limit,
                             offset).fetchall()
        self.clear()
        return result

    def throw(self, message: str):
        """ Wrapper for Exception raising
        """
        raise Exception("DB error [{}]".format(message))

    def create_table(self, name: str, fields: list, indexes: dict = {}):
        """ Creates a table by specified definitions
        """
        if len(fields) == 0:
            return False

        # iterate through fields
        ps = []
        for field in fields:
            ps.append(self._field_sql(field))

        # iterate through indexes
        for index in indexes:
            ps.append(self._index_sql(index))

        # iterate through indexes
        q = 'CREATE TABLE {} ({})'.format(name, ','.join(ps))
        return self.link.execute(q)

    def alter_table(self, name: str, fields: list, type: str = None) -> bool:
        if len(fields) == 0:
            return False

        q = 'ALTER TABLE {} {} {}'
        if len(fields) == 1:
            self.link.execute(q.format(name, 'ADD COLUMN',
                                       self._field_sql(fields[0])))
        elif len(fields) == 2:
            if fields[0] != fields[1]:
                self.link.execute(q.format(
                    name, 'RENAME COLUMN',
                    '{} TO {}'.format(fields[0], fields[1])))
            if type:
                self.link.execute(q.format(
                    name, 'ALTER COLUMN',
                    '{0} TYPE {1} USING ({0}::{1})'.format(fields[1], type)))

        return True

    def rename_table(self, name: str, new_name: str):
        return self.link.execute('ALTER TABLE {} RENAME TO {}'.format(
            name, new_name))

    def drop(self, table: str, field: str = None):
        if field is None:
            return self.link.execute('DROP TABLE {} CASCADE'.format(table))
        else:
            return self.link.execute(
                'ALTER TABLE {} DROP COLUMN {}'.format(table, field))

    @staticmethod
    def _field_sql(field_def):
        # name:type:not_null:ai
        # first_name:varchar(100):1

        _def = field_def.split(':')
        return '{} {} {} {}'.format(
            _def[0], _def[1], 'NOT NULL' if _def[2] == '1' else '',
            'DEFAULT {}'.format(_def[3]) if len(_def) > 3 else '')

    @staticmethod
    def _index_sql(index_def):
        # name:type
        _def = index_def.split(':')
        return ' {} KEY ({})'.format(_def[1], _def[0])

    def create_trigger(self, trigger_name: str, table_name: str,
                       function_name: str, when: str, events: list,
                       each: str = None, condition: str = None,
                       arguments: list = {}):
        self.link.execute(
            "CREATE TRIGGER {} {} {} ON {} {} {} EXECUTE PROCEDURE \
            {}({})".format(
                trigger_name, when, ' OR '.join(events), table_name,
                'FOR EACH {}'.format(each) if each else '',
                'WHEN ({})'.format(condition) if condition else '',
                function_name,
                ', '.join(arguments) if len(arguments) > 0 else ''))

    def update_fields(self, fields=None):
        if fields is not None:
            self.fields = fields

        # set default options to the fields if options are None
        for key in self.fields:
            if self.fields[key] is None:
                self.fields[key] = {}
        self.attr_list = list(map(self.column_name, self.fields))
