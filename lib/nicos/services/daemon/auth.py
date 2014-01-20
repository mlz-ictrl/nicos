#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2014 by the NICOS contributors (see AUTHORS)
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

"""NICOS daemon authentication and user abstraction."""

from nicos.core import Device, Param, listof, oneof, GUEST, USER, ADMIN, \
    ACCESS_LEVELS
from collections import namedtuple


User = namedtuple('User', 'name level')


system_user = User('system', ADMIN)


class AuthenticationError(Exception):
    pass


class Authenticator(Device):

    def pw_hashing(self):
        """Return the expected hashing method of the password.

        Can be 'md5', 'sha1' or 'plain' (no hashing).
        """
        return 'sha1'

    def authenticate(self, username, password):
        """Authenticate a user with given username and password hash.

        On success, must return a User object.  On failure, must raise
        `AuthenticationError`.

        The default implementation accepts any user and password and grants
        ADMIN user level.
        """
        return User(username, ADMIN)


def auth_entry(val=None):
    val = list(val)
    if len(val) != 3:
        raise ValueError('auth entry needs to be a 3-tuple '
                         '(name, password, accesslevel)')
    if not isinstance(val[0], str):
        raise ValueError('user name must be a string')
    val[0] = val[0].strip()
    if not isinstance(val[1], str):
        raise ValueError('user password must be a string')
    val[1] = val[1].strip()
    if isinstance(val[2], str):
        for i, name in ACCESS_LEVELS.iteritems():
            if name == val[2].strip():
                val[2] = i
                break
        else:
            raise ValueError('access level must be one of %s' %
                             ', '.join(map(repr, ACCESS_LEVELS.values())))
    elif not isinstance(val[2], int):
        # for backwards compatibility: allow integer values as well
        raise ValueError('access level must be one of %s' %
                         ', '.join(map(repr, ACCESS_LEVELS.values())))
    else:
        if val[2] not in ACCESS_LEVELS.keys():
            raise ValueError('access level must be one of %s' %
                             ', '.join(map(repr, ACCESS_LEVELS.values())))
    return tuple(val)


class ListAuthenticator(Authenticator):
    """Authenticates against the fixed list of usernames, passwords and
    user levels given in the "passwd" parameter (in order).

    An empty password means that any password is accepted.
    An empty username means that any username is accepted.
    Password less entries and anonymous entries are restricted
    to 'at most' USER level. If both fields are unspecified, we still request
    a username and restrict to GUEST level.
    """

    parameters = {
        'hashing': Param('Type of hash used for the password (sha1 or md5)',
                         type=oneof('sha1', 'md5')),
        'passwd':  Param('List of (username, password_hash, userlevel) tuples',
                         type=listof(auth_entry)),
    }

    def pw_hashing(self):
        return self.hashing

    def authenticate(self, username, password):
        username = username.strip()
        if not username:
            raise AuthenticationError('No username, please identify yourself!')
        # check for exact match (also matches empty password if username matches)
        for (user, pw, level) in self.passwd:
            if user == username:
                if not pw or pw == password:
                    if not password and level > USER:
                        level = USER # limit passwordless entries to USER
                    return User(username, level)
                else:
                    raise AuthenticationError('Invalid username or password!')
        # check for unspecified user
        for (user, pw, level) in self.passwd:
            if user == '':
                if pw and pw == password:
                    if level > USER:
                        level = USER # limit passworded anonymous to USER
                    return User(username, level)
                elif not pw: # fix passwordless anonymous to GUEST
                    return User(username, GUEST)
        # do not give a hint whether username or password is wrong...
        raise AuthenticationError('Invalid username or password!')


class PamAuthenticator(Authenticator):
    """Authenticates against PAM.

    This unfortunately only works against the local shadow database if the
    daemon runs as the root user.

    The access level info can be put into the "gecos" field.
    """

    def pw_hashing(self):
        return 'plain'

    def authenticate(self, username, password):
        try:
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
        except Exception as err:
            raise AuthenticationError('exception during PAM authentication: %s'
                                      % err)
