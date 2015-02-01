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

import sys
import logging
from db.errors import DBError
import time
from db.pool import ConnectionPool

LOGGER = logging.getLogger('db')

class DB(object):

    adapters = {}
    dialects = {}

    def __init__(self, config, minconn=5, maxconn=10, key='defalut', adapter='mysql'):
        """ Setup DB::

        param config dict: is the db adapter config
        param key string: the key to identify dabtabase
        param adapter string: the dabtabase adapter current support mysql only
        param minconn int: the min connection for connection pool
        param maxconn int: the max connection for connection pool

        """
        adapter = adapter or 'mysql'
        self.key = key
        self.adapter = adapter
        self.pool = ConnectionPool(minconn, maxconn, self.connection_class(adapter), config)
        self.dialect = self.dialect_class(adapter)(self)

    def select(self, table):
        return self.dialect.select(table)

    def insert(self, table):
        return self.dialect.insert(table)

    def update(self, table):
        return self.dialect.update(table)

    def delete(self, table):
        return self.dialect.delete(table)

    def query(self, sql, args=None, many=None, as_dict=False):
        """The connection raw sql query,  when select table,  show table
            to fetch records, it is compatible the dbi execute method::

        args:
        sql string: the sql stamtement like 'select * from %s'
        args maybe list: Wen set None, will use dbi execute(sql), else
            dbi execute(sql, args), the args keep the original rules, it shuld be tuple or list of list
        many maybe int: when set, the query method will return genarate an iterate
        as_dict bool: when is true, the type of row will be dict, otherwise is tuple
        """
        con = self.pool.pop()
        c = None
        try:
            c = con.cursor(as_dict)
            LOGGER.debug("Query sql: " + sql + " args:" + str(args))
            c.execute(sql, args)
            if many and many > 0:
                return self._yield(con, c, many)
            else:
                return c.fetchall()

        except Exception as e:
            LOGGER.error("Error Qeury on %s", str(e))
            raise DBError(e.args[0], e.args[1])
        finally:
            many or (c and c.close())
            many or (con and self.pool.push(con))

    def _yield(self, con, cursor , many):
        try:
            result = cursor.fetchmany(many)
            while result:
                for row in result:
                    yield row
                result = cursor.fetchmany(many)
        finally:
            cursor and cursor.close()
            con and self.pool.push(con)

    def execute(self, sql, args=None):
        """It is used for update, delete records::

            execute('insert into users values(%s, %s)', [(1L, 'blablabla'), (2L, 'animer')])
            execute('delete from users')
        """
        con = self.pool.pop()
        c = None
        try:
            c = con.cursor()
            LOGGER.debug("Execute sql: " + sql + " args:" + str(args))
            if type(args) is tuple:
                c.execute(sql, args)
            elif type(args) is list:
                if len(args) > 1 and type(args[0]) in (list, tuple):
                    c.executemany(sql, args)
                else:
                    c.execute(sql, args)
            elif args is None:
                c.execute(sql)
            if sql.lstrip()[:6].upper() == 'INSERT':
                return c.lastrowid
            return c.rowcount
        except Exception as e:
            LOGGER.error("Error Execute on %s", str(e))
            raise DBError(str(e))
        finally:
            c and c.close()
            con and self.pool.push(con)


    def transaction(self):
        return Transaction(self)

    def connection_class(self, adapter):
        if self.adapters.get(adapter):
            return self.adapters[adapter]
        try:
            class_prefix = getattr(
                __import__('db.' + adapter, globals(), locals(),
                           ['__class_prefix__']),  '__class_prefix__')
            driver = self._import_class('db.' + adapter + '.connection.' +
                                  class_prefix + 'Connection')
        except ImportError:
            raise DBError("Must install adapter `%s` or doesn't support" %
                          (adapter))

        self.adapters[adapter] = driver
        return driver

    def dialect_class(self, adapter):
        if self.dialects.get(adapter):
            return self.dialects[adapter]
        try:
            class_prefix = getattr(
                __import__('db.' + adapter, globals(), locals(),
                            ['__class_prefix__']),  '__class_prefix__')
            driver = self._import_class('db.' + adapter + '.dialect.' + 
                                     class_prefix + 'Dialect')
        except ImportError:
            raise DBError("Must install adapter `%s` or doesn't support" %
                          (adapter))

        self.dialects[adapter] = driver
        return driver

    def _import_class(self, module2cls):
        d = module2cls.rfind(".")
        classname = module2cls[d + 1: len(module2cls)]
        m = __import__(module2cls[0:d], globals(), locals(), [classname])
        return getattr(m, classname)


class lazy_attr(object):

    def __init__(self, wrapped):
        self.wrapped = wrapped
        try:
            self.__doc__ = wrapped.__doc__
        except: # pragma: no cover
            pass

    def __get__(self, inst, objtype=None):
        if inst is None:
            return self
        val = self.wrapped(inst)
        setattr(inst, self.wrapped.__name__, val)
        return val

class Transaction(object):

    def __init__(self, db):
        self._db = db
        self._con = None

    @lazy_attr
    def dialect(self):
        return self._db.dialects.get(self._db.adapter)(self)

    def __enter__(self):
        self._con = self._db.pool.pop()
        self._con.ensure_connect()
        self._con.autocommit(False)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self._con.commit()
            self._con.autocommit(True)
        except Exception as e:
            err_trace = sys.exc_info()[2]
            try:
                self._con.rollback()
            except Exception as e_:
                LOGGER.error('When transaction happend error: %s', e_)
            raise e, None, err_trace
        finally:
            self._db.pool.push(self._con)
            self._con = None
            self._db = None

    def begin(self):
        self._con = self._db.pool.pop()
        self._con.ensure_connect()
        self._con.autocommit(False)

    def commit(self):
        try:
            self._con.commit()
            self._con.autocommit(True)
        except Exception as e:
            err_trace = sys.exc_info()[2]
            try:
                self._con.rollback()
            except Exception as e_:
                LOGGER.error('When transaction happend error: %s', e_)
            raise e, None, err_trace
        finally:
            self._db.pool.push(self._con)
            self._con = None
            self._db = None

    def execute(self, sql, args):
        c = None
        try:
            c = self._con.cursor()
            LOGGER.debug("execute sql: " + sql + " args:" + str(args))
            if type(args) is tuple:
                c.execute(sql, args)
            elif type(args) is list:
                if len(args) > 1 and type(args[0]) in (list, tuple):
                    c.executemany(sql, args)
                else:
                    c.execute(sql, args)
            elif args is None:
                c.execute(sql)
            if sql.lstrip()[:6].upper() == 'INSERT':
                return c.lastrowid
            return c.rowcount
        finally:
            c and c.close()

    def insert(self, table):
        return self.dialect.insert(table)

    def update(self, table):
        return self.dialect.update(table)

    def delete(self, table):
        return self.dialect.delete(table)
