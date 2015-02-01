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

    def __init__(self, dialect):
        self.dialect = dialect

    def close(self):
        self.dialect = None

    def __del__(self):
        self.close()

    def connect(self):
        pass

    def to_sql(self):
        return self.compile()

    __str__ = to_sql


    def execute(self):
        pass