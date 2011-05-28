#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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
# *****************************************************************************

name = 'devices for the detector'

includes = ['system']

devices = dict(
    timer    = device('nicos.virtual.VirtualTimer',
                      lowlevel = True),

    mon1     = device('nicos.virtual.VirtualCounter',
                      lowlevel = True,
                      type = 'monitor',
                      countrate = 1000),

    ctr1     = device('nicos.virtual.VirtualCounter',
                      lowlevel = True,
                      type = 'counter',
                      countrate = 2000),

    det      = device('nicos.detector.FRMDetector',
                      t  = 'timer',
                      m1 = 'ctr1',
                      m2 = None,
                      m3 = None,
                      z1 = 'mon1',
                      z2 = None,
                      z3 = None,
                      z4 = None,
                      z5 = None,
                      maxage = 3,
                      pollinterval = 0.5),
)
