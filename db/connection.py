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
    """Base Database Connection class

    :param db_options: db optional configuration, defaults to None
    :type db_options: dict, optional
    """

    def __init__(self, db_options=None):
        db_options = db_options or {}

        #: database optional configuration, defaults to None
        self._db_options = self.default_options()
        self._db_options.update(db_options)

        #: database real connection
        self._connect = None
        self.initialize()

    def initialize(self):
        """Initialize customize configuration in  subclass"""
        pass

    def default_options(self):
        """Defalut options for intailize sql connection"""
        return {}

    def connect(self):
        """connects database"""
        raise NotImplementedError('Must implement connect in Subclass')

    def close(self):
        """Close connect"""
        if self._connect is not None:
            self._connect.close()
            self._connect = None

    def ensure_connect(self):
        """Ensure the connetion is useable"""
        raise NotImplementedError('Must implement ensure_connect in Subclass')

    def cursor(self, as_dict=False):
        """Gets the cursor by type ,  if ``as_dict is ture, make a dict  sql connection cursor"""
        self.ensure_connect()
        ctype = self.real_ctype(as_dict)
        return self._connect.cursor(ctype)

    def real_ctype(self, as_dict):
        """The real sql cursor type"""
        raise NotImplementedError('Must implement real_ctype in Subclass')

    def driver(self):
        """Get database driver"""
        return None

    def commit(self):
        """Commit batch execute"""
        self._connect.commit()

    def rollback(self):
        """Rollback database process"""
        self._connect.rollback()

    def autocommit(self, enable=True):
        """Sets commit to auto if True"""
        self._connect.autocommit(enable)
