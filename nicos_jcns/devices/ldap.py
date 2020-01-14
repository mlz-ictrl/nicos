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
#   Alexander Steffens <a.steffens@fz-juelich.de>
#
# *****************************************************************************

from __future__ import absolute_import, division, print_function

from requests import get

from nicos import session
from nicos.services.daemon.auth.ldap import Authenticator as LDAPAuthenticator

from nicos_jcns.devices.sample import GETPUT_REQUEST_OK


class Authenticator(LDAPAuthenticator):
    """Device that ensures that the LDAP user already has an IFF sample
     database account after authenticating against the IFF LDAP server.
     """

    def authenticate(self, username, password):
        user = LDAPAuthenticator.authenticate(self, username, password)
        r = get(session.experiment.sampledb_url + 'users/me',
                auth=(username, password))
        if r.status_code != GETPUT_REQUEST_OK:
            session.log.error('could not log in to IFF sample database with '
                              'given credentials (user="%s")', username)
        else:
            user.data['ldap_id'] = r.json()['user_id']
        return user
