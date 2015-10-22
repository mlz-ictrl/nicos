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
#   Andreas Wilhelm <andreas.wilhelm@frm2.tum.de>
#
# *****************************************************************************

description = 'setup for the velocity selector'

group = 'lowlevel'

TANGO_BASE_URL = 'tango://sans1hw.sans1.frm2:10000/sans1/selector'

devices = dict(
    selector_rpm = device('devices.tango.WindowTimeoutAO',
                          description = 'Selector speed control',
                          tangodevice='%s/speed' % TANGO_BASE_URL,
                          abslimits = (3100, 28300),
                          unit = 'rpm',
                          fmtstr = '%.0f',
                          timeout = 600,
                          warnlimits = (3099, 28300),
                          precision = 6,
                          comdelay = 30,
                          maxage = 35,
                         ),
    selector_lambda = device('devices.vendor.astrium.SelectorLambda',
                             description = 'Selector center wavelength control',
                             seldev = 'selector_rpm',
                             unit = 'A',
                             fmtstr = '%.2f',
                             twistangle = 48.27,
                             length = 0.25,
                             beamcenter = 0.115, # antares value!, sans1 value unknown
                             maxspeed = 28300,
                             maxage = 35,
                            ),
    selector_sspeed = device('devices.tango.AnalogInput',
                             description = 'Selector speed read out by optical sensor',
                             tangodevice='%s/sspeed' % TANGO_BASE_URL,
                             unit = 'Hz',
                             fmtstr = '%.1d',
                             maxage = 35,
                            ),
    selector_vacuum = device('devices.tango.AnalogInput',
                             description = 'Vacuum in the selector',
                             tangodevice='%s/vacuum' % TANGO_BASE_URL,
                             unit = 'x1e-3 mbar',
                             fmtstr = '%.5f',
                             warnlimits = (0, 0.008), # selector shuts down above 0.005
                             maxage = 35,
                            ),
    selector_rtemp = device('devices.tango.AnalogInput',
                            description = 'Temperature of the selector',
                            tangodevice='%s/rotortemp' % TANGO_BASE_URL,
                            unit = 'C',
                            fmtstr = '%.1f',
                            warnlimits = (10, 45),
                            maxage = 35,
                           ),
    selector_wflow = device('devices.tango.AnalogInput',
                            description = 'Cooling water flow rate through selector',
                            tangodevice='%s/flowrate' % TANGO_BASE_URL,
                            unit = 'l/min',
                            fmtstr = '%.1f',
                            warnlimits = (2.3, 10),#without rot temp sensor; old value (2.5, 10)
                            maxage = 35,
                           ),
    selector_winlt = device('devices.tango.AnalogInput',
                            description = 'Cooling water temperature at inlet',
                            tangodevice='%s/waterintemp' % TANGO_BASE_URL,
                            unit = 'C',
                            fmtstr = '%.1f',
                            warnlimits = (15, 28),
                            maxage = 35,
                           ),
    selector_woutt = device('devices.tango.AnalogInput',
                            description = 'Cooling water temperature at outlet',
                            tangodevice='%s/waterouttemp' % TANGO_BASE_URL,
                            unit = 'C',
                            fmtstr = '%.1f',
                            warnlimits = (15, 28),
                            maxage = 35,
                           ),
    selector_vibrt = device('devices.tango.AnalogInput',
                            description = 'Selector vibration',
                            tangodevice='%s/vibration' % TANGO_BASE_URL,
                            unit = 'mm/s',
                            fmtstr = '%.2f',
                            warnlimits = (0, 1),
                            maxage = 35,
                           ),
)
