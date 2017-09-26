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

from db.connection import Connection
from db.errors import (
    NotInstallDriverError,
)

try:
    import MySQLdb
    from MySQLdb.cursors import DictCursor, Cursor
except ImportError:
    raise NotInstallDriverError("Must install MySQLdb module fistly")


import time
import logging

LOGGER = logging.getLogger('db.mysql')


class MySQLConnection(Connection):

    def initialize(self):
        self._last_used = time.time()
        self._max_idle = self._db_options.pop('max_idle', 10)

    def default_options(self):
        return {
            'port': 3306,
            'host': 'localhost',
            'user': 'test',
            'passwd': 'test',
            'db': 'test',
            'use_unicode': True,
            'charset': 'utf8'
        }

    def connect(self):
        self.close()
        self._connect = MySQLdb.connect(**self._db_options)
        self._connect.autocommit(True)

    def ensure_connect(self):
        if not self._connect or self._max_idle < (time.time() - self._last_used):
            try:
                self._connect.ping()
            except:
                self.connect()
        self._last_used = time.time()

    def real_ctype(self, as_dict=False):
        if as_dict:
            return DictCursor
        return Cursor

    def driver(self):
        return 'mysql'
