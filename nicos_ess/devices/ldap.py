#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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
#   Matt Clarke <matt.clarke@ess.eu>
#
# *****************************************************************************

import ldap3

from nicos.core import GUEST, Override, User
from nicos.services.daemon.auth import AuthenticationError
from nicos.services.daemon.auth.ldap import Authenticator as LDAPAuthenticator


class Authenticator(LDAPAuthenticator):
    parameter_overrides = {
        'groupbasedn': Override(mandatory=False),
    }

    def authenticate(self, username, password):
        connection = self._connect_to_server(username, password)
        group = self._get_user_group(connection, username)

        user_level = self._check_explicit_rights(username, GUEST)
        user_level = self._check_group_rights(group, user_level)

        return User(username, user_level)

    def _check_group_rights(self, group, user_level):
        if group in self.grouproles:
            user_level = max(user_level,
                             self._access_levels[self.grouproles[group]])
        return user_level

    def _check_explicit_rights(self, username, user_level):
        if username in self.userroles:
            user_level = self._access_levels[self.userroles[username]]
        return user_level

    def _connect_to_server(self, username, password):
        error = None
        try:
            server = ldap3.Server(self.uri, use_ssl=True)
            if not server.check_availability():
                raise AuthenticationError('LDAP server unavailable')
            connection = ldap3.Connection(server, user=f'{username}@ESSS.SE',
                                          password=password, auto_bind=True,
                                          read_only=True)
        except ldap3.core.exceptions.LDAPException as err:
            # this avoids leaking credential details via tracebacks
            error = str(err)
        if error:
            raise AuthenticationError(f'LDAP connection failed ({error})')
        return connection

    def _get_user_group(self, connection, username):
        try:
            if not connection.search(self.userbasedn,
                                     f'(sAMAccountName={username})',
                                     attributes=['department']) \
                                     or len(connection.entries) == 0:
                raise AuthenticationError('Could not get user details from '
                                          'LDAP')
            if len(connection.entries) == 1:
                group = connection.entries[0].department.value
                return group

            raise AuthenticationError('Could not get unique user details from '
                                      'LDAP')
        except AuthenticationError:
            raise
        except Exception as err:
            raise AuthenticationError(f'LDAP connection failed ({err})')\
                from None
