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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

description = 'setup for the velocity selector'

group = 'optional'

tango_host = 'tango://phys.biodiff.frm2:10000'
tango_url = '%s/biodiff/selector' % (tango_host,)


devices = dict(

    selector_speed  = device('devices.tango.AnalogOutput',
                             description = 'Selector speed control',
                             tangodevice = tango_url + '/speed',
                             unit = 'rpm',
                             fmtstr = '%.0f',
                             warnlimits = (11000, 22000),
                             abslimits = (11000, 22000),
                            ),

    selector_lambda = device('devices.vendor.astrium.SelectorLambda',
                             description = 'Selector wavelength control',
                             seldev = 'selector_speed',
                             unit = 'A',
                             fmtstr = '%.2f',
                             twistangle = 48.27,
                             length = 0.25,
                             beamcenter = 0.115,
                             maxspeed = 28300,
                            ),

    selector_rtemp  = device('devices.tango.AnalogInput',
                             description = 'Temperature of the selector rotor',
                             tangodevice = tango_url + '/rotortemp',
                             unit = 'C',
                             fmtstr = '%.1f',
                             warnlimits = (10, 45),
                            ),
    selector_winlt  = device('devices.tango.AnalogInput',
                             description = 'Cooling water temperature at inlet',
                             tangodevice = tango_url + '/waterintemp',
                             unit = 'C',
                             fmtstr = '%.1f',
                             warnlimits = (15, 20),
                            ),
    selector_woutt  = device('devices.tango.AnalogInput',
                             description = 'Cooling water temperature at outlet',
                             tangodevice = tango_url + '/waterouttemp',
                             unit = 'C',
                             fmtstr = '%.1f',
                             warnlimits = (15, 20),
                            ),
    selector_wflow  = device('devices.tango.AnalogInput',
                             description = 'Cooling water flow rate through selector',
                             tangodevice = tango_url + '/flowrate',
                             unit = 'l/min',
                             fmtstr = '%.1f',
                             warnlimits = (1.5, 10),
                            ),
    selector_vacuum = device('devices.tango.AnalogInput',
                             description = 'Vacuum in the selector',
                             tangodevice = tango_url + '/vacuum',
                             unit = 'mbar',
                             fmtstr = '%.5f',
                             warnlimits = (0, 0.005),
                            ),
    selector_vibrt  = device('devices.tango.AnalogInput',
                             description = 'Selector vibration',
                             tangodevice = tango_url + '/vibration',
                             unit = 'mm/s',
                             fmtstr = '%.2f',
                             warnlimits = (0, 0.6),
                            ),
)
