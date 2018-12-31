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
#   Dominic Oram <dominic.oram@stfc.ac.uk>
#
# *****************************************************************************

description = 'Ibex System setup'

group = 'lowlevel'

modules = ['nicos.commands.basic', 'nicos_isis.ibex.genie_commands']

devices = dict(
    # NOTE: removing the FreeSpace device doens't hurt the daemon functionality.
    # However, the daemon seems to die slightly more gracefully on CTRL+C when
    # this device is present
    Space = device('nicos.devices.generic.FreeSpace',
                   description = 'The amount of free space for storing data',
                   path = None,
                   minfree = 5,
                  ),
)
