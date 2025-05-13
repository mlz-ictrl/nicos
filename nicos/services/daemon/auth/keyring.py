# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#   Christian Felder <c.felder@fz-juelich.de>
#   Björn Pedersen <bjoern.pedersen@frm2.tum.de>
#
# *****************************************************************************

from nicos.core import USER, Param, User, listof
from nicos.services.daemon.auth import AuthenticationError, \
    Authenticator as BaseAuthenticator
from nicos.services.daemon.auth.params import UserLevelAuthEntry
from nicos.utils.credentials.keystore import nicoskeystore


class Authenticator(BaseAuthenticator):
    r"""Authenticates against the fixed list of usernames, and
    user levels given in the "access" parameter (in order).
    Passwords are stored in an external keystore

    An empty password means that any password is accepted.
    Passwordless entries are restricted to 'at most' USER level.

    You can set passwords via:

    a) the `nicos-keystore` tool:

       `nicos-keystore add nicos_user \<username\>`

    b) the `keyring` tool (this may require additional dependencies to be
       installed):

       `keyring -b keyrings.alt.file.EncryptedKeyring set nicos_user \<username\>`

    Empty passwords are accepted.
    """

    parameters = {
        'access': Param('List of (username, userlevel) tuples',
                        type=listof(UserLevelAuthEntry)),
        'userdomain': Param('Keystore domain for user/pw authentication',
                            type=str, mandatory=False, settable=False,
                            default='nicos_user'),
    }

    def authenticate(self, username, password):
        # check for exact match (also matches empty password if username
        # matches)
        password_ks = nicoskeystore.getCredential(username,
                                                  domain=self.userdomain)
        if password_ks is None:
            raise AuthenticationError('Invalid username or password!')
        for (user, level) in self.access:
            if user == username:
                if password_ks == password:
                    if password == '' and level > USER:  # pylint: disable=compare-to-empty-string
                        level = USER  # limit passwordless entries to USER
                    return User(username, level)
                else:
                    raise AuthenticationError('Invalid username or password!')
        # do not give a hint whether username or password is wrong...
        raise AuthenticationError('Invalid username or password!')
