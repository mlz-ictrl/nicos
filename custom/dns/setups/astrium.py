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

description = 'setup for the velocity selector'

group = 'optional'

#tango_host = 'tango://phys.dns.frm2:10000'
tango_host = 'tango://localhost:10000'
tango_url = '%s/dns/Selector' % (tango_host,)


devices = dict(

    selector_speed  = device('devices.tango.AnalogOutput',
                             description = 'Selector speed control',
                             tangodevice = tango_url + 'Speed/1',
                             unit = 'rpm',
                             fmtstr = '%.0f',
                             warnlimits = (0, 3600),
                            ),

    selector_rtemp  = device('devices.tango.AnalogInput',
                             description = 'Temperature of the selector rotor',
                             tangodevice = tango_url + 'Sensor/MotorTemp',
                             unit = 'C',
                             fmtstr = '%.1f',
                             warnlimits = (10, 45),
                            ),
    selector_winlt  = device('devices.tango.AnalogInput',
                             description = 'Cooling water temperature at inlet',
                             tangodevice = tango_url + 'Sensor/WaterInTemp',
                             unit = 'C',
                             fmtstr = '%.1f',
                             warnlimits = (15, 20),
                            ),
    selector_woutt  = device('devices.tango.AnalogInput',
                             description = 'Cooling water temperature at outlet',
                             tangodevice = tango_url + 'Sensor/WaterOutTemp',
                             unit = 'C',
                             fmtstr = '%.1f',
                             warnlimits = (15, 20),
                            ),
    selector_wflow  = device('devices.tango.AnalogInput',
                             description = 'Cooling water flow rate through selector',
                             tangodevice = tango_url + 'Sensor/FlowRate',
                             unit = 'l/min',
                             fmtstr = '%.1f',
                             warnlimits = (1.5, 10),
                            ),
    selector_vacuum = device('devices.tango.AnalogInput',
                             description = 'Vacuum in the selector',
                             tangodevice = tango_url + 'Sensor/Vacuum',
                             unit = 'x1e-3 mbar',
                             fmtstr = '%.5f',
                             warnlimits = (0, 0.005),
                            ),
    selector_vibrt  = device('devices.tango.AnalogInput',
                             description = 'Selector vibration',
                             tangodevice = tango_url + 'Sensor/Vibration',
                             unit = 'mm/s',
                             fmtstr = '%.2f',
                             warnlimits = (0, 1),
                            ),

    selector_lift   = device('devices.tango.Motor',
                             description = 'Selector lift',
                             tangodevice = '%s/dns/fzjs7/sel_lift' % tango_host,
                            ),
)
