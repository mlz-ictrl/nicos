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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# **************************************************************************

# to be included by nok1
group = 'lowlevel'

nethost = 'refsanssrv.refsans.frm2'

description = 'IPC Motor bus device configuration'

includes = []

# data from instrument.inf
# used for:
# - nok4 reactor side (addr 0x36)
# - zb0 (addr 0x37)
# - zb1 (addr 0x38)
#

devices = dict(
    nokbus2 = device('devices.vendor.ipc.IPCModBusTaco',
                      tacodevice = '//%s/test/ipcsms/2' % (nethost,),
                      loglevel = 'info',
                      lowlevel = True,
                      bustimeout = 0.5,
            ),
)
