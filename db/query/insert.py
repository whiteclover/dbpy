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

from db.query.base import Query


class InsertQuery(Query):

    def __init__(self, table, dialect, db, columns=[]):
        self._columns = columns or []
        self._values = []
        self._table = table
        self._db = db
        Query.__init__(self, dialect)

    def table(self, table):
        self._table = table
        return self

    def fields(self, *columns):
        self._columns.extend(columns)
        return self

    def values(self, values):
        """The values for insert , 
            it can be a dict row or list tuple row.
        """
        if isinstance(values, dict):
            l = []
            for column in self._columns:
                l.append(values[column])
            self._values.append(tuple(l))
        else:
            self._values.append(values)
        return self

    def compile(self):
        sql = 'INSERT INTO ' + self.dialect.quote_table(self._table)
        if self._columns:
            sql += ' (' + ', '.join([self.dialect.quote_column(_) for _ in self._columns]) + ')'
        sql += ' VALUES(' + ', '.join(['%s' for _ in range(len(self._values[0]))]) + ')'
        return sql

    def execute(self):
        bind = self._values[0] if len(self._values) == 1 else self._values
        return self._db.execute(self.to_sql(), bind)

    def clear(self):
        self._columns = []
        self._values = []
        return self
