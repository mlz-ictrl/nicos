#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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

"""NICOS daemon authentication and user abstraction."""

from nicos.core import Device, Param, dictof, listof, oneof, GUEST, USER, ADMIN, \
    ACCESS_LEVELS, NicosError, User
from nicos.pycompat import string_types

try:
    import ldap3  # pylint: disable=F0401
except ImportError:
    ldap3 = None


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
    if not isinstance(val[0], string_types):
        raise ValueError('user name must be a string')
    val[0] = val[0].strip()
    if not isinstance(val[1], string_types):
        raise ValueError('user password must be a string')
    val[1] = val[1].strip()
    if isinstance(val[2], string_types):
        for i, name in ACCESS_LEVELS.items():
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
        if val[2] not in ACCESS_LEVELS:
            raise ValueError('access level must be one of %s' %
                             ', '.join(map(repr, ACCESS_LEVELS.values())))
    return tuple(val)


class LDAPAuthenticator(Authenticator):
    """Authenticates against the configured LDAP server.

    Basically it tries to bind on the server with the given userdn.
    Per default, all ldap users are rejected when there is no user level
    definition inside the 'roles' dictionary.
    """

    parameters = {
        'server': Param('Ldap server',
                        type=str,
                        mandatory=True),
        'port':   Param('Ldap port',
                        type=int,
                        default=389),
        'userbasedn':  Param('Base dn to query users.',
                             type=str,
                             mandatory=True),
        'userfilter':  Param('Filter for querying users. Must contain "%(username)s"',
                             type=str,
                             default='(&(uid=%(username)s)(objectClass=posixAccount))'),
        'groupbasedn': Param('Base dn to query groups.',
                             type=str,
                             mandatory=True),
        'groupfilter': Param('Filter for querying groups. Must contain "%(gidnumber)s"',
                             type=str,
                             default='(&(gidNumber=%(gidnumber)s)(objectClass=posixGroup))'),
        'userroles':   Param('Dictionary of allowed users with their associated role',
                             type=dictof(str, oneof(*ACCESS_LEVELS.values()))),
        'grouproles':  Param('Dictionary of allowed groups with their associated role',
                             type=dictof(str, oneof(*ACCESS_LEVELS.values()))),
    }

    def doInit(self, mode):
        # refuse the usage of the ldap authenticator if the ldap3 package is missing
        if not ldap3:
            raise NicosError('LDAP authentication not supported (ldap3 package missing)')

        # create a ldap server object
        self._server = ldap3.Server('%s:%d' % (self.server, self.port))

    def pw_hashing(self):
        # A plain password is necessary for ldap bind.
        return 'plain'

    def authenticate(self, username, password):
        userdn = self._buildUserDn(username)

        # first of all: try a bind to check user existance and password
        conn = ldap3.Connection(self._server, user=userdn, password=password)
        if not conn.bind():
            raise AuthenticationError('LDAP bind failed')

        userlevel = -1

        # check if the user has explicit rights
        if username in self.userroles:
            userlevel = self._getUserLevelCodeForRoleName(self.userroles[username])
            return User(username, userlevel)

        # if no explicit user right was given, check group rights
        groups = self._getUserGroups(conn, username)

        for group in groups:
            if group in self.grouproles:
                levelCode = self._getUserLevelCodeForRoleName(self.grouproles[group])
                if levelCode > userlevel:
                    userlevel = levelCode

        self.log.warning('## %r' % userlevel)

        if userlevel >= 0:
            return User(username, userlevel)

        raise AuthenticationError('Login not permitted for the given user')

    def _getUserLevelCodeForRoleName(self, role):
        for levelCode, name in ACCESS_LEVELS.items():
            if name == role:
                return levelCode
        return -1

    def _buildUserDn(self, username):
        return ('uid=%s,%s' % (username, self.userbasedn))

    def _getGroupnameForGidnumber(self, conn, gidnumber):
        filterStr = self.groupfilter % {'gidnumber': gidnumber}
        if not conn.search(self.groupbasedn, filterStr, ldap3.LEVEL,
                           attributes=ldap3.ALL_ATTRIBUTES):
            return None
        try:
            return conn.response[0]['attributes']['cn'][0]
        except StandardError:
            return None

    def _getUserGroups(self, conn, username):
        filterStr = self.userfilter % {'username': username}
        if not conn.search(self.userbasedn, filterStr, ldap3.LEVEL,
                           attributes=ldap3.ALL_ATTRIBUTES):
            return []

        try:
            gidnumbers = [int(num) for num in
                          conn.response[0]['attributes']['gidNumber']]
        except StandardError:
            return []

        return [self._getGroupnameForGidnumber(conn, entry)
                for entry in gidnumbers]


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
                        level = USER  # limit passwordless entries to USER
                    return User(username, level)
                else:
                    raise AuthenticationError('Invalid username or password!')
        # check for unspecified user
        for (user, pw, level) in self.passwd:
            if user == '':
                if pw and pw == password:
                    if level > USER:
                        level = USER  # limit passworded anonymous to USER
                    return User(username, level)
                elif not pw:  # fix passwordless anonymous to GUEST
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
            import nicos._vendor.pam as pam
            import pwd
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
