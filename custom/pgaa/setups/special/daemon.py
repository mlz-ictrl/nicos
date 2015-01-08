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
#
# *****************************************************************************

description = 'setup for the execution daemon'
group = 'special'

import hashlib

devices = dict(
    UserDB = device('frm2.auth.Frm2Authenticator'),
    Auth   = device('services.daemon.auth.ListAuthenticator',
                    hashing = 'md5',
                    # first entry is the user name, second the hashed password, third the user level
                    passwd = [('guest', '', 'guest'),
                              ('user', hashlib.md5(b'user').hexdigest(), 'user'),
                              ('admin', hashlib.md5(b'admin').hexdigest(), 'admin')],
                   ),
    Daemon = device('services.daemon.NicosDaemon',
                    server = 'bunker.pgaa.frm2',
                    authenticators = ['Auth'], # or ['UserDB', 'Auth']
                    loglevel = 'info',
                   ),
)
