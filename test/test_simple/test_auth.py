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

import pytest

from nicos.services.daemon.auth import auth_entry, ListAuthenticator, \
    AuthenticationError
from nicos.core import GUEST, USER, User

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


@pytest.fixture(scope='function')
def ListAuth(request):
    Auth = ListAuthenticator('authenicator',
                             passwd=request.function.passwd)
    yield Auth


def test_passwd_user(session, ListAuth):
    assert ListAuth.authenticate('user', 'user') == User('user', USER)
    assert ListAuth.authenticate('guest', '') == User('guest', GUEST)
    assert ListAuth.authenticate('guest', 'somepw') == User('guest', GUEST)
    assert raises(AuthenticationError, ListAuth.authenticate, 'user', 'nouser')
    assert raises(AuthenticationError, ListAuth.authenticate, 'joedoe', '')

test_passwd_user.passwd = [('guest', '', 'guest'),
                           ('user', 'user', 'user'),
                           ('admin', 'admin', 'admin')]


def test_any_user(session, ListAuth):
    assert ListAuth.authenticate('user', 'user') == User('user', USER)
    assert ListAuth.authenticate('guest', '') == User('guest', GUEST)
    assert ListAuth.authenticate('joedoe', '') == User('joedoe', GUEST)
    assert ListAuth.authenticate('joedoe', '') != User('joedoe', USER)
    assert raises(AuthenticationError, ListAuth.authenticate, 'user', 'user_')

test_any_user.passwd = [('guest', '', 'guest'),
                        ('', '', 'admin'),
                        ('user', 'user', 'user'),
                        ('admin', 'admin', 'admin')]


def test_empty_user(session, ListAuth):
    assert ListAuth.authenticate('joedoe', 'passwd') == User('joedoe', USER)

test_empty_user.passwd = [('admin', 'admin', 'admin'),
                          ('', 'passwd', 'admin')]
