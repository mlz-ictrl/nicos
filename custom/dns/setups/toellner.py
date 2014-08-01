#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2014 by the NICOS contributors (see AUTHORS)
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
# **************************************************************************

description = 'DNS digital in- and outputs'

group = 'optional'

_TANGO_HOST = 'tango://phys.dns.frm2:10000'
_TANGO_URL = _TANGO_HOST + '/dns/FZJDP_Digital/'
_POLCHANGE = {
                "+": 0,
                "-": 1,
              }

devices = dict(
    A         = device('dns.toellner.CurrentToellner',
                       description = 'Coil A',
                       tangodevice = '%s/dns/gpib/22' % _TANGO_HOST,
                       abslimits = (-3.2,3.2),
                       polchange = 'polch_A',
                       channel = 1,
                      ),
    polch_A   = device('devices.tango.NamedDigitalOutput',
                       description = 'Pole changer for coil A',
                       tangodevice = _TANGO_URL + 'Polum3',
                       mapping = _POLCHANGE,
                       lowlevel = True,
                      ),

    B         = device('dns.toellner.CurrentToellner',
                       description = 'Coil B',
                       tangodevice = '%s/dns/gpib/22' % _TANGO_HOST,
                       abslimits = (-3.2,3.2),
                       polchange = 'polch_B',
                       channel = 2,
                      ),
    polch_B   = device('devices.tango.NamedDigitalOutput',
                       description = 'Pole changer for coil B',
                       tangodevice = _TANGO_URL + 'Polum4',
                       mapping = _POLCHANGE,
                       lowlevel = True,
                      ),

    ZB        = device('dns.toellner.CurrentToellner',
                       description = 'Coil-Z Bottom',
                       tangodevice = '%s/dns/gpib/23' % _TANGO_HOST,
                       abslimits = (-5,5),
                       polchange = 'polch_ZB',
                       channel = 1,
                      ),
    polch_ZB  = device('devices.tango.NamedDigitalOutput',
                       description = 'Pole changer for coil Z Bottom',
                       tangodevice = _TANGO_URL + 'Polum5',
                       mapping = _POLCHANGE,
                       lowlevel = True,
                      ),

    ZT        = device('dns.toellner.CurrentToellner',
                       description = 'Coil-Z Top',
                       tangodevice = '%s/dns/gpib/23' % _TANGO_HOST,
                       abslimits = (-5,5),
                       polchange = 'polch_ZT',
                       channel = 2,
                      ),
    polch_ZT  = device('devices.tango.NamedDigitalOutput',
                       description = 'Pole changer for coil Z Top',
                       tangodevice = _TANGO_URL + 'Polum6',
                       mapping = _POLCHANGE,
                       lowlevel = True,
                      ),

    C         = device('dns.toellner.CurrentToellner',
                       description = 'Coil C',
                       tangodevice = '%s/dns/gpib/24' % _TANGO_HOST,
                       abslimits = (-3.2,3.2),
                       polchange = 'polch_C',
                       channel = 1,
                      ),
    polch_C   = device('devices.tango.NamedDigitalOutput',
                       description = 'Pole changer for coil C',
                       tangodevice = _TANGO_URL + 'Polum7',
                       mapping = _POLCHANGE,
                       lowlevel = True,
                      ),
)

startupcode = '''
'''
