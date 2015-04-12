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

import threading
import logging
from db.errors import DBError
import time


LOGGER = logging.getLogger('db.pool')

class BaseConnectionPool(object):

    def __init__(self, minconn, maxconn, connection_cls, db_options={}):
        self.db_options = db_options
        self.maxconn = maxconn
        self.minconn = minconn if self.maxconn > minconn else int(self.maxconn * 0.2)
        if not connection_cls:
            raise ValueError('Must be Connection subclass')
        self.connection_cls = connection_cls

    def new_connect(self):
        return self.connection_cls(self.db_options)

    def push(self, con):
        pass

    def pop(self):
        pass

    def release(self):
        pass


class ConnectionPool(BaseConnectionPool):

    def __init__(self, minconn=3, maxconn=10,connection_cls=None, db_options={}):
        self._created_conns = 0
        BaseConnectionPool.__init__(self, minconn, maxconn, connection_cls, db_options)
        self._lock = threading.Lock()
        self._available_conns = []
        self._in_use_conns = []
        for i in range(self.minconn):
            self._available_conns.append(self.new_connect())

    def pop(self):
        con = None
        first_tried = time.time()
        while True:
            self._lock.acquire()
            try:
                con = self._available_conns.pop(0)
                self._in_use_conns.append(con)
                break
            except IndexError:

                if self._created_conns < self.maxconn:

                    self._created_conns += 1
                    con = self.new_connect()
                    self._in_use_conns.append(con)
                    break
            finally:
                self._lock.release()

            if not con and 3 <= (time.time() - first_tried):
                raise DBPoolError("tried 3 seconds, can't load connection, maybe too many threads")

        return con

    def push(self, con):
        self._lock.acquire()
        if con in self._in_use_conns:
            self._in_use_conns.remove(con)
            self._available_conns.append(con)
        self._lock.release()

    def release(self):
        with self._lock:
            for conn in self._available_conns:
                conn.close()
            for conn in self._in_use_conns:
                conn.close()
            self._available_conns[:] = []
            self._in_use_conns[:] = []
            self._created_conns = 0


class DBPoolError(DBError): pass
