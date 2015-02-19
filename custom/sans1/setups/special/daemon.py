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

devices = dict(
    UserDB = device('frm2.proposaldb.Authenticator'),
    Auth   = device('services.daemon.auth.ListAuthenticator',
                    hashing = 'md5',
                    # first entry is the user name, second the hashed password, third the user level
                    passwd = [
                              ('guest', '', 'guest'),
                              ('user', 'ee11cbb19052e40b07aac0ca060c23ee', 'user'),
                              ('admin', 'ec326b6858b88a51ff1605197d664add', 'admin'),
                              ('andreas', 'da5121879fff54b08b69ec54d9ac2bf6', 'admin'),
                              ('ralph', 'e543fdb4737f66b96e764d7303a15ae8', 'admin'),
                              ('andre', '1b2bc04a135d959e8da04733e24195da', 'admin'),
                              ('sebastian', '6c79a7389f572813edfe5fc873e099ce', 'admin'),
                              ('edv', 'cb50179ebd60c94a29770c652a848765', 'admin'),
                              ],
                   ),
    Daemon = device('services.daemon.NicosDaemon',
                    server = 'sans1ctrl.sans1.frm2',
                    authenticators = ['UserDB', 'Auth'],
                    loglevel = 'debug',
                   ),
)
