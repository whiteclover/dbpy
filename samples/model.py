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

from hashlib import sha224
from datetime import datetime



class User(object):

    def __init__(self, username, email, real_name, password, bio, status, role='user', uid=None):
        """If the user load from database, if will intialize the uid and secure password.
        Otherwise will hash encrypt the real password

        arg role enum: the string in ('user', 'editor', 'administrator')
        arg status enum: the string in ('actived', 'inactive')
        arg password fix legnth string: the use sha224 password hash
        """

        self.username = username
        self.email = email
        self.real_name = real_name
        self.bio = bio
        self.status = status
        self.role = role

        if uid:
            self.uid = uid
            self.password = password
        else:
            self.password = self.secure_password(password)

    def check(self, password):
        """Check the password"""
        return self.password == self.secure_password(password)

    def secure_password(self, password):
        """Encrypt password to sha224 hash"""
        return sha224(password).hexdigest()

    def as_json(self):
        data = self.__dict__.copy()
        del data['password']
        return data



class Post(object):

    def __init__(self, title, slug, description, html, css, js, category, status, 
        comments, author=None, created=datetime.now(), pid=None):
        self.title = title
        self.slug = slug
        self.description = description
        self.created = created
        self.html = html
        self.css = css
        self.js = js
        self.category = category
        self.status = status
        self.comments = comments
        self.author = author
        self.created = created
        self.pid = pid


    def as_json(self):
        data = self.__dict__.copy()
        return data
