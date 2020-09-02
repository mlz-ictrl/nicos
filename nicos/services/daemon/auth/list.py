#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

import hashlib

from nicos.core import GUEST, USER, Param, User, listof, oneof
from nicos.pycompat import from_maybe_utf8, to_utf8
from nicos.services.daemon.auth import AuthenticationError, \
    Authenticator as BaseAuthenticator
from nicos.services.daemon.auth.params import UserPassLevelAuthEntry


class Authenticator(BaseAuthenticator):
    """Authenticates against the fixed list of usernames, passwords and
    user levels given in the "passwd" parameter (in order).

    An empty password means that any password is accepted.
    An empty username means that any username is accepted.
    Passwordless entries and anonymous entries are restricted
    to 'at most' USER level. If both fields are unspecified, we still request
    a username and restrict to GUEST level.

    One way to create the password hashes is the use of the `mkpasswd` tool::

      # tools/mkpasswd -E md5
      Please enter password:
      5f4dcc3b5aa765d61d8327deb882cf99

    or::

      # tools/mkpasswd -E sha1
      Please enter password:
      5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8

    These hexdigests can be used in the `passwd` list::

       passwd = [
           ...
           ('username', '5f4dcc3b5aa765d61d8327deb882cf99', 'user'),
           ...
       ]
    """

    parameters = {
        'hashing': Param('Type of hash used for the password (sha1 or md5)',
                         type=oneof('sha1', 'md5')),
        'passwd':  Param('List of (username, password_hash, userlevel) tuples',
                         type=listof(UserPassLevelAuthEntry)),
    }

    def _hash(self, password):
        password = to_utf8(from_maybe_utf8(password))
        if self.hashing == 'sha1':
            password = hashlib.sha1(password).hexdigest()
        elif self.hashing == 'md5':
            password = hashlib.md5(password).hexdigest()
        return password

    def authenticate(self, username, password):
        username = username.strip()
        if not username:
            raise AuthenticationError('No username, please identify yourself!')
        # check for exact match (also matches empty password if username
        # matches)
        for (user, pw, level) in self.passwd:
            if user == username:
                if not pw or pw == self._hash(password):
                    if not password and level > USER:
                        level = USER  # limit passwordless entries to USER
                    return User(username, level)
                else:
                    raise AuthenticationError('Invalid username or password!')
        # check for unspecified user
        for (user, pw, level) in self.passwd:
            if user == '':  # pylint: disable=compare-to-empty-string
                if pw and pw == self._hash(password):
                    if level > USER:
                        level = USER  # limit passworded anonymous to USER
                    return User(username, level)
                elif not pw:  # fix passwordless anonymous to GUEST
                    return User(username, GUEST)
        # do not give a hint whether username or password is wrong...
        raise AuthenticationError('Invalid username or password!')
