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
#   Dominic Oram <dominic.oram@stfc.ac.uk>
#
# *****************************************************************************

description = 'Setup for the Ibex execution daemon'
group = 'special'

devices = dict(
    Auth=device('nicos.services.daemon.auth.list.Authenticator',
                hashing='sha1',
                # first entry is the user name, second the hashed password, third the user level
                passwd=[('ibex', 'a2eed0a7fcb214a497052435191b5264cca5b687', 'admin')],
                ),
    Daemon=device('nicos.services.daemon.NicosDaemon',
                  # Set the server to 'localhost' to only allow traffic from the local machine
                  # Set the server to the machine's IP to allow traffic from other machines
                  # Default port is 1301
                  server='127.0.0.1',
                  authenticators=['Auth'],
                  loglevel='info',
                  serializercls='nicos.protocols.daemon.classic.JsonSerializer',
                  servercls='nicos.services.daemon.proto.zeromq.Server',
                  ),
)
