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

import unittest
import db
import logging



global config

config = {
        'passwd': 'test',
        'user': 'test',
        'host': 'localhost',
        'db': 'test'
    }


def _create():
    db.execute('DROP TABLE IF EXISTS `users`')
    db.execute("""CREATE TABLE `users` (
                `uid` int(10) unsigned NOT NULL AUTO_INCREMENT,
                `name` varchar(20),
                PRIMARY KEY (`uid`))""")

class TestDBBase(unittest.TestCase):

    def setUp(self):
        setattr(db, '__db', {})

    def test_dup_key(self):
        db.setup(config)
        f = lambda: db.setup(config)
        self.assertRaises(db.DBError, f)

    def test_invalid_key(self):
        f = lambda: db.setup(config, key='dd.xx')

        self.assertRaises(TypeError, f)


    def test_database(self):
        db.setup(config)
        self.assertEqual(db.database(), db.database('default', slave=True))
        conns = getattr(db, '__db', [])
        self.assertEqual(len(conns['default.slave']), 1)

        db.setup(config, slave=True)
        self.assertNotEqual(db.database(), db.database('default', slave=True))
        conns = getattr(db, '__db', [])
        self.assertEqual(len(conns['default.slave']), 1)

        db.setup(config, slave=True)
        conns = getattr(db, '__db', [])
        self.assertEqual(len(conns['default.slave']), 2)

class TestBase(unittest.TestCase):

    def setUp(self):
        setattr(db, '__db', {})
        db.setup(config)
        db.execute('DROP TABLE IF EXISTS `users`')
        db.execute("""CREATE TABLE `users` (
                `uid` int(10) unsigned NOT NULL AUTO_INCREMENT,
                `name` varchar(20) NOT NULL,
                PRIMARY KEY (`uid`))""")

    def test_query(self):
        self.assertEqual(1, db.query('SELECT 1')[0][0])
        self.assertEqual(0, len(db.query('SELECT * FROM users')))

    def test_execute(self):
        res = db.execute('INSERT INTO users VALUES(%s, %s)', [(10, 'execute_test'), (9, 'execute_test')])
        self.assertTrue(res)
        res = db.execute('DELETE FROM users WHERE name=%s', ('execute_test',))
        self.assertEqual(res, 2)

    def test_pool(self):
        import threading

        def q(n):
            for i in range(10):
                res = db.query('select count(*) from  users')
                self.assertEqual(0, res[0][0])
        n = 50
        ts = []
        for i in range(n):
            t = threading.Thread(target=q, args=(i,))
            ts.append(t)
        for t in ts:
            t.start()
        for t in ts:
            t.join()



class TestMultilDB(unittest.TestCase):

    def setUp(self):
        setattr(db, '__db', {})
        db.setup(config, key='test')
        db.setup(config, key='test', slave=True)
        db.execute('DROP TABLE IF EXISTS `users`', key='test')
        db.execute("""CREATE TABLE `users` (
                `uid` int(10) unsigned NOT NULL AUTO_INCREMENT,
                `name` varchar(20) NOT NULL,
                PRIMARY KEY (`uid`))""", key='test')
        rows = []
        for _ in range(1, 10):
            rows.append('(%d , "name_%d")' % (_,  _))
        db.execute('INSERT INTO users VALUES ' + ', '.join(rows), key='test')

    def tearDown(self):
        db.execute('DELETE FROM users', key='test')


    def test_excute(self):
        res = db.execute('insert into users values(%s, %s)', [(10L, 'thomas'), (11L, 'animer')], key='test')
        res = db.query('SELECT count(*) FROM users WHERE uid>=10', key='test')
        self.assertEqual(2, res[0][0])

    def test_query(self):
        res = db.query('select name from users limit 5', key='test')
        self.assertEqual(len(res), 5)
        res = db.query('select name from users limit %s', (100,), many=20, key='test')
        rows = []
        for r in res:
            rows.append(r)
        self.assertTrue(10, len(rows))

class TestSelectQuery(unittest.TestCase):

    def setUp(self):
        setattr(db, '__db', {})
        db.setup(config)
        _create()
        users = []
        for i in range(1, 5):
            users.append((i, 'user_' + str(i)))
        users.append((5, None))
        db.execute('INSERT INTO users VALUES(%s, %s)', users)
        self.select = db.select('users')

    def tearDown(self):
        db.execute('delete from users')


    def test_select_all(self):
        self.assertEquals(len(self.select
            .execute()), 5)


    def test_select_as_dict(self):
        res = self.select.condition('uid', 1).execute(as_dict=True)
        self.assertEqual(len(res), 1)
        self.assertEqual(type(res[0]), dict)
        self.assertEqual(res[0]['uid'], 1)

    def test_select_many(self):
        res = (self.select.fields('*')
               .execute(many=2))
        rows = []
        for row in res:
            rows.append(row)

        self.assertEquals(len(rows), 5)

    def test_select_condition(self):
        res = (self.select
               .condition('name', 'user_1')
               .condition('uid', 1)
               .execute())

        self.assertEquals(res[0][1], 'user_1')

    def test_select_or_condition(self):
        from db import or_
        or_con = or_()
        or_con.condition('name', 'user_1')
        or_con.condition('name', 'user_2')
        res = (self.select
               .condition(or_con)
               .execute())

        self.assertEquals(res[0][1], 'user_1')

    def test_select_like(self):
        res = (self.select
               .condition('name', 'user_%', 'like')
               .execute())
        self.assertEquals(len(res), 4)

    def test_select_in(self):
        res = (self.select.fields('*')
               .condition('name', ['user_1', 'user_2'])
               .execute())
        self.assertEquals(res[0][1], 'user_1')
        self.assertEquals(res[1][1], 'user_2')

    def test_select_group_by(self):
        self.assertEquals(len(self.select
            .group_by('name', 'uid')
            .execute()), 5)

    def test_select_order_by_ASC(self):

        self.assertEquals(len(self.select
            .order_by('name')
            .execute()), 5)

    def test_select_order_by_DESC(self):

        self.assertEquals(len(self.select
            .order_by('name', 'DESC')
            .execute()), 5)
        
    def test_select_limit(self):
      self.assertEquals(len(self.select.limit(2).execute()), 2)

    def test_table_dot_condition(self):
        res = self.select.condition('users.uid', 5).execute()
        self.assertEqual(res[0][0], 5)

    def test_is_null(self):
        res = self.select.is_null('name').condition('uid', 5).execute()
        self.assertEqual(res[0][0], 5)

    def test_is_not_null(self):
        self.assertEqual(len(self.select.is_not_null('uid').execute()), 5)

    def test_expr(self):
        from  db import expr
        res = self.select.fields(expr('count(*)')).execute()
        self.assertEqual(res[0][0], 5)
        res = db.select('users').fields(expr('count(uid)', 'total')).execute()
        self.assertEqual(res[0][0], 5)
        

class TestUpdateQuery(unittest.TestCase):

    def setUp(self):
        setattr(db, '__db', {})
        db.setup(config)
        _create()
        users = []
        for i in range(1, 6):
            users.append((i, 'user_' + str(i)))
        db.execute('delete from users')
        db.execute('INSERT INTO users VALUES(%s, %s)', users)
        self.update = db.update('users')

    def tearDown(self):
        db.execute('delete from users')

    def test_update_on_name(self):
        res = (self.update.
               mset({'name':'update_test'})
               .condition('name','user_1')
               .execute())
        self.assertEquals(res, 1)


    def test_update_on_name_and_uid(self):
        res = (self.update.
               set('name', 'update_test')
               .condition('name', 'user_2')
               .condition('uid', 2)
               .execute())
        self.assertEquals(res, 1)

    def test_update_not_exists(self):
        res = (self.update.
               mset({'name':'update', 'uid': 10})
               .condition('name', 'not_exists')
               .execute())
        self.assertEquals(res, 0)

class TestInsertQuery(unittest.TestCase):

    def setUp(self):
        setattr(db, '__db', {})
        db.setup(config)
        _create()
        users = []
        for i in range(1, 6):
            users.append((i, 'user_' + str(i)))
        db.execute('delete from users')
        db.execute('INSERT INTO users VALUES(%s, %s)', users)
        self.insert = db.insert('users')
        self.select = db.select('users')

    def tearDown(self):
        db.execute('delete from users')

    def test_insert(self):
        res = self.insert.values((10, 'test_insert')).execute()
        res = self.select.condition('name', 'test_insert').execute()
        self.assertEqual(res[0][1], 'test_insert')

    def test_insert_dict_values(self):
        self.insert.fields('name').values({'name': 'insert_1'}).values(('insert_2',)).execute()
        res = self.select.condition('name', ['insert_1', 'insert_2']).execute()
        self.assertEqual(len(res), 2)

class TestDeleteQuery(unittest.TestCase):

    def setUp(self):
        setattr(db, '__db', {})
        db.setup(config)
        _create()
        users = []
        for i in range(1, 6):
            users.append((i, 'user_' + str(i)))
        db.execute('INSERT INTO users VALUES(%s, %s)', users)
        self.delete = db.delete('users')

    def tearDown(self):
        db.execute('delete from users')

    def test_delete_by_uid(self):
        res = self.delete.condition('uid', 1).execute()
        self.assertEqual(res, 1)

    def test_delete_by_condtions(self):
        res = self.delete.condition('uid', 2).condition('name', 'user_2').execute()
        self.assertEqual(res, 1)

    def test_delete_or_condtions(self):
        from db import or_
        or_con = or_().condition('name', 'user_1').condition('name', 'user_2')
        res = self.delete.condition(or_con).execute()
        self.assertEqual(res, 2)


class TestTransaction(unittest.TestCase):

    def setUp(self):
        setattr(db, '__db', {})
        db.setup(config)
        _create()
        users = []
        for i in range(1, 6):
            users.append((i, 'user_' + str(i)))
        db.execute('INSERT INTO users VALUES(%s, %s)', users)


    def tearDown(self):
        db.execute('delete from users')

    def test_with(self):
        with db.transaction() as t:
            t.delete('users').condition('uid', 1).execute()
            res = db.select('users').condition('uid', 1).execute()
            self.assertEqual(len(res), 1)
        res = db.select('users').condition('uid', 1).execute()
        self.assertEqual(len(res), 0)

    def test_begin_commit(self):
        t = db.transaction()
        t.begin()
        t.delete('users').condition('uid', 1).execute()
        res = db.select('users').condition('uid', 1).execute()
        self.assertEqual(len(res), 1)
        t.commit()
        res = db.select('users').condition('uid', 1).execute()
        self.assertEqual(len(res), 0)

if __name__ == '__main__':
    debug = True
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S', filemode='a+')
    unittest.main(verbosity=2 if debug else 0)