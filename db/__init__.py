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

__version__ = '0.1.2'
VERSION = tuple(map(int, __version__.split('.')))



__all__ = [
    'and_',
    'or_',
    'expr',
    'query',
    'execute',
    'transaction',
    'setup',
    'select',
    'insert',
    'update',
    'delete',
    'database',
    'DBError'
]

from db.query.select import QueryCondition
from db.query.expr import Expr as expr
from db._db import DB
from db.errors import DBError
from random import choice

def and_():
    return QueryCondition('AND')


def or_():
    return QueryCondition('OR')


__db = {}


def setup(config,  minconn=5, maxconn=10,  adapter='mysql', key='default', slave=False):
    global __db

    if '.' in key:
        raise TypeError('The DB Key: "%s" Can\'t Contain dot' %(key))

    if slave == False and key in __db:
        raise DBError('The Key: "%s" was set' %(key))

    database = DB(config, minconn, maxconn, key, adapter)

    master_key = key
    slave_key = key + '.slave'

    if not slave:
        __db[master_key] = database
        if slave_key not in __db:
            __db[slave_key] = [database]
    else:
        if key in __db:
            databases = __db[slave_key]
            if len(databases) == 1 and __db[master_key] == databases[0]:
                __db[slave_key] = [database]
            else:
                __db[slave_key].append(database)
        else:
            __db[slave_key] = [database]

def query(sql, args=None, many=None, as_dict=False, key='default'):
    """The connection raw sql query,  when select table,  show table
        to fetch records, it is compatible the dbi execute method::

    args::

    sql string: the sql stamtement like 'select * from %s'
    args maybe list: Wen set None, will use dbi execute(sql), else
        dbi execute(sql, args), the args keep the original rules, it shuld be tuple or list of list
    many maybe int: when set, the query method will return genarate an iterate
    as_dict bool: when is true, the type of row will be dict, otherwise is tuple
    key: a key for your dabtabase you wanna use
    """
    database = choice(__db[key + '.slave'])
    return database.query(sql, args, many, as_dict)


def execute(sql, args=None, key='default'):
    """It is used for update, delete records::

        execute('insert into users values(%s, %s)', [(1L, 'blablabla'), (2L, 'animer')])
        execute('delete from users')
    """
    database = __db[key]
    return database.execute(sql, args)


def transaction(key='default'):
    database = __db[key]
    return database.transaction()


def select(table, key='default'):
    database = choice(__db[key+'.slave'])
    return database.select(table)


def insert(table, key='default'):
    database = __db[key]
    return database.insert(table)


def update(table, key='default'):
    database = __db[key]
    return database.update(table)


def delete(table, key='default'):
    database = __db[key]
    return database.delete(table)


def database(key='default', slave=False):
    if slave:
        key += '.slave'
        return choice(__db[key])
    return __db.get(key)
