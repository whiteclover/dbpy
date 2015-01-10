DBPY
#####


.. contents::
    :depth: 3

dbpy是一个python写的数据库CURD人性化api库。借鉴了 `webpy db <https://github.com/webpy/webpy>`_ 和 `drupal database <https://www.drupal.org/developing/api/database>`_ 的设计。 如果你喜欢 tornado db 或者 webpy db这类轻巧的db库，或者想发挥原生SQL优势，那么绝对值得一试。 



Featues
================

#. 灵活简单
#. 天马行空的SQL构建语法糖
#. 线程安全的连接池
#. 支持读写分离（当前限定只能是一主多副模式）
#. 支持简单事务


Install
==============

从github上fork下来，终端执行下面命令:

.. code-block:: bash

    cd dbpy # the path to the project
    python setup.py install

.. note:: 安装前先安装 ``MySQLdb`` (``MySQL-python``) 依赖python库


Development
===========

下载后终端执行:

.. code-block:: bash 

    cd dbpy # the path to the project
    python setup.py develop


Compatibility
=============

在 Python 2.7.x 测试开发

DB API
========

先提醒下模块使用单例模式。所以api相对比较好使。


.. code-block:: python

    config = {
            'passwd': 'test',
            'user': 'test',
            'host': 'localhost',
            'db': 'test',
            'max_idle' : 5*60
        }

    db.setup(config，  minconn=5, maxconn=10,  
        adapter='mysql', key='defalut', slave=False)



setup
---------

:config: 是数据库连接参数，可以传入MySQLDB#connect接口中所有的可选参数。 其中``max_idel`` 相对是mysql服务端 connect_timeout配置,默认10秒。
:minconn: 为当前数据库连接池保持最小连接池，默认为5
:maxconn: 为当前数据库连接池最大连接池，默认为10
:adapter: 为适配器名，当前只支持 mysql
:key: 是数据库的标识符,默认为 default
:slave: 如果为true那么当前的数据库将会注册为读数据库。如果你没有做读写分离，只有一个数据库用来读写，那么setup一次就好，这样就可以读写。

.. code-block:: python

    config = {
            'passwd': 'test',
            'user': 'test',
            'host': 'localhost',
            'db': 'test',
            'max_idle' : 5*60
        }

    db.setup(config， key='test')
    config['host'] = 'test.slave'
    # 这次setup将会把key标记为仅可写，就是在后面用api时，制定到当前key的数据库会做数据分离
    db.setup(config， key='test', slave=True) 

    config['host'] = 'test.slave2'
    # 再加入一个slave数据库
    db.setup(config， key='test', slave=True)


    config['host'] = 'host2'
    config['db'] = 'social'
    # 再加入一个数据库
    db.setup(config， key='social', slave=True)

query
-------

query用于raw sql的查询语言。如果有更新数据请用execute.

query(sql, args=None, many=None, as_dict=False, key='default'):

:sql: mysql的格式化raw sql
:args: 可以为元组和list，是sql格式化预处理的输入
:many: 如果指定为大于零的整数将会使用fetchmany语句，并返回对象将会是迭代器.否则api调用fetchall返回结果.
:as_dict: 如果为 true将会返回字典行，否则返回元组行。
:key: 用于指定使用那个数据库。


.. code-block:: python

    print db.query('SELECT 1')
    # > ((1L,),)

    # use social db
    print db.query('SELECT 1', key='social')
    # > ((1L,),)

    print db.query('SELECT * FROM users WHERE uid=%s and name=%s', (1, 'user_1'))
    # > ((1L, u'user_1'),)

    # Wanna return dict row
    print db.query('SELECT * FROM users WHERE uid=%s and name=%s', (1, 'user_1'), as_dict=True)
    # > ({'uid': 1L, 'name': u'user_1'},)

    # Use fetchmany(many) then yeild, Return generator
    res = db.query('SELECT * FROM users WHERE uid=%s and name=%s', (1, 'user_1'), many=5, as_dict=True)
    print res
    print res.next()
    # > <generator object _yield at 0x7f818f4b6820>
    # > {'uid': 1L, 'name': u'user_1'}


execute
--------

execute用于raw sql的更新语言。
execute(sql, args=None, key='default'):


:sql: mysql的格式化raw sql
:args: 可以为元组和list，是sql格式化预处理的输入.如下面例子insert语句values有多个插入时，调用 ``executemany``
:key: 用于指定使用那个数据库。

返回规范::

   对于insert 将会返回 last_insert_id, 其他更新语句返回rowcount

.. code-block:: python
    
    db.execute('DROP TABLE IF EXISTS `users`')
    db.execute("""CREATE TABLE `users` (
             `uid` int(10) unsigned NOT NULL AUTO_INCREMENT,
            `name` varchar(20) NOT NULL,
            PRIMARY KEY (`uid`))""")
    
    # insert语句插入多个value，注意这样写将会调用executemany，你懂的，就是封装了多条execute的玩意
    db.execute('INSERT INTO users VALUES(%s, %s)', [(10, 'execute_test'), (9, 'execute_test')])
    # > 9
    db.execute('DELETE FROM users WHERE name=%s', ('execute_test',))
    # > 2


    # use social db
    print db.execute('delete from events where created_at<%s', (expired, ), key='social')
    # > 10

select
-----------


select(table, key='default'):

:table: 选定表
:key: 用于指定使用那个数据库。

select all
~~~~~~~~~~~~~~~~

.. code-block:: python

    db.select('users')
    # > SELECT * FROM `users`

specific columns
~~~~~~~~~~~~~~~~~

.. code-block:: python

    db.select('users').fields('uid', 'name')
    # > SELECT `uid`, `name` FROM `users`


execute
~~~~~~~~~~~~~~~~

在构建好查询条语句后使用execute api可以返回结果。

execute(many=None, as_dict=False):

:many: 如果指定为大于零的整数将会使用fetchmany语句，并返回对象将会是迭代器.否则api调用fetchall返回结果.
:as_dict: 如果为 true将会返回字典行，否则返回元组行。

.. code-block:: python

    q = db.select('users').fields('uid', 'name')
    res = q.execute()
    print res
    # > ((1L, u'user_1'), (2L, u'user_2'), (3L, u'user_3'), (4L, u'user_4'), (5L, None))

    res = q.execute(many=2, as_dict=True)
    print res
    print res.next()
    # > <generator object _yield at 0x7f835825e820>
    # > {'uid': 1L, 'name': u'user_1'}


Condition
~~~~~~~~~~~

上面已经学会如何做简单的查询，那么如何组件条件查询。这里将会重点讲述condition方法如何构建各种查询条件。

condition(field, value=None, operator=None):

:field: 是条件限制的表字段
:value: 是字段的条件值， 如果炸路额， oprator都不指定就是 "field is null"
:operator: 默认可能是等于操作符号， 可选的操作符号有 BETWEEN, IN, NOT IN, EXISTS, NOT EXISTS, IS NULL, IS NOT NULL, LIKE, NOT LIKE, =, <, >, >=, <=, <>等


在所有的select，update, delete查询中多个默认的condition将会是and条件组合。

simple 
^^^^^^^^^^^^^^^^

.. code-block:: python

    db.select('users').condition('uid', 1) # condition('uid', 1, '=')
    # > SELECT * FROM `users`
    # > WHERE  `uid` = %s 


in 
^^^^^^^^^^^^^^^^

.. code-block:: python


    db.select('users').condition('uid', (1, 3)) # condition('uid', [1, 3]) 一样
    # > SELECT * FROM `users`
    # > WHERE  `uid` IN  (%s, %s) 

between 
^^^^^^^^^^^^^^^^

.. code-block:: python

    db.select('users').condition('uid', (1, 3), 'between')
    # > SELECT * FROM `users`
    # > WHERE  `uid` BETWEEN %s AND %s 


multi condition
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    db.select('users').condition('uid', 1).condition('name', 'blabla')
    # > SELECT * FROM `users`
    # > WHERE  `uid` = %s AND `name` = %s 

or condition
^^^^^^^^^^^^^^

.. code-block:: python

    or_cond = db.or_().condition('uid', 1).condition('name', 'blabla')
    db.select('users').condition(or_cond).condition('uid', 1, '<>')
    # > SELECT * FROM `users`
    # > WHERE  ( `uid` = %s OR `name` = %s ) AND `uid` <> %s 



order by
~~~~~~~~~

.. code-block:: python

    db.select('users').order_by('name')
    # > SELECT * FROM `users`
    # > ORDER BY `name`

    db.select('users').order_by('name', 'DESC')
    # > SELECT * FROM `users`
    # > ORDER BY `name` DESC

    db.select('users').order_by('name', 'DESC').order_by('uid')
    # > SELECT * FROM `users`
    # > ORDER BY `name` DESC, `uid`



distinct
~~~~~~~~~

.. code-block:: python

    db.select('users').distinct().condition('uid', 1)
    # > SELECT DISTINCT * FROM `users`
    # > WHERE  `uid` = %s 

    db.select('users').fields('uid', 'name').distinct().condition('uid', 1)
    # > SELECT DISTINCT `uid`, `name` FROM `users`
    # > WHERE  `uid` = %s 


group by
~~~~~~~~~

.. code-block:: python

    db.select('users').group_by('name', 'uid')
    # > SELECT * FROM `users`
    # > GROUP BY `name`, `uid`


limit and offset
~~~~~~~~~~~~~~~~~

.. code-block:: python

    db.select('users').limit(2).offset(5)
    # > SELECT * FROM `users`
    # > LIMIT 2 OFFSET 5

null condition
~~~~~~~~~~~~~~~

.. code-block:: python

    db.select('users').is_null('name').condition('uid', 5)
    # > SELECT * FROM `users`
    # > WHERE  `name` IS NULL  AND `uid` = %s 

    db.select('users').is_not_null('name').condition('uid', 5)
    # > SELECT * FROM `users`
    # > WHERE  `name` IS NOT NULL  AND `uid` = %s 

    db.select('users').condition('name', None)
    # > SELECT * FROM `users`
    # > WHERE  `name` IS NULL  


complex conditions
-------------------

使用 db.and_(), db.or_() 可以构建and或or粘合的条件组合。

.. code-block:: python

    or_cond = db.or_().condition('field1', 1).condition('field2', 'blabla')
    and_cond = db.and_().condition('field3', 'what').condition('field4', 'then?')
    print db.select('table_name').condition(or_cond).condition(and_cond)

    # > SELECT * FROM `table_name`
    # > WHERE  ( `field1` = %s OR `field2` = %s ) AND ( `field3` = %s AND `field4` = %s ) 

expr
------------

如果你需要使用 count sum之类的集聚函数，那么使用 Expr构建字段吧。

.. code-block:: python

    from  db import expr

    db.select('users').fields(expr('count(*)'))
    # > SELECT count(*) FROM `users`

    db.select('users').fields(expr('count(uid)', 'total'))
    # > SELECT count(uid) AS `total` FROM `users`



insert
-----------


insert(table, key='default'):

:table: 选定表
:key: 用于指定使用那个数据库。


.. code-block:: python

    q = db.insert('users').values((10, 'test_insert'))
    # > INSERT INTO `users` VALUES(%s, %s)
    print q._values
    # > [(10, 'test_insert')]


    q = db.insert('users').fields('name').values({'name': 'insert_1'}).values(('insert_2',))
    # > INSERT INTO `users`(`name`) VALUES(%s)
    print q._values
    # > [('insert_1',), ('insert_2',)]

构建好执行execute会执行数据库插入,execute返回的是last insert id：

.. code-block:: python
    
    
    print q.execute()
    # > 2



update
-----------


update(table, key='default'):

:table: 选定表
:key: 用于指定使用那个数据库。

update 主要可用的方法是mset和set， mset：

:mset: 传入的是字典，用于一次set多个表属性
:set(column, value): 只能设置一个属性，可以多次使用 

构建条件codition前面已经讲述了。请参考 `select`_


.. code-block:: python
    
    
    db.update('users').mset({'name':None, 'uid' : 12}).condition('name','user_1')
    # > UPDATE `users` SET `name` = %s, `uid` = %s WHERE  `name` = %s 

    q = db.update('users').set('name', 'update_test').set('uid', 12).condition('name', 'user_2').condition('uid', 2) # .execute()
    print q.to_sql()
    # > UPDATE `users` SET `name` = %s, `uid` = %s WHERE  `name` = %s AND `uid` = %s 
  
	
构建好执行execute会执行数据库插入,execute返回的是更新的 rowcount：

.. code-block:: python
    
    
    print q.execute()
    # > 2

limit
~~~~~~~~~

因为你可能希望限制更新几条。那么可以使用limit


.. code-block:: python
    
    db.update('users').mset({'name':None, 'uid' : 12}).condition('name','user_1').limit(5)
    # > UPDATE `users` SET `name` = %s, `uid` = %s WHERE  `name` = %s  LIMIT 5

delete
-----------


delete(table, key='default'):

:table: 选定表
:key: 用于指定使用那个数据库。

构建条件codition前面已经讲述了。请参考 `select`_

.. code-block:: python
    
    db.delete('users').condition('name','user_1')
    # > DELETE FROM `users` WHERE  `name` = %s 
	
构建好执行execute会执行数据库插入,execute返回的是删除的 rowcount：

.. code-block:: python
    
    
    print q.execute()
    # > 2


to_sql and str
---------------------

``db.insert``, ``db.update``,  ``db.delete`` 返回的对象都可以使用 to_sql 或者__str__ 来查看构建成的sql语句。


.. code-block:: python
    

    q = db.update('users').set('name', 'update_test').set('uid', 12).condition('name', 'user_2').condition('uid', 2)
    print q.to_sql()
    print q
    # > UPDATE `users` SET `name` = %s, `uid` = %s WHERE  `name` = %s AND `uid` = %s 


transaction
------------

transaction(table, key='default'):

:table: 选定表
:key: 用于指定使用那个数据库。

对于事务，这里比较简单的实现。要么全部执行，要么全部不做，没用做保存点。



.. code-block:: python
    

    # with context
    with db.transaction() as t:
        t.delete('users').condition('uid', 1).execute()
        t.update('users').mset({'name':None, 'uid' : 12}).condition('name','user_1').execute()


    # 普通用法
    t = db.transaction()
    t.begin()
    t.delete('users').condition('uid', 1).execute()
    t.update('users').mset({'name':None, 'uid' : 12}).condition('name','user_1').execute()
    #这里将会提交，如果失败将会rollback
    t.commit()

.. note:: 使用 begin一定要结合commit方法，不然可能连接不会返还连接池。建议用 ``with`` 语句。


simple orm
-----------

这里将会讲述最简单的orm构建技巧， 详细参考 `samples <https://github.com/thomashuang/dbpy/blob/master/samples>`_

.. code-block:: python
    
    import model
    from orm import Backend
    import db

    db.setup({ 'host': 'localhost', 'user': 'test', 'passwd': 'test', 'db': 'blog'})


    user = Backend('user').find_by_username('username')
    if user and user.check('password'):
        print 'auth'

    user = model.User('username', 'email', 'real_name', 'password', 'bio', 'status', 'role')
    if Backend('user').create(user):
        print 'fine'

    user = Backend('user').find(12)
    user.real_name = 'blablabla....'
    if Backend('user').save(user):
        print 'user saved'

    if Backend('user').delete(user):
        print 'delete user failed'


    post = model.Post('title', 'slug', 'description', 'html', 'css', 'js', 'category', 'status', 'comments', 'author')
    if not Backend('post').create(post):
        print 'created failed'

Future
--------

当前只支持mysql适配驱动，因为个人并不熟悉其他关联数据库，dbpy的设计比较灵活，所以如果有高手可以尝试写写其他数据库适配，仿照 `db/mysql目录 <https://github.com/thomashuang/dbpy/blob/master/db/mysql>`_ 如果写pgsql的适配应该不会多余800行代码。


对于构建orm框架方面，从个人来讲，更喜欢原生SQL，也不打算再造一个orm轮子。从设计和实现来说，dbpy是为了更好的发挥原生SQL优势和简单灵活。

下面是个人一些想法：

#. 为select加入join构建方法糖。
#. 尝试完成schame类，用于创建表，修改表结构等。
#. 加入一些mysql特有的sql方法糖，比如replace， on dup更新等。
#. 优化改进pool连接池，比如加入固定大小连接池的pool。


LICENSE
=======

    Copyright (C) 2014-2015 Thomas Huang

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, version 2 of the License.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

