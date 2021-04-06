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
#   Petr Cermak <cermak@mag.mff.cuni.cz>
#
# *****************************************************************************

from nicos.core import USER, Param, User
from nicos.services.daemon.auth import AuthenticationError, \
    Authenticator as BaseAuthenticator
from nicos.utils.credentials.keystore import nicoskeystore

from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session


class Authenticator(BaseAuthenticator):
    """Authenticates against oAuth2 server via Password Grant type.
    """

    parameters = {
        'tokenurl': Param('OAuth server token url to authenticate',
                          type=str),
        'clientid': Param('OAuth client id',
                          type=str),
        'keystoretoken': Param('Id used in the keystore for the OAuth client '
                               'secret',
                               type=str, default='oauth2server'),
    }

    def authenticate(self, username, password):
        secret = nicoskeystore.getCredential(self.keystoretoken)
        error = None
        try:
            oauth = OAuth2Session(
                client=LegacyApplicationClient(client_id=self.clientid))
            token = oauth.fetch_token(
                token_url=self.tokenurl, username=username, password=password,
                client_id=self.clientid, client_secret=secret)
        except Exception as err:
            # this avoids leaking credential details via tracebacks
            error = str(err)
        if error:
            raise AuthenticationError('exception during authenticate(): %s'
                                      % error)
        if not oauth.authorized:
            raise AuthenticationError('wrong password')
        return User(username, USER,
                    {'token': token, 'clientid': self.clientid})
