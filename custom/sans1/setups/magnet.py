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

description = '5T SANS-1 magnet devices'

includes = ['system']

nethost= 'taco61.taco.frm2'

devices = dict(
    I     = device('sans1.mercury.OxfordMercury',
                   description = 'Magnet current',
                   tacodevice = '//%s/sans1/network/ips1' % (nethost,),
                   abslimits = (-24.19, 24.19),
                   ramplimit = 0.3,
                   unit = 'A',
                   fmtstr = '%.3f'
                  ),
    I2    = device('sans1.mercury.OxfordMercury',
                   description = 'Magnet current',
                   tacodevice = '//%s/sans1/network/ips2' % (nethost,),
                   abslimits = (-137.05, 137.05),
                   ramplimit = 1.71,
                   unit = 'A',
                   fmtstr = '%.3f'
                  ),
)

