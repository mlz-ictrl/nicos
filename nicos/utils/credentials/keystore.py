#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2017 by the NICOS contributors (see AUTHORS)
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
#   Bjoern Pedersen <bjoern.pedersen@frm2.tum.de>
#
# *****************************************************************************

"""
Utilility class to access and store credentials

The current implementation uses the :py:class:`EncryptedNicosKeyStore`, a file
based multi-keyring keystore as backend.

To set a password in the default store, run the keyring utility:

   `keyring -b nicos.utils.credentials.NicosKeyRing set <domain> <id>`

.. attention::
   Make sure to set the keystore key to 'nicos'.
   The default domain is 'nicos'

"""

from nicos import config

import os.path
from keyring.util import properties
from keyrings.alt.file import EncryptedKeyring


from . import NicosKeyStore


class NicosKeyRing(EncryptedKeyring):
    '''Keyring that allows easy setting of storage location
    '''

    def __init__(self, storepath=None):
        self.storepath = os.path.expanduser(storepath)

    @properties.NonDataProperty
    def file_path(self):
        if self.storepath:
            return os.path.join(self.storepath, self.filename)
        else:
            return NicosKeyRing.file_path(self)


class EncryptedNicosKeyStore(NicosKeyStore):
    '''Multi-keyring keystore

    This keystore uses multiple keyrings, but allows write access only to
    the last one in the list.
    '''

    storepathes = config.keystorepaths
    keyrings = []

    def __init__(self, storekey='nicos'):
        for sp in self.storepathes:
            ring = NicosKeyRing(sp)
            ring.keyring_key = storekey
            self.keyrings.append(ring)

    def getCredential(self, credid, domain='nicos'):
        for ring in self.keyrings:
            pw = ring.get_password(domain, credid)
            if pw:
                return pw
        return None

    def setCredential(self, credid, passwd, domain='nicos'):
        return self.keyrings[-1].set_password(domain, credid, passwd)

    def delCredential(self, credid, domain='nicos'):
        return self.keyrings[-1].delete_password(domain, credid)


nicoskeystore = EncryptedNicosKeyStore()
