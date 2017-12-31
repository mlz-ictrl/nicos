#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2017-2018 by the NICOS contributors (see AUTHORS)
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
Utility classes to access and store credentials

"""


class NicosKeyStore(object):
    '''Abstract base class for nicos key stores
    '''

    def getCredential(self, credid, domain='nicos'):
        '''return a stored credential

        *credid*  The id /username for which we want to get the credential

        *domain*  The domain where we store the credential
        '''

        raise NotImplementedError

    def setCredential(self, credid, passwd, domain='nicos'):
        '''set a credential in the store

        *credid*  The id /username for which we want to set the credential

        *passwd*  The credential value to store, this can be any
            plain-text representable value

        *domain*  The domain where we store the credential
        '''

        raise NotImplementedError

    def delCredential(self, credid, domain='nicos'):
        '''delete a stored credential

        *credid*  The id /username for which we want to get the credential

        *domain*  The domain where we store the credential
        '''

        raise NotImplementedError
