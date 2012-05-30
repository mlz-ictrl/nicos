#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""NICOS daemon user abstraction."""

__version__ = "$Revision$"

from nicos.core import GUEST, USER, ADMIN


class User(object):
    def __init__(self, username, accesslevel):
        self.name = username
        self.level = accesslevel


class AuthenticationError(Exception):
    pass


class Authenticator(object):
    def __init__(self, daemon):
        self.method = daemon.authmethod
        self.passwd = daemon.passwd

    def needs_plain_pw(self):
        return self.method == 'pam'

    def authenticate(self, username, password):
        try:
            if self.method == 'none':
                return User(username, ADMIN)
            elif self.method == 'list':
                entry = None
                for entry in self.passwd:
                    if entry[0] == username:
                        break
                else:
                    raise AuthenticationError('no such user')
                if entry[1] and password != entry[1]:
                    raise AuthenticationError('wrong password hash')
                if entry[2] in (GUEST, USER, ADMIN):
                    return User(username, entry[2])
                else:
                    return User(username, GUEST)
            elif self.method == 'pam':
                import pam, pwd
                message = pam.authenticate(username, password)
                if message:
                    raise AuthenticationError('PAM authentication failed: %s'
                                              % message)
                entry = pwd.getpwnam(username)
                idx = entry.pw_gecos.find('access=')
                if idx > -1:
                    access = int(entry.pw_gecos[idx+7])
                    if access in (GUEST, USER, ADMIN):
                        return User(username, access)
                return User(username, ADMIN)
        except AuthenticationError:
            raise
        except Exception, err:
            raise AuthenticationError('exception during authenticate(): %s'
                                      % err)
