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

from db.query.select import WhereQuery


class DeleteQuery(WhereQuery):
    """Delete operator query builder"""

    def __init__(self, table, dialect, db):
        """Constructor

        :param table:  table name
        :type table: str
        :param dialect: the sql dialect instance
        :param db: the database connection instance
        """
        if table:
            self._table = table
        self._db = db
        WhereQuery.__init__(self, dialect)

    def table(self, table):
        """Sets table name"""
        self._table = table
        return self

    def compile(self):
        """Compiles the delete sql statement"""
        sql = ''
        sql += 'DELETE FROM ' + self.dialect.quote_table(self._table)
        if self._where:
            sql += ' WHERE ' + self.compile_condition(self._where)
        if self._order_by:
            sql += ' ' + self.compile_order_by(self._order_by)

        if self._limit:
            sql += ' LIMIT ' + self._limit
        return sql

    def clear(self):
        """Clear and reset to orignal state"""
        WhereQuery.clear(self)
        self._table = None
        self._parameters = []
        self._sql = None

    def execute(self):
        """Execute the sql for delete operator"""
        return self._db.execute(self.to_sql(), self.bind)
