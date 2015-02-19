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

tacodevice = '//sans1srv/sans1/network/selector'

devices = dict(
    selector_state = device('devices.vendor.astrium.SelectorState',
                      tacodevice = tacodevice,
                      lowlevel = True,
                      pollinterval = 10,
                      maxage = 35,
                      comtries = 9,
                     ),
    selector_rpm = device('devices.vendor.astrium.SelectorSpeed',
                          description = 'Selector speed control',
                          abslimits = (3100, 28300),
                          statedev = 'selector_state',
                          unit = 'rpm',
                          fmtstr = '%.0f',
                          timeout = 600,
                          warnlimits = (3099, 28300),
                          blockedspeeds = [(3600, 4500), (7800, 9900)],
                          precision = 6,
                          comdelay = 30,
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
                            ),
    selector_sspeed = device('devices.vendor.astrium.SelectorValue',
                             description = 'Selector speed read out by optical sensor',
                             statedev = 'selector_state',
                             valuename = 'SSPEED',
                             unit = 'Hz',
                             fmtstr = '%.1d',
                            ),
    selector_vacuum = device('devices.vendor.astrium.SelectorValue',
                             description = 'Vacuum in the selector',
                             statedev = 'selector_state',
                             valuename = 'VACUM',
                             unit = 'x1e-3 mbar',
                             fmtstr = '%.5f',
                             warnlimits = (0, 0.008), # selector shuts down above 0.005
                            ),
    selector_rtemp = device('devices.vendor.astrium.SelectorValue',
                            description = 'Temperature of the selector',
                            statedev = 'selector_state',
                            valuename = 'RTEMP',
                            unit = 'C',
                            fmtstr = '%.1f',
                            warnlimits = (10, 45),
                           ),
    selector_wflow = device('devices.vendor.astrium.SelectorValue',
                            description = 'Cooling water flow rate through selector',
                            statedev = 'selector_state',
                            valuename = 'WFLOW',
                            unit = 'l/min',
                            fmtstr = '%.1f',
                            warnlimits = (2.3, 10),#without rot temp sensor; old value (2.5, 10)
                           ),
    selector_winlt = device('devices.vendor.astrium.SelectorValue',
                            description = 'Cooling water temperature at inlet',
                            statedev = 'selector_state',
                            valuename = 'WINLT',
                            unit = 'C',
                            fmtstr = '%.1f',
                            warnlimits = (15, 28),
                           ),
    selector_woutt = device('devices.vendor.astrium.SelectorValue',
                            description = 'Cooling water temperature at outlet',
                            statedev = 'selector_state',
                            valuename = 'WOUTT',
                            unit = 'C',
                            fmtstr = '%.1f',
                            warnlimits = (15, 28),
                           ),
    selector_vibrt = device('devices.vendor.astrium.SelectorValue',
                            description = 'Selector vibration',
                            statedev = 'selector_state',
                            valuename = 'VIBRT',
                            unit = 'mm/s',
                            fmtstr = '%.2f',
                            warnlimits = (0, 1),
                           ),
)
