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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#   Björn Pedersen <bjoern.pedersen@frm2.tum.de>
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

import hashlib
import shutil
import tempfile
from os import path

import pytest

from nicos.core import ADMIN, GUEST, USER, NicosError, User
from nicos.services.daemon.auth import AuthenticationError
from nicos.services.daemon.auth.list import Authenticator as ListAuthenticator
from nicos.services.daemon.auth.params import UserLevelAuthEntry, \
    UserPassLevelAuthEntry

try:
    from nicos.services.daemon.auth.keyring import \
        Authenticator as KeyringAuthenticator
except ImportError:
    KeyringAuthenticator = None
try:
    from nicos.utils.credentials.keystore import nicoskeystore
except ImportError:
    nicoskeystore = None
try:
    from nicos.services.daemon.auth.oauth2 import \
        Authenticator as OAuthAuthenticator
except ImportError:
    OAuthAuthenticator = None

session_setup = 'empty'


class TestUserPassLevelAuthEntry:

    @pytest.mark.parametrize(('inp', 'outp'), [
        [['user', 'passwd', 'user'], ('user', 'passwd', USER)],
        [['user', 'passwd', USER], ('user', 'passwd', USER)],
        [[' user ', 'passwd', USER], ('user', 'passwd', USER)],
        [['user', ' passwd ', USER], ('user', 'passwd', USER)],
    ], ids=str)
    def test_auth_entry(self, inp, outp):
        assert UserPassLevelAuthEntry(inp) == outp

    @pytest.mark.parametrize('inp', [
        (['user', 'passwd', 'xxx']),
        (['user', 'passwd', -1]),
        (['user', 'passwd', ()]),
        ([['user'], 'passwd', 'user']),
        (['user', ['passwd'], 'user']),
        (['user']),
        (['user', 'passwd']),
        (['user', 'passwd', USER, 'garbage']),
    ], ids=str)
    def test_wrong_auth_entry(self, inp):
        pytest.raises(ValueError, UserPassLevelAuthEntry, inp)


class TestUserLevelAuthEntry:

    @pytest.mark.parametrize(('inp', 'outp'), [
        [['user', 'user'], ('user', USER)],
        [['user', USER], ('user', USER)],
        [[' user ', USER], ('user', USER)],
    ], ids=str)
    def test_auth_entry(self, inp, outp):
        assert UserLevelAuthEntry(inp) == outp

    @pytest.mark.parametrize('inp', [
        (['user', 'xxx']),
        (['user', -1]),
        (['user', ()]),
        ([['user'], 'user']),
        (['user', 'passwd', USER]),
        (['user'])
    ], ids=str)
    def test_wrong_auth_entry(self, inp):
        pytest.raises(ValueError, UserLevelAuthEntry, inp)


@pytest.mark.skipif(OAuthAuthenticator is None,
                    reason='oauthlib packages not installed')
class TestOAuthAuthenticator:

    @pytest.fixture
    def OAuthAuth(self, request):
        Auth = OAuthAuthenticator('authenicator',
                                  tokenurl='https://unit.test/',
                                  clientid='')
        yield Auth

    def test_oauth_errors(self, session, OAuthAuth):
        pytest.raises(AuthenticationError, OAuthAuth.authenticate, 'user', '')


@pytest.fixture(scope='function')
def ListAuth(request):
    passwds = []
    for (user, pw, level) in request.function.passwd:
        # note: we currently allow empty password to match any password!
        # pylint: disable=compare-to-empty-string
        hashed = hashlib.sha1(pw.encode()).hexdigest() if pw != '' else pw
        passwds.append((user, hashed, level))

    Auth = ListAuthenticator('authenicator',
                             hashing='sha1',
                             passwd=passwds)
    yield Auth


def test_passwd_user(session, ListAuth):
    assert ListAuth.authenticate('user', 'user') == User('user', USER)
    assert ListAuth.authenticate('guest', '') == User('guest', GUEST)
    assert ListAuth.authenticate('guest', 'somepw') == User('guest', GUEST)
    pytest.raises(AuthenticationError, ListAuth.authenticate, 'user', 'nouser')
    pytest.raises(AuthenticationError, ListAuth.authenticate, 'joedoe', '')
    assert User('user', USER).data == {}
    assert User('guest', GUEST).data == {}


test_passwd_user.passwd = [('guest', '', 'guest'),
                           ('user', 'user', 'user'),
                           ('admin', 'admin', 'admin')]


def test_any_user(session, ListAuth):
    assert ListAuth.authenticate('user', 'user') == User('user', USER)
    assert ListAuth.authenticate('guest', '') == User('guest', GUEST)
    assert ListAuth.authenticate('joedoe', '') == User('joedoe', GUEST)
    assert ListAuth.authenticate('joedoe', '') != User('joedoe', USER)
    pytest.raises(AuthenticationError, ListAuth.authenticate, 'user', 'user_')
    assert User('user', USER).data == {}
    assert User('guest', GUEST).data == {}


test_any_user.passwd = [('guest', '', 'guest'),
                        ('', '', 'admin'),
                        ('user', 'user', 'user'),
                        ('admin', 'admin', 'admin')]


def test_empty_user(session, ListAuth):
    assert ListAuth.authenticate('joedoe', 'passwd') == User('joedoe', USER)
    assert User('joedoe', USER).data == {}


test_empty_user.passwd = [('admin', 'admin', 'admin'),
                          ('', 'passwd', 'admin')]


@pytest.fixture
def KeystoreAuth(request):
    nicoskeystore.storepathes[-1] = tempfile.mktemp(prefix='nicoskeystore')
    nicoskeystore.keyrings[-1].storepath = nicoskeystore.storepathes[-1]
    for user, cred in request.function.creds:
        nicoskeystore.setCredential(user, cred, domain='test_nicos_user')
    try:
        auth = KeyringAuthenticator('authenticator',
                                    access=[('admin', 'admin'),
                                            ('joedoe', 'user')],
                                    userdomain='test_nicos_user')
    except NicosError:
        pytest.skip('Keystore is not available')
    yield auth
    for user, _cred in request.function.creds:
        nicoskeystore.delCredential(user, domain='test_nicos_user')
    if path.isdir(nicoskeystore.keyrings[-1].storepath):
        shutil.rmtree(nicoskeystore.keyrings[-1].storepath)


@pytest.mark.skipif(KeyringAuthenticator is None,
                    reason='keyring packages not installed')
def test_keystore_auth(session, KeystoreAuth):
    assert KeystoreAuth.userdomain == 'test_nicos_user'

    assert KeystoreAuth.authenticate('admin', 'admin') == User('admin', ADMIN)
    assert KeystoreAuth.authenticate('joedoe', 'userpass') == User('joedoe', USER)
    pytest.raises(AuthenticationError, KeystoreAuth.authenticate, 'user', 'user_')
    pytest.raises(AuthenticationError, KeystoreAuth.authenticate, 'admin', 'user_')
    assert User('admin', ADMIN).data == {}
    assert User('joedoe', USER).data == {}


test_keystore_auth.creds = [('admin', 'admin'),
                            ('joedoe', 'userpass')]


@pytest.mark.skipif(nicoskeystore is None,
                    reason='keyring packages not installed')
def test_keystore_auth_nokeys(session, KeystoreAuth):
    pytest.raises(AuthenticationError, KeystoreAuth.authenticate, 'user', 'user_')
    pytest.raises(AuthenticationError, KeystoreAuth.authenticate, 'user', '')


test_keystore_auth_nokeys.creds = []
