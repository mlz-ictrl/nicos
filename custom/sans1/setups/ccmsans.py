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
#   Andreas Wilhelm <andreas.wilhelm@frm2.tum.de>
#
# *****************************************************************************

description = 'Sans1 Magnet'

group = 'plugplay'

includes = ['alias_B']

nethost = 'ccmsans.sans1.frm2'

devices = dict(
    A_ccmsans_left = device('devices.taco.CurrentSupply',
                            description = 'The left current loop',
                            tacodevice = '//%s/magnet/ips/1' % (nethost,),
                            abslimits = (-1, 160),
                            fmtstr = '%.3f',
                            maxage = 120,
                            pollinterval = 15,
                           ),
    A_ccmsans_right = device('devices.taco.CurrentSupply',
                             description = 'The right current loop',
                             tacodevice = '//%s/magnet/ips/2' % (nethost,),
                             abslimits = (-1, 160),
                             fmtstr = '%.3f',
                             maxage = 120,
                             pollinterval = 15,
                            ),
    B_ccmsans = device('sans1.ccmsans.AsymmetricMagnet',
                       description = 'The resulting magnetic field',
                       tacodevice = '//%s/magnet/oxford/magnet' % (nethost, ),
                       abslimits = (-5, 5),
                       fmtstr = '%.3f',
                       maxage = 120,
                       pollinterval = 15,
                       tacotimeout = 5,
                      ),
    ccmsans_T1 = device('devices.taco.AnalogInput',
                        description = 'Coldhead Stage 1',
                        tacodevice = '//%s/magnet/coldhead/stage1' % (nethost, ),
                        fmtstr = '%.3f',
                        maxage = 120,
                        pollinterval = 15,
                       ),
    ccmsans_T2 = device('devices.taco.AnalogInput',
                        description = 'Coldhead Stage 2',
                        tacodevice = '//%s/magnet/coldhead/stage2' % (nethost, ),
                        fmtstr = '%.3f',
                        maxage = 120,
                        pollinterval = 15,
                       ),
    ccmsans_T3 = device('devices.taco.AnalogInput',
                        description = 'Shield Top',
                        tacodevice = '//%s/magnet/shield/top' % (nethost, ),
                        fmtstr = '%.3f',
                        maxage = 120,
                        pollinterval = 15,
                       ),
    ccmsans_T4 = device('devices.taco.AnalogInput',
                        description = 'Shield Bottom',
                        tacodevice = '//%s/magnet/shield/bottom' % (nethost, ),
                        fmtstr = '%.3f',
                        maxage = 120,
                        pollinterval = 15,
                       ),
    ccmsans_T5 = device('devices.taco.AnalogInput',
                        description = 'Magnet Top Left',
                        tacodevice = '//%s/magnet/magnet/topleft' % (nethost, ),
                        fmtstr = '%.3f',
                        maxage = 120,
                        pollinterval = 15,
                       ),
    ccmsans_T6 = device('devices.taco.AnalogInput',
                        description = 'Magnet Top Right',
                        tacodevice = '//%s/magnet/magnet/topright' % (nethost, ),
                        fmtstr = '%.3f',
                        maxage = 120,
                        pollinterval = 15,
                       ),
    ccmsans_T7 = device('devices.taco.AnalogInput',
                        description = 'Magnet Bottom Right',
                        tacodevice = '//%s/magnet/magnet/bottomright' % (nethost, ),
                        fmtstr = '%.3f',
                        maxage = 120,
                        pollinterval = 15,
                       ),
    ccmsans_T8 = device('devices.taco.AnalogInput',
                        description = 'Magnet Bottom Left',
                        tacodevice = '//%s/magnet/magnet/bottomleft' % (nethost, ),
                        fmtstr = '%.3f',
                        maxage = 120,
                        pollinterval = 15,
                       ),
)
startupcode = """
B.alias = B_ccmsans
AddEnvironment(B)
"""
