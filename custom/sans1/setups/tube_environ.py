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
# excludes = ['excluded']

nethost= '//sans1srv.sans1.frm2/'

devices = dict(
    tub_h1 = device('nicos.taco.AnalogInput',
                     tacodevice = nethost + 'sans1/tube/h1',
                     fmtstr = '%.1f',
                     pollinterval = 60,
                     maxage = 120,
                   ),
    tub_h2 = device('nicos.taco.AnalogInput',
                     tacodevice = nethost + 'sans1/tube/h2',
                     fmtstr = '%.1f',
                     pollinterval = 60,
                     maxage = 120,
                   ),
    tub_dew_1 = device('nicos.taco.AnalogInput',
                       tacodevice = nethost + 'sans1/tube/d1',
                       fmtstr = '%.1f',
                       pollinterval = 60,
                       maxage = 120,
                      ),
    tub_dew_2 = device('nicos.taco.AnalogInput',
                       tacodevice = nethost + 'sans1/tube/d2',
                       fmtstr = '%.1f',
                       pollinterval = 60,
                       maxage = 120,
                      ),
    tub_t1 = device('nicos.taco.AnalogInput',
                     tacodevice = nethost + 'sans1/tube/t1',
                     fmtstr = '%.1f',
                     pollinterval = 60,
                     maxage = 120,
                   ),
    tub_t2 = device('nicos.taco.AnalogInput',
                     tacodevice = nethost + 'sans1/tube/t2',
                     fmtstr = '%.1f',
                     pollinterval = 60,
                     maxage = 120,
                   ),
    tub_t3 = device('nicos.taco.AnalogInput',
                     tacodevice = nethost + 'sans1/tube/t3',
                     fmtstr = '%.1f',
                     pollinterval = 60,
                     maxage = 120,
                   ),
    tub_t6 = device('nicos.taco.AnalogInput',
                     tacodevice = nethost + 'sans1/tube/t6',
                     fmtstr = '%.1f',
                     pollinterval = 60,
                     maxage = 120,
                   ),
    tub_t7 = device('nicos.taco.AnalogInput',
                     tacodevice = nethost + 'sans1/tube/t7',
                     fmtstr = '%.1f',
                     pollinterval = 60,
                     maxage = 120,
                   ),
    tub_v1 = device('nicos.taco.AnalogInput',
                     tacodevice = nethost + 'sans1/tube/v1',
                     fmtstr = '%.3f',
                     pollinterval = 60,
                     maxage = 120,
                   ),
    tub_v2 = device('nicos.taco.AnalogInput',
                     tacodevice = nethost + 'sans1/tube/v2',
                     fmtstr = '%.3f',
                     pollinterval = 60,
                     maxage = 120,
                   ),
)

