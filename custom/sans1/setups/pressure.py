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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

description = 'Vacuum sensors of detector and collimation tube'

group = 'lowlevel'

nethost = 'sans1srv.sans1.frm2'

devices = dict(
    det_tube = device('devices.taco.AnalogInput',
                      description = 'pressure detector tube: Tube',
                      tacodevice = '//%s/sans1/tube/p1' % (nethost, ),
                      fmtstr = '%.4G',
                      pollinterval = 15,
                      maxage = 60,
                      lowlevel = True,
                     ),
    det_nose = device('devices.taco.AnalogInput',
                      description = 'pressure detector tube: Nose',
                      tacodevice = '//%s/sans1/tube/p2' % (nethost, ),
                      fmtstr = '%.4G',
                      pollinterval = 15,
                      maxage = 60,
                      lowlevel = True,
                     ),
#    det_p3 = device('devices.taco.AnalogInput',
#                    description = 'pressure detector tube: NOT IN USE!!!',
#                    tacodevice = '//%s/sans1/tube/p3' % (nethost, ),
#                    fmtstr = '%.4G',
#                    pollinterval = 15,
#                    maxage = 60,
#                    lowlevel = True,
#                   ),
    coll_tube = device('devices.taco.AnalogInput',
                       description = 'pressure collimation tube: Tube',
                       tacodevice = '//%s/sans1/coll/p1' % (nethost, ),
                       fmtstr = '%.4G',
                       pollinterval = 15,
                       maxage = 60,
                       lowlevel = True,
                      ),
    coll_nose = device('devices.taco.AnalogInput',
                       description = 'pressure collimation tube: Nose',
                       tacodevice = '//%s/sans1/coll/p2' % (nethost, ),
                       fmtstr = '%.4G',
                       pollinterval = 15,
                       maxage = 60,
                       lowlevel = True,
                      ),
    coll_pump = device('devices.taco.AnalogInput',
                       description = 'pressure collimation tube: Pump',
                       tacodevice = '//%s/sans1/coll/p3' % (nethost, ),
                       fmtstr = '%.4G',
                       pollinterval = 15,
                       maxage = 60,
                       lowlevel = True,
                      ),
)
