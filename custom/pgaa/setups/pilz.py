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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

description = 'Pilz box'

group = 'basic'

includes = []

nethost= 'pgaasrv.pgaa.frm2'

devices = dict(

    shutter = device('pgaa.pilz.Switch',
                     description = 'secondary experiment shutter',
                     tacodevice = '//%s/pgaa/pilz/shutter' % (nethost,),
                     readback = '//%s/pgaa/pilz/ishutter' % (nethost,),
                     error = '//%s/pgaa/pilz/eshutter' % (nethost,),
                     remote = '//%s/pgaa/pilz/erc' % (nethost,),
                     mapping = {'closed': 2, 'open': 1},
                    ),

    att1 = device('pgaa.pilz.Switch',
                  description = 'attenuator 1',
                  tacodevice = '//%s/pgaa/pilz/satt1' % (nethost,),
                  error = '//%s/pgaa/pilz/eatt1' % (nethost,),
                  readback = '//%s/pgaa/pilz/iatt1' % (nethost,),
                  remote = '//%s/pgaa/pilz/erc' % (nethost,),
                  mapping = {'out': 0, 'in': 1},
                 ),

    att2 = device('pgaa.pilz.Switch',
                  description = 'attenuator 2',
                  tacodevice = '//%s/pgaa/pilz/satt2' % (nethost,),
                  error = '//%s/pgaa/pilz/eatt2' % (nethost,),
                  readback = '//%s/pgaa/pilz/iatt2' % (nethost,),
                  remote = '//%s/pgaa/pilz/erc' % (nethost,),
                  mapping = {'out': 0, 'in': 1},
                 ),

    att3 = device('pgaa.pilz.Switch',
                  description = 'attenuator 3',
                  tacodevice = '//%s/pgaa/pilz/satt3' % (nethost,),
                  error = '//%s/pgaa/pilz/eatt3' % (nethost,),
                  readback = '//%s/pgaa/pilz/iatt3' % (nethost,),
                  remote = '//%s/pgaa/pilz/erc' % (nethost,),
                  mapping = {'out': 0, 'in': 1},
                 ),
)
