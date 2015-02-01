#!/usr/bin/env python
# Copyright (C) 2014-2015 Thomas Huang
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from db.query.select import SelectQuery
from db.query.base import Query
from db.query.expr import Expr
from db.query.update import UpdateQuery
from db.query.insert import InsertQuery
from db.query.delete import DeleteQuery

class Dialect(object):

    def __init__(self, db=None):
        self._identifier = '"'
        self.db = db
        self.initialize()

    def initialize(self):
        pass

    def select(self, table):
        return SelectQuery(table, self, self.db)

    def update(self, table):
        return UpdateQuery(table, self, self.db)

    def insert(self, table):
        return InsertQuery(table, self, self.db)

    def delete(self, table):
        return DeleteQuery(table, self, self.db)

    def escape(self):
        pass

    def quote(self, value):
        if not value:
            return 'NULL'
        elif value == True:
            return "'1'"
        elif value == False:
            return "'0'"
        elif isinstance(value, Query):
            if isinstance(value, SelectQuery):
                return '(' + value.compile() + ')'
            elif isinstance(value, Expr):
                return value.compile()
            else:
                return self.quote(value)
        elif isinstance(value, list):
            return '(' + ', '.join([self.quote(_) for _ in vlaue]) + ')'
        else:
            return str(value)
        return self.escape(value)

    def quote_column(self, column):
        alias = None
        escaped_identifier = self._identifier + self._identifier
        if isinstance(column, list):
            column, alias = column
            alias = alias.replace(self._identifier, escaped_identifier)

        if isinstance(column, Query):
            column = '(' + column.compile() + ')'
        elif isinstance(column, Expr):
            column = column.compile(self)
        else:
            column = str(column)
            column = column.replace(self._identifier, escaped_identifier)
            if column == '*':
                return column
            elif column.find('.') != -1:
                parts = column.split('.')
                _parts = []
                for part in parts:
                    if part != '*':
                        _parts.append(self._identifier + part + self._identifier)
                    else:
                        _parts.append(part)
                column = '.'.join(_parts)
            elif 'as' not in column.lower():
                column = self._identifier + column + self._identifier

        if alias:
            column += ' AS ' + self._identifier + alias + self._identifier
        return column

    def quote_table(self, table):
        alias = None
        escaped_identifier = self._identifier + self._identifier
        if isinstance(table, list):
            table, alias = table
            alias = alias.replace(self._identifier, escaped_identifier)
        if isinstance(table, Query):
            table = '(' + table.compile() + ')'

        elif isinstance(table, Expr):
            table = table.compile()
        else:
            table = table.replace(self._identifier, escaped_identifier)
            if table.find('.') != -1:
                parts = table.split('.')
                parts  = [self._identifier + part + self._identifier for part in parts]
                table = '.'.join(parts)
            else:
                table = self._identifier + table + self._identifier

        if alias:
            table += ' AS ' + self._identifier  + alias + self._identifier

        return table

    def quote_identifier(self, value):
        escaped_identifier = self._identifier + self._identifier

        if isinstance(value, list):
            value, alias = value
            alias = alias.replace(self._identifier, escaped_identifier)
        if isinstance(value, Query):
            value = '(' + value.compile() + ')'

        elif isinstance(value, Expr):
            value = value.compile()
        else:
            value = value.replace(self._identifier, escaped_identifier)
            if value.find('.') != -1:
                parts = value.split('.')
                parts  = [self._identifier + part + self._identifier for part in parts]
                value = '.'.join(parts)
            else:
                value = self._identifier + value + self._identifier
        if alias:
            value += ' AS ' + self._identifier + alias + self._identifier

        return value

    def map_condition_operator(self, operator):
        return None