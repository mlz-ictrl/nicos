#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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

from nicos.core import GUEST, USER, ADMIN, User
from nicos.services.daemon.auth import AuthenticationError, Authenticator as \
    BaseAuthenticator
import nicos._vendor.pam as pam
import pwd


class Authenticator(BaseAuthenticator):
    """Authenticates against PAM.

    This unfortunately only works against the local shadow database if the
    daemon runs as the root user.

    The access level info can be put into the "gecos" field.
    """

    def authenticate(self, username, password):
        try:
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
