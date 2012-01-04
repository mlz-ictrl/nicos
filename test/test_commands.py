#  -*- coding: utf-8 -*-
# *****************************************************************************
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
# Module authors:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""NICOS commands tests."""

from nicos import session
from nicos.core import UsageError, LimitError, ModeError

from nicos.commands.scan import scan
from nicos.commands.measure import count
from nicos.commands.device import move, maw

from nicos.commands.analyze import fwhm
from nicos.core import Value

from test.utils import raises

def setup_module():
    session.loadSetup('axis')
    session.setMode('master')

def teardown_module():
    session.unloadSetup()

def test_commands():
    motor = session.getDevice('motor')

    session.setMode('slave')
    assert raises(ModeError, scan, motor, [0, 1, 2, 10])

    session.setMode('master')
    scan(motor, [0, 1, 2, 10])

    assert raises(UsageError, count, motor)
    count()

    assert raises(LimitError, move, motor, max(motor.abslimits)+1)

    positions = (min(motor.abslimits), 0, max(motor.abslimits))
    for pos in positions:
        move(motor, pos)
        motor.wait()
        assert motor.curvalue == pos

    for pos in positions:
        maw(motor, pos)
        assert motor.curvalue == pos

def test_fwhm():
    import numpy
    data = numpy.array((1, 2, 1, 2, 2, 2, 5, 20, 30, 20, 10, 2, 3, 1, 2, 1, 1, 1))
    xpoints = numpy.arange(-9,9)
    assert len(data)== len(xpoints)
    dataset = session.experiment.createDataset(None)
    dataset.xvalueinfo= [Value('x','steps')]
    dataset.yvalueinfo= [Value('y','counts'),Value('y','counts')]
    dataset.xresults = [ [x] for x in xpoints]
    dataset.yresults = [ [y] for y in data]

    print dataset.xresults
    session.experiment._last_datasets.append(dataset)

    result=fwhm(1,1)
    print result
    assert result == (2.75, -1, 30, 1)
