#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Module authors:
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

from nicos.services.daemon.auth import auth_entry, ListAuthenticator, \
    AuthenticationError
from nicos.core import GUEST, USER, User
from nicos.commands.basic import RemoveDevice

from test.utils import raises

session_setup = 'empty'


def test_auth_entry():
    assert auth_entry(['user', 'passwd', 'user']) == ('user', 'passwd', USER)
    assert auth_entry(['user', 'passwd', USER]) == ('user', 'passwd', USER)
    assert auth_entry([' user ', 'passwd', USER]) == ('user', 'passwd', USER)
    assert auth_entry(['user', ' passwd ', USER]) == ('user', 'passwd', USER)
    assert raises(ValueError, auth_entry, ['user', 'passwd', 'xxx'])
    assert raises(ValueError, auth_entry, ['user', 'passwd', -1])
    assert raises(ValueError, auth_entry, ['user', 'passwd', ()])
    assert raises(ValueError, auth_entry, [['user'], 'passwd', 'user'])
    assert raises(ValueError, auth_entry, ['user', ['passwd'], 'user'])


def test_passwd_user(session):
    Auth = ListAuthenticator('authenicator',
                             passwd = [('guest', '', 'guest'),
                                       ('user', 'user', 'user'),
                                       ('admin', 'admin', 'admin')])
    assert Auth.authenticate('user', 'user') == User('user', USER)
    assert Auth.authenticate('guest', '') == User('guest', GUEST)
    assert Auth.authenticate('guest', 'somepw') == User('guest', GUEST)
    assert raises(AuthenticationError, Auth.authenticate, 'user', 'nouser')
    assert raises(AuthenticationError, Auth.authenticate, 'joedoe', '')
    RemoveDevice(Auth)


def test_any_user(session):
    Auth = ListAuthenticator('authenicator',
                             passwd = [('guest', '', 'guest'),
                                       ('', '', 'admin'),
                                       ('user', 'user', 'user'),
                                       ('admin', 'admin', 'admin')])
    assert Auth.authenticate('user', 'user') == User('user', USER)
    assert Auth.authenticate('guest', '') == User('guest', GUEST)
    assert Auth.authenticate('joedoe', '') == User('joedoe', GUEST)
    assert Auth.authenticate('joedoe', '') != User('joedoe', USER)
    assert raises(AuthenticationError, Auth.authenticate, 'user', 'user_')
    RemoveDevice(Auth)


def test_empty_user(session):
    Auth = ListAuthenticator('authenicator',
                             passwd = [('admin', 'admin', 'admin'),
                                       ('', 'passwd', 'admin')])
    assert Auth.authenticate('joedoe', 'passwd') == User('joedoe', USER)
    RemoveDevice(Auth)
