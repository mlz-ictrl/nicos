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
#   Lydia Fleischhauer-Fuss <l.fleischhauer-fuss@fz-juelich.de>
#
# *****************************************************************************

description = 'DNS digital in- and outputs'

group = 'optional'

includes = []

tango_host = 'tango://phys.dns.frm2:10000'
tango_url = tango_host + '/dns/FZJDP_Digital/'

devices = dict(

    mccrystal_t1 = device('devices.tango.NamedDigitalOutput',
                          description = 'Monchromator crystal tilt 1',
                          tangodevice = tango_url + 'MCKristallKip1',
                          mapping = dict(start=1, stop=0),
                         ),
    mccrystal_t2 = device('devices.tango.NamedDigitalOutput',
                          description = 'Monchromator crystal tilt 2',
                          tangodevice = tango_url + 'MCKristallKip2',
                          mapping = dict(start=1, stop=0),
                         ),
    mccrystal_t3 = device('devices.tango.NamedDigitalOutput',
                          description = 'Monchromator crystal tilt 3',
                          tangodevice = tango_url + 'MCKristallKip3',
                          mapping = dict(start=1, stop=0),
                         ),
    mccrystal_t4 = device('devices.tango.NamedDigitalOutput',
                          description = 'Monchromator crystal tilt 4',
                          tangodevice = tango_url + 'MCKristallKip4',
                          mapping = dict(start=1, stop=0),
                         ),
    mccrystal_t5 = device('devices.tango.NamedDigitalOutput',
                          description = 'Monchromator crystal tilt 5',
                          tangodevice = tango_url + 'MCKristallKip5',
                          mapping = dict(start=1, stop=0),
                         ),
    mccrystal_t6 = device('devices.tango.NamedDigitalOutput',
                          description = 'Monchromator crystal tilt 6',
                          tangodevice = tango_url + 'MCKristallKip6',
                          mapping = dict(start=1, stop=0),
                         ),
    mccrystal_t7 = device('devices.tango.NamedDigitalOutput',
                          description = 'Monchromator crystal tilt 7',
                          tangodevice = tango_url + 'MCKristallKip7',
                          mapping = dict(start=1, stop=0),
                         ),
)

startupcode = '''
'''
