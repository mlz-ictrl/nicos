# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-present by the NICOS contributors (see AUTHORS)
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
#
# *****************************************************************************

"""Utilities to combine and parse user strings."""

from nicos.core.params import mailaddress


def combineUsers(users):
    """Combine user info into a string with known format."""
    res = []
    for user in users:
        userstr = user['name']
        if user.get('email'):
            userstr += ' <%s>' % user['email']
        if user.get('affiliation'):
            userstr += ' (%s)' % user['affiliation']
        res.append(userstr)
    return '; '.join(res)


def splitUsers(users_str):
    """Split string from the combineUsers() format."""
    users = []
    for userstr in users_str.split(';'):
        user = {}
        userstr = userstr.strip()
        if '(' in userstr and userstr.endswith(')'):
            userstr, _, affiliation = userstr[:-1].partition('(')
            user['affiliation'] = affiliation.strip()
            userstr = userstr.strip()
        if '<' in userstr and userstr.endswith('>'):
            userstr, _, email = userstr[:-1].partition('<')
            user['email'] = mailaddress(email)
        user['name'] = userstr.strip()
        users.append(user)
    return users
