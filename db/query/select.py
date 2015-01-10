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
from db.errors import DBError
from db.query import LOGGER


class QueryCondition(object):

    def __init__(self, glue):
        self.glue = glue
        self.conditions = []
        self.changed = True

        self.bind = []

    def __nonzero__(self):
        return bool(len(self.conditions))
    __bool__ = __nonzero__

    def where(self, fields, snippet):
        self.conditions.append(dict(
            field=fields,
            value=snippet,
            op=None
        ))
        self.changed = True
        return self

    def __len__(self):
        return len(self.conditions)

    def condition(self, field, value=None, op=None):
        if not op:
            if isinstance(value, (list, tuple)):
                op = 'IN'
            elif value is None:
                op = 'IS NULL'
            else:
                op = '='
        self.conditions.append(dict(
            field=field,
            value=value,
            op=op
        ))
        self.changed = True

        return self

    def is_null(self, field):
        return self.condition(field)

    def is_not_null(self, field):
        return self.condition(field, None, 'IS NOT NULL')

    def exists(self, select):
        return self.condition('', select, 'EXISTS')

    def not_exists(self, select):
        return self.condition('', select, 'NOT EXISTS')

    def compile(self, db, query_placeholder='%s'):
        if self.changed:
            condition_fragments = []
            #arguments = []
            conditions = [_.copy() for _ in self.conditions]
            glue = self.glue
            self.glue = None

            for condition in conditions:
                is_select = False
                if not condition.get('op'):
                    condition_fragments.append(' (' + condition['field'] + ') ')
                else:
                    field = condition['field']
                    if isinstance(field, QueryCondition):
                        field.compile(db)
                        if len(condition) == 1:
                            condition_fragments.append(field.to_sql())
                        else:
                            condition_fragments.append(
                                ' (' + field.to_sql() + ') ')
                            self.bind.extend(field.bind)
                    else:
                        operator_defaults = dict(
                            prefix='',
                            postfix='',
                            delimiter='',
                            op=condition['op'],
                            use_value=True)
                        op = db.map_condition_operator(condition['op'])
                        if not op:
                            op = self.map_condition_operator(
                                condition['op'])
                        operator_defaults.update(op)
                        op = operator_defaults
                        placeholders = []
                        if isinstance(condition['value'], SelectQuery):
                            is_select = True
                            condition['value'].compile(
                                db, query_placeholder)
                            placeholders.append(condition['value'].to_sql())
                            self.bind.extend(condition.bind)
                            op['use_value'] = False
                        elif not op.get('delimiter'):
                            condition['value'] = [condition['value']]

                        if op.get('use_value'):
                            for value in condition['value']:
                                if isinstance(value, list):
                                    placeholders.append(
                                        ', '.join(['%s'] * len(value)))
                                    self.bind.extend(value)
                                else:
                                    self.bind.append(value)
                                    placeholders.append('%s')

                        if is_select:
                            LOGGER.deubg('select :' + db.quote_column(condition['field']))
                            condition_fragments.append(' (' +
                                db.quote_column(condition['field']) + ' ' +
                                op['op'] + ' ' + op['prefix'] + 
                                op['delimiter'].join(placeholders) + op['postfix'] + ') ')
                        else:
                            condition_fragments.append(' ' +
                                db.quote_column(condition['field']) + ' ' +
                                op['op'] + ' ' + op['prefix'] + 
                                op['delimiter'].join(placeholders) + op['postfix'] + ' ')

            self.changed = False
            self.string_version = glue.join(condition_fragments)

    def to_sql(self):
        if self.changed:
            return ''
        return self.string_version
    __str__ = to_sql

    def map_condition_operator(self, op):
        specials = {
            'BETWEEN': {'delimiter': ' AND '},
            'IN': {'delimiter': ', ', 'prefix': ' (', 'postfix': ') '},
            'NOT IN': {'delimiter': ', ', 'prefix': ' (', 'postfix': ')'},
            'EXISTS': {'prefix': ' (', 'postfix': ') '},
            'NOT EXISTS': {'prefix': ' (', 'postfix': ') '},
            'IS NULL': {'use_value': False},
            'IS NOT NULL': {'use_value': False},
            'LIKE': {},
            'NOT LIKE': {},
            '=': {},
            '<': {},
            '>': {},
            '>=': {},
            '<=': {}
        }
        if specials.get(op):
            result = specials.get(op)
        else:
            op = op.upper()
            result = specials.get(op) if specials.get(op) else {}

        result['op'] = op
        return result


class WhereQuery(Query):

    def __init__(self, dialect):
        self._where = QueryCondition('AND')
        self._order_by = []
        self._limit = None

        self.bind = []

        Query.__init__(self, dialect)

    def where(self, snippet, args):
        self._where.where(snippet, args)
        return self

    def condition(self, field, value=None, operator=None):
        self._where.condition(field, value, operator)
        return self

    def conditions(self):
        return self._where.conditions()

    def arguments(self):
        return self._where.arguments()

    def is_null(self, field):
        self._where.is_null(field)
        return self

    def is_not_null(self, field):
        self._where.is_not_null(field)
        return self

    def exists(self, query):
        self._where.exists(query)
        return self

    def not_exists(self, query):
        self._where.not_exists(query)
        return self

    def order_by(self, column, direction=''):
        self._order_by.append((column, direction))
        return self

    def limit(self, limt):
        self._limit = limt
        return self

    def compile_condition(self, condition):
        condition.compile(self.dialect, self)
        sql = condition.to_sql()
        self.bind.extend(condition.bind)
        return sql

    def compile_set(self, values):
        sets = []
        for column, value in values:
            column = self.dialect.quote_column(column)
            self.bind.append(value)
            sets.append(column + ' = ' + '%s')

        return ', '.join(sets)

    def compile_group_by(self, columns):
        group = []
        for column in columns:
            column = self.dialect.quote_identifier(column) if isinstance(column, list) else \
                self.dialect.quote_column(column)
            group.append(column)

        return 'GROUP BY ' + ', '.join(group)

    def compile_order_by(self, columns, direction=''):
        sorts = []
        for column, direction in columns:
            column = self.dialect.quote_identifier(column) if isinstance(column, list) else \
                self.dialect.quote_column(column)
            if direction:
                direction = ' ' + direction.upper()
            sorts.append(column + direction)
        return 'ORDER BY ' + ', '.join(sorts)


    def clear(self):
        self._where = QueryCondition('AND')
        self._order_by = []
        self._limit = None
        self.bind = []



class SelectQuery(WhereQuery):

    def __init__(self, table, dialect, db, columns=None):

        self._select = []
        self._distinct = False

        self._from = [table]
        self._group_by = []
        self._offset = []

        self._select = columns or []
        self._db = db
        WhereQuery.__init__(self, dialect)

    def execute(self, many=None, as_dict=False):
        return self._db.query(self.to_sql(), self.bind, many=many, as_dict=as_dict)

    def distinct(self, distinct=True):
        self._distinct = distinct
        return self

    def select(self, *columns):
        self._select.extend(columns)
        return self

    fields = select

    def fram(self, tables):
        self._from.extend(tables)
        return self

    def group_by(self, *columns):
        self._group_by.extend(columns)
        return self

    def offset(self, offset):
        self._offset = offset
        return self

    def compile(self):
        quote_column = self.dialect.quote_column
        quote_table = self.dialect.quote_table

        sql = 'SELECT '
        if self._distinct:
            sql += 'DISTINCT '
        if not self._select:
            sql += '*'
        else:
            sql += ', '.join([quote_column(_) for _ in self._select])

        if self._from:
            sql += ' FROM ' + ', '.join([quote_table(_) for _ in self._from])

        if self._where:
            sql += '\nWHERE ' + self.compile_condition(self._where)

        if self._group_by:
            sql += '\n' + self.compile_group_by(self._group_by)

        if self._order_by:
            sql += '\n' + self.compile_order_by(self._order_by)
        if self._limit:
            sql += '\nLIMIT ' + str(self._limit)

        if self._offset:
            sql += ' OFFSET ' + str(self._offset)
        return sql

    def clear(self):
        self._select = []
        self._distinct = False
        self._from = []
        self._join = []
        self._group_by = []
        self._offset = []
        self._where = QueryCondition('AND')
        self._last_join = None
        self._limit = None
        self._offset = None