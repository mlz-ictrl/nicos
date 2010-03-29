#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   NICOS test setup file with a few devices
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
#   The basic NICOS methods for the NICOS daemon (http://nicos.sf.net)
#
#   Copyright (C) 2009 Jens Krüger <jens.krueger@frm2.tum.de>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# *****************************************************************************

name = 'test setup with a few devices'

includes = ['system']

modules = ['nicm.commands']

devices = dict(
    m1 = device('nicm.testdev.VirtualMotor',
                loglevel = 'debug',
                initval = 1,
                absmin = 0,
                absmax = 100,
                unit = 'deg'),

    m2 = device('nicm.testdev.VirtualMotor',
                loglevel = 'debug',
                initval = 0.5,
                absmin = 0,
                absmax = 100,
                speed = 1,
                unit = 'deg'),

    c1 = device('nicm.testdev.VirtualCoder',
                motor = 'm1',
                unit = 'deg'),

    a1 = device('nicm.axis.Axis',
                autocreate = True,
                motor = 'm1',
                coder = 'c1',
                obs = ['c1'],
                absmin = 0,
                absmax = 100,
                usermin = 0,
                usermax = 50),

    a2 = device('nicm.axis.Axis',
                autocreate = True,
                motor = 'm2',
                coder = 'm2',
                obs = [],
                absmin = 0,
                absmax = 100,
                usermin = 0,
                usermax = 50),

    Power = device('taco.analog.Input',
                   description = 'FRM II reactor power',
                   #autocreate = True,
                   tacodevice = '//tacodb/frm2/reactor/power',
                   fmtstr = '%.1f',
                   unit = 'MW'),

    ctr1 = device('nicm.testdev.VirtualCounter',
                  countrate = 1000),
    ctr2 = device('nicm.testdev.VirtualCounter',
                  countrate = 2000),

    det = device('nicm.data.Detector',
                 components = ['ctr1', 'ctr2'],
                 autocreate = True),
)

startupcode = '''
print 'startup code executed'
'''
