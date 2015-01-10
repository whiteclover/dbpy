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

    def __init__(self, table, dialect, db,):
        if table:
            self._table = table
        self._db = db
        WhereQuery.__init__(self, dialect)

    def table(self, table):
        self._table = table
        return self

    def compile(self):
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
        WhereQuery.clear(self)
        self._table = None
        self._parameters = []
        self._sql = None

    def execute(self):
        return self._db.execute(self.to_sql(), self.bind)
