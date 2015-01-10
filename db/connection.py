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


class Connection(object):

    def __init__(self, db_options={}):
        self._db_options = self.default_options()
        self._db_options.update(db_options)
        self._connect = None
        self.initialize()
        
    def initialize(self):
        """Initialize Custom config in your Subclass"""
        pass

    def default_options(self):
        return {}

    def connect(self):
        raise NotImplemented('Must implement connect in Subclass')

    def close(self):
        if self._connect is not None:
            self._connect.close()
            self._connect = None

    def ensure_connect(self):
        raise NotImplemented('Must implement ensure_connect in Subclass')

    def cursor(self, as_dict=False):
        self.ensure_connect()
        ctype = self.real_ctype(as_dict)
        return self._connect.cursor(ctype)

    def real_ctype(self, as_dict):
        raise NotImplemented('Must implement real_ctype in Subclass')

    def driver(self):
        return  None

    def commit(self):
        self._connect.commit()

    def rollback(self):
        self._connect.rollback()

    def autocommit(self, enable=True):
        self._connect.autocommit(enable)
