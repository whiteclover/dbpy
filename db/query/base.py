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


class Query(object):
    """Base Sql Query class"""

    def __init__(self, dialect):
        """The sql dialect for building sql"""
        self.dialect = dialect

    def close(self):
        """Reset the dialect to none"""
        self.dialect = None

    def __del__(self):
        self.close()

    def to_sql(self):
        """Generates the sql statement"""
        return self.compile()

    def compile(self):
        """Comile the sql statement"""
        raise NotImplementedError("Implements ``compile`` in subclass...")

    __str__ = to_sql

    def execute(self):
        """excute database sql operator"""
        raise NotImplementedError("Implements ``execute`` in subclass...")
