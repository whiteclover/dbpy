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
