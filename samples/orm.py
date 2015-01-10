# !/usr/bin/env python
# Copyright (C) 2014-2015 Thomas Huang

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2 of the License.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
import db

from model import User, Post

logger = logging.getLogger(__name__)

class BaseMapper(object):

    def load(self, data, o):
        return o(*data)


class PrimaryTrait(object):

    primary_id = 'id'

    def find(self, id):
        q = db.select(self.table).condition(self.primary_id, id)
        data = q.query()
        if data:
            return self.load(data[0], self.model)



class UserMapper(BaseMapper,  PrimaryTrait):

    model = User
    table = 'users'

    def find(self, uid):
        """Find and load the user from database by uid(user id)"""
        data = (db.select(self.table).select('username', 'email', 'real_name',
                'password', 'bio', 'status', 'role', 'uid').
                condition('uid', uid).execute()
                )
        if data:
            logger.info('data %s', data)
            return self.load(data[0], self.model)

    def find_by_username(self, username):
        """Return user by username if find in database otherwise None"""
        data = (db.select(self.table).select('username', 'email', 'real_name',
                'password', 'bio', 'status', 'role', 'uid').
                condition('username', username).execute()
                )
        if data:
            return self.load(data[0], self.model)

    def create(self, user):
        return db.execute("INSERT INTO users(username, email, real_name, password, bio, status, role) \
             VALUES(%s, %s, %s, %s, %s, %s, %s)",
                          (user.username, user.email, user.real_name, user.password, user.bio, user.status, user.role))

    def search(self, **kw):
        """Find the users match the condition in kw"""
        q = db.select(self.table).condition('status', 'active')
        for k, v in kw:
            q.condition(k, v)
        data = q.execute()
        users = []
        for user in data:
            users.append(self.load(user, self.model))
        return users

    def count(self):
        return db.query('SELECT COUNT(*) FROM ' + self.table)[0][0]

    def paginate(self, page=1, perpage=10):
        count = self.count()
        q = db.select(self.table).select('username', 'email', 'real_name',
                                         'password', 'bio', 'status', 'role', 'uid')
        results = q.limit(perpage).offset((page - 1) * perpage).order_by('real_name', 'desc').execute()
        return [self.load(user, self.model) for user in results]
        

    def save(self, user):
        q = db.update(self.table)
        data = dict( (_, getattr(user, _)) for _ in ('username', 'email', 'real_name',
                'password', 'bio', 'status', 'role'))
        q.mset(data)
        return q.condition('uid', user.uid).execute()

    def delete(self, user):
        return db.delete(self.table).condition('uid', user.uid).execute()

class PostMapper(BaseMapper):

    table = 'posts'
    model = Post
    
    def find(self, pid):
        data = db.select(self.table).fields('title', 'slug', 'description', 'html', 'css', 'js', 
            'category', 'status', 'comments', 'author', 'created', 'pid').condition('pid', pid).execute()
        if data:
            return self.load(data[0], self.model)

    def count(self):
        return db.select(self.table).fields(db.expr('COUNT(*)')).execute()[0][0]

    def create(self, post):
        row = []
        for _ in ('title', 'slug', 'description', 'created', 'html', 'css', 'js', 
            'category', 'status', 'comments', 'author'):
            row.append(getattr(post, _))
        return db.insert(self.table).columns('title', 'slug', 'description', 'created', 'html', 'css', 'js', 
            'category', 'status', 'comments', 'author').values(row).execute()

    def paginate(self, page=1, perpage=10, category=None):
        """Paginate the posts"""
        q = db.select(self.table).fields('title', 'slug', 'description', 'html', 'css', 'js', 
            'category', 'status', 'comments', 'author', 'created', 'pid')
        if category:
            q.condition('category', category)
        results = (q.limit(perpage).offset((page - 1) * perpage)
                    .order_by('created', 'DESC').execute())
        return [self.load(data, self.model) for data in results]


    def save(self, page):
        q = db.update(self.table)
        data = dict( (_, getattr(page, _)) for _ in ('title', 'slug', 'description', 'html', 'css', 'js', 
            'category', 'status', 'comments'))
        q.mset(data)
        return q.condition('pid', page.pid).execute()

    def delete(self, page_id):
        return db.delete(self.table).condition('pid', page_id).execute()


    def category_count(self, category_id):
        return db.select(self.table).fields(db.expr('count(*)', 
            'total')).condition('category', category_id).condition('status', 'published').execute()[0][0]



__backends = {}
__backends['post'] = PostMapper()
__backends['user'] = UserMapper()

def Backend(name):
    return __backends.get(name)