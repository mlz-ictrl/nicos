#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

description = 'checking detector environment conditions'

includes = ['system']

nethost = 'sans1srv.sans1.frm2'

devices = dict(
    tub_h1 = device('devices.taco.AnalogInput',
                     tacodevice = '//%s/sans1/tube/h1' % (nethost, ),
                     warnlimits = (0, 30),
                     fmtstr = '%.1f',
                     pollinterval = 60,
                     maxage = 120,
                   ),
    tub_h2 = device('devices.taco.AnalogInput',
                     tacodevice = '//%s/sans1/tube/h2' % (nethost, ),
                     warnlimits = (0, 30),
                     fmtstr = '%.1f',
                     pollinterval = 60,
                     maxage = 120,
                   ),
    tub_dew_1 = device('devices.taco.AnalogInput',
                       tacodevice = '//%s/sans1/tube/d1' % (nethost, ),
                       fmtstr = '%.1f',
                       pollinterval = 60,
                       maxage = 120,
                      ),
    tub_dew_2 = device('devices.taco.AnalogInput',
                       tacodevice = '//%s/sans1/tube/d2' % (nethost, ),
                       fmtstr = '%.1f',
                       pollinterval = 60,
                       maxage = 120,
                      ),
    tub_t1 = device('devices.taco.AnalogInput',
                     tacodevice = '//%s/sans1/tube/t1' % (nethost, ),
                     warnlimits = (None, 40),
                     fmtstr = '%.1f',
                     pollinterval = 60,
                     maxage = 120,
                   ),
    tub_t2 = device('devices.taco.AnalogInput',
                     tacodevice = '//%s/sans1/tube/t2' % (nethost, ),
                     warnlimits = (None, 40),
                     fmtstr = '%.1f',
                     pollinterval = 60,
                     maxage = 120,
                   ),
    tub_t3 = device('devices.taco.AnalogInput',
                     tacodevice = '//%s/sans1/tube/t3' % (nethost, ),
                     warnlimits = (None, 40),
                     fmtstr = '%.1f',
                     pollinterval = 60,
                     maxage = 120,
                   ),
    tub_t6 = device('devices.taco.AnalogInput',
                     tacodevice = '//%s/sans1/tube/t6' % (nethost, ),
                     warnlimits = (None, 30),
                     fmtstr = '%.1f',
                     pollinterval = 60,
                     maxage = 120,
                   ),
    tub_t7 = device('devices.taco.AnalogInput',
                     tacodevice = '//%s/sans1/tube/t7' % (nethost, ),
                     warnlimits = (None, 30),
                     fmtstr = '%.1f',
                     pollinterval = 60,
                     maxage = 120,
                   ),
    tub_v1 = device('devices.taco.AnalogInput',
                     tacodevice = '//%s/sans1/tube/v1' % (nethost, ),
                     warnlimits = (5.75, None),
                     fmtstr = '%.3f',
                     pollinterval = 60,
                     maxage = 120,
                   ),
    tub_v2 = device('devices.taco.AnalogInput',
                     tacodevice = '//%s/sans1/tube/v2' % (nethost, ),
                     warnlimits = (None, -5.75),
                     fmtstr = '%.3f',
                     pollinterval = 60,
                     maxage = 120,
                   ),
)
