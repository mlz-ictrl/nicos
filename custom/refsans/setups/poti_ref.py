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
#   Matthias Pomm <matthias.pomm@hzg.de>
#
# **************************************************************************

description = 'reference values for the encoder potiometers'

# not included by others
group = 'lowlevel'

nethost = 'refsanssrv.refsans.frm2'
tacodev = '//%s/test' % nethost

devices = dict(
    wegbox_A_1ref = device('nicos.devices.taco.AnalogInput',
                           description = 'wegbox_A_1ref',
                           tacodevice = '%s/WB_A/1_6' % tacodev,
                          ),
    wegbox_A_2ref = device('nicos.devices.taco.AnalogInput',
                           description = 'wegbox_A_2ref',
                           tacodevice = '%s/WB_A/2_6' % tacodev,
                          ),
    wegbox_B_1ref = device('nicos.devices.taco.AnalogInput',
                           description = 'wegbox_B_1ref',
                           tacodevice = '%s/WB_B/1_6' % tacodev,
                          ),
    wegbox_B_2ref = device('nicos.devices.taco.AnalogInput',
                           description = 'wegbox_B_2ref',
                           tacodevice = '%s/WB_B/2_6' % tacodev,
                          ),
    wegbox_C_1ref = device('nicos.devices.taco.AnalogInput',
                           description = 'wegbox_C_1ref',
                           tacodevice = '%s/WB_C/1_6' % tacodev,
                          ),
    wegbox_C_2ref = device('nicos.devices.taco.AnalogInput',
                           description = 'wegbox_C_2ref',
                           tacodevice = '%s/WB_C/2_6' % tacodev,
                          ),
)

startupcode = """
"""

