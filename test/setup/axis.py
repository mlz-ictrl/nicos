#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   NICOS test setup file for test_axis
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

name = 'test_axis setup'

includes = ['system']

devices = dict(
    motor = device(
        'nicm.testdev.VirtualMotor',
        unit = 'mm',
        initval = 0,
        absmin = -100,
        absmax = 100,
    ),

    coder = device(
        'nicm.testdev.VirtualCoder',
        motor = 'motor',
        unit = 'mm',
    ),

    axis = device(
        'nicm.axis.Axis',
        motor = 'motor',
        coder = 'coder',
        obs = [],
        usermin = -50,
        usermax = 50,
        loopdelay = 0.005,  # delay not necessary for virtual motor
    ),
)
