#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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

description = 'detector related devices including beamstop'

includes = []

group = 'lowlevel'

nethost = 'sans1srv.sans1.frm2'

devices = dict(
    det1_t_ist = device('devices.taco.FRMTimerChannel',
                        tacodevice = '//%s/sans1/qmesydaq/timer' % (nethost, ),
                        fmtstr = '%.2f',
                        lowlevel = True,
                       ),

#   det1_t_ist = device('devices.taco.FRMTimerChannel',
#                       tacodevice = '//%s/sans1/qmesydaq/det' % (nethost, ),
#                       fmtstr = '%.1f',
#                       pollinterval = 1,
#                       maxage = 3,
#                       # lowlevel = True,
#                      ),

#   det1_t_soll = device('devices.taco.FRMTimerChannel',
#                        tacodevice = '//%s/sans1/qmesydaq/timer' % (nethost, ),
#                        fmtstr = '%.1f',
#                        pollinterval = 5,
#                        maxage = 13,
#                        # lowlevel = True,
#                       ),

    hv_interlock = device('devices.taco.DigitalInput',
                          tacodevice = '//%s/sans1/interlock/hv' % (nethost, ),
                          lowlevel = True,
                          ),
    hv_discharge_mode = device('devices.taco.DigitalInput',
                               tacodevice = '//%s/sans1/interlock/mode' % (nethost, ),
                               lowlevel = True,
                              ),
    hv_discharge = device('devices.taco.DigitalOutput',
                          tacodevice = '//%s/sans1/interlock/discharge' % (nethost, ),
                          lowlevel = True,
                         ),
    hv = device('devices.taco.VoltageSupply',
                tacodevice = '//%s/sans1/iseg/hv' % (nethost, ),
                abslimits = [0, 1530],
                maxage = 120,
                pollinterval = 15,
                fmtstr = '%d',
               ),
    hv_current = device('devices.taco.AnalogInput',
                        tacodevice = '//%s/sans1/iseg/hv-current' % (nethost, ),
                        maxage = 120,
                        pollinterval = 15,
                       ),

    det1_x1a = device('devices.taco.axis.Axis',
                      tacodevice = '//%s/sans1/detector1/x' % (nethost, ),
                      fmtstr = '%.1f',
                      abslimits = (4, 570),
                      maxage = 120,
                      pollinterval = 5,
                     ),
    det1_x1amot = device('devices.taco.motor.Motor',
                         tacodevice = '//%s/sans1/detector1/xmot' % (nethost, ),
                         fmtstr = '%.1f',
                         abslimits = (4, 570),
                       ),
    det1_x1aenc = device('devices.taco.coder.Coder',
                         tacodevice = '//%s/sans1/detector1/xenc' % (nethost, ),
                         fmtstr = '%.1f',
                        ),

    det1_z1a = device('devices.taco.axis.Axis',
                      tacodevice = '//%s/sans1/detector1/z' % (nethost, ),
                      fmtstr = '%.1f',
                      abslimits = (1100, 20000),
                      maxage = 120,
                      pollinterval = 5,
                     ),
    det1_z1amot = device('devices.taco.motor.Motor',
                         tacodevice = '//%s/sans1/detector1/zmot' % (nethost, ),
                         fmtstr = '%.1f',
                         abslimits = (1100, 20000),
                        ),
    det1_z1aenc = device('devices.taco.coder.Coder',
                         tacodevice = '//%s/sans1/detector1/zenc' % (nethost, ),
                         fmtstr = '%.1f',
                        ),

    det1_omega1a = device('devices.taco.axis.Axis',
                          tacodevice = '//%s/sans1/detector1/omega' % (nethost, ),
                          fmtstr = '%.1f',
                          abslimits = (-0.2, 21),
                          maxage = 120,
                          pollinterval = 5,
                         ),
    det1_omega1amot = device('devices.taco.motor.Motor',
                             tacodevice = '//%s/sans1/detector1/omegamot' % (nethost, ),
                             fmtstr = '%.1f',
                             abslimits = (-0.2, 21),
                            ),
    det1_omega1aenc = device('devices.taco.coder.Coder',
                             tacodevice = '//%s/sans1/detector1/omegaenc' % (nethost, ),
                             fmtstr = '%.1f',
                            ),

    bs1_x1a    = device('nicos.devices.generic.Axis',
                        motor = 'bs1_x1amot',
                        coder = 'bs1_x1aenc',
                        obs = [],
                        precision = 0.1,
                        fmtstr = '%.2f',
                        abslimits = (480, 860), #need to check
                       ),
    bs1_x1amot = device('devices.taco.motor.Motor',
                        tacodevice = '//%s/sans1/beamstop1/xmot' % (nethost, ),
                        fmtstr = '%.2f',
                        abslimits = (480, 860), #need to check
                       ),
    bs1_x1aenc = device('devices.taco.coder.Coder',
                        tacodevice = '//%s/sans1/beamstop1/xenc' % (nethost, ),
                        fmtstr = '%.1f',
                       ),
    bs1_y1a    = device('nicos.devices.generic.Axis',
                        motor = 'bs1_y1amot',
                        coder = 'bs1_y1aenc',
                        obs = [],
                        precision = 0.1,
                        fmtstr = '%.2f',
                        abslimits = (-120, 500), #need to check
                       ),
    bs1_y1amot = device('devices.taco.motor.Motor',
                        tacodevice = '//%s/sans1/beamstop1/ymot' % (nethost, ),
                        fmtstr = '%.1f',
                        abslimits = (-120, 500), #need to check
                       ),
    bs1_y1aenc = device('devices.taco.coder.Coder',
                        tacodevice = '//%s/sans1/beamstop1/yenc' % (nethost, ),
                        fmtstr = '%.2f',
                       ),

)
