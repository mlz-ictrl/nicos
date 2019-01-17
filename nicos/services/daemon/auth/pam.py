#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2019 by the NICOS contributors (see AUTHORS)
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

from __future__ import absolute_import, division, print_function

import pwd
import re

import pamela as pam

from nicos.core import ADMIN, GUEST, USER, User
from nicos.pycompat import to_utf8
from nicos.services.daemon.auth import AuthenticationError, \
    Authenticator as BaseAuthenticator

access_re = re.compile(r'access=(?P<level>\d+)')


class Authenticator(BaseAuthenticator):
    """Authenticates against PAM.

    This unfortunately only works against the local shadow database if the
    daemon runs as the root user.

    The access level info can be put into the "gecos" field.
    """

    def authenticate(self, username, password):
        try:
            pam.authenticate(username, password, resetcred=0)
            entry = pwd.getpwnam(username)
            idx = access_re.search(to_utf8(entry.pw_gecos))
            if idx:
                access = int(idx.group('level'))
                if access in (GUEST, USER, ADMIN):
                    return User(username, access)
            return User(username, ADMIN)
        except pam.PAMError as err:
            raise AuthenticationError('PAM authentication failed: %s' % err)
        except Exception as err:
            raise AuthenticationError('exception during PAM authentication: %s'
                                      % err)
