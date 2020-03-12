#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

"""NICOS tests for nicos.commands.scan and nicos.core.scan modules."""

from __future__ import absolute_import, division, print_function

import warnings

import pytest

from nicos.commands.analyze import checkoffset
from nicos.commands.imaging import tomo
from nicos.commands.measure import SetEnvironment, avg, count, live, minmax
from nicos.commands.scan import appendscan, contscan, cscan, manualscan, \
    scan, sweep, timescan, twodscan
from nicos.core import CommunicationError, ModeError, NicosError, \
    PositionError, UsageError
from nicos.core.acquire import CountResult
from nicos.core.scan import ContinuousScan
from nicos.core.sessions.utils import MASTER, SLAVE
from nicos.core.status import BUSY, OK
from nicos.core.utils import waitForState

from test.utils import raises

# this can happen during fitting, just don't print it out
warnings.filterwarnings('ignore', 'Covariance of the parameters could not '
                        'be estimated')

session_setup = 'scanning'


def test_scan(session, log):
    m = session.getDevice('motor')
    m2 = session.getDevice('motor2')
    c = session.getDevice('coder')
    mm = session.getDevice('manual')
    mm.move(0)

    # check that scans are impossible in slave mode
    session.setMode(SLAVE)
    assert raises(ModeError, scan, m, [0, 1, 2, 10])
    session.setMode(MASTER)

    session.experiment.setDetectors([session.getDevice('det')])
    session.experiment.setEnvironment([avg(mm), minmax(mm)])

    dataman = session.experiment.data
    try:
        # plain scan, with some extras: infostring, firstmove
        scan(m, 0, 1, 5, 0.005, 'test scan', manual=1)
        dataset = dataman.getLastScans()[-1]
        assert [v.name for v in dataset.devvalueinfo] == ['motor']
        assert [v.unit for v in dataset.devvalueinfo] == ['mm']
        assert dataset.devvaluelists == [[float(i)] for i in range(5)]
        assert [v.name for v in dataset.detvalueinfo] == \
            ['timer', 'mon1', 'ctr1', 'ctr2', 'img.sum']
        assert [v.unit for v in dataset.detvalueinfo] == \
            ['s', 'cts', 'cts', 'cts', 'cts']
        assert dataset.info.startswith('test scan')
        assert len(dataset.detvaluelists) == 5
        assert len(dataset.envvaluelists[0]) == 3
        assert dataset.envvaluelists[0] == [1., 1., 1.]  # avg, min, max
        assert mm.read() == 1

        session.experiment.setEnvironment([])

        # scan with second basic syntax
        scan(m, [0, 4, 5], 0.)
        dataset = dataman.getLastScans()[-1]
        assert dataset.devvaluelists == [[float(i)] for i in [0, 4, 5]]

        # scan with multiple devices
        scan([m, m2], [0, 0], [1, 2], 3, t=0.)
        dataset = dataman.getLastScans()[-1]
        assert dataset.devvaluelists == [[float(i), float(i*2)] for i in [0, 1, 2]]

        # same with tuple arguments
        scan((m, m2), (0, 0), (1, 2), 2, t=0.)

        # scan with multiple devices and second basic syntax
        scan([m, m2], [[0, 0, 1], [4, 2, 1]], t=0.)
        dataset = dataman.getLastScans()[-1]
        assert dataset.devvaluelists == [[0., 4.], [0., 2.], [1., 1.]]

        # scan with different environment
        scan(m, [0, 1], c)
        dataset = dataman.getLastScans()[-1]
        assert dataset.devvaluelists == [[0.], [1.]]
        assert dataset.envvaluelists == [[0.], [1.]]
        assert dataset.devvalueinfo[0].name == 'motor'
        assert dataset.devvalueinfo[0].unit == 'mm'
        assert dataset.envvalueinfo[0].name == 'coder'
        assert dataset.envvalueinfo[0].unit == 'mm'

    finally:
        session.experiment.envlist = []
        session.experiment.detlist = []


def test_scan2(session):
    m = session.getDevice('motor')
    det = session.getDevice('det')
    mm = session.getDevice('manual')
    mm.move(0)

    session.experiment.setDetectors([session.getDevice('det')])

    dataman = session.experiment.data
    try:
        session.experiment.setEnvironment([])

        # scan with different detectors
        scan(m, [0, 1], det, m=1, t=0.)
        dataset = dataman.getLastScans()[-1]
        assert dataset.devvaluelists == [[0.], [1.]]
        # 2 points, 5 detector channels
        assert len(dataset.detvaluelists) == 2
        assert len(dataset.detvaluelists[0]) == 5
        assert [v.name for v in dataset.detvalueinfo] == \
            ['timer', 'mon1', 'ctr1', 'ctr2', 'img.sum']

        # scan with multistep
        scan(m, [0, 1], det, manual=[3, 4], t=0.)
        dataset = dataman.getLastScans()[-1]
        assert dataset.devvaluelists == [[0., 3.], [0., 4.],
                                         [1., 3.], [1., 4.]]

    finally:
        session.experiment.envlist = []
        session.experiment.detlist = []


def test_scan_plotindex(session):
    m = session.getDevice('motor')
    m2 = session.getDevice('motor2')
    mm = session.getDevice('manual')
    mm.move(0)

    dataman = session.experiment.data
    session.experiment.setDetectors([session.getDevice('det')])
    # first device is moving
    scan([m, m2], [0, 0], [2, 0], 2, t=0)
    assert dataman.getLastScans()[-1].xindex == 0
    # second device is moving
    scan([m, m2], [0, 0], [0, 2], 2, t=0)
    assert dataman.getLastScans()[-1].xindex == 1
    # second device is moving, with multistep (issue #4030, #4031)
    scan([m, m2], [0, 0], [0, 2], 2, t=0., manual=[1, 2])
    assert dataman.getLastScans()[-1].xindex == 1
    # degenerate case only multistep moving, with multistep (issue #4030, #4031)
    scan([m, m2], [0, 0], [0, 0], 2, t=0., manual=[1, 2])
    assert dataman.getLastScans()[-1].xindex == 0


def test_scan_usageerrors(session):
    m = session.getDevice('motor')
    m2 = session.getDevice('motor2')

    # not enough arguments
    assert raises(UsageError, scan, m)
    assert raises(UsageError, scan, m, 0, 1)
    assert raises(UsageError, scan, [m, m2], [0, 1])
    assert raises(UsageError, scan, [m, m2], [0, 1], [0.1, 0.2])
    # start/step must be lists for multidevice
    assert raises(UsageError, scan, [m, m2], 0)
    assert raises(UsageError, scan, [m, m2], [0, 1], 0.1, 1)
    # start/step must be of equal length
    assert raises(UsageError, scan, [m, m2], [0, 1], [0.1, 0.2, 0.3], 1)
    # as must individual value lists
    assert raises(UsageError, scan, [m, m2], [[0, 1], [0.1, 0.2, 0.3]])
    # as must multistep lists
    assert raises(UsageError, scan, m, 0, 1, 1, motor=[1, 2], motor2=[3, 4, 5])
    # unsupported scan argument
    assert raises(UsageError, scan, m, 0, 1, 1, {})


def test_scan_invalidpreset(session, log):
    m = session.getDevice('motor')
    # invalid preset
    session.experiment.setDetectors([session.getDevice('det')])
    with log.assert_warns('these preset keys were not recognized by any of '
                          'the detectors: .*'):
        scan(m, 0, 1, 1, preset=5, t=0.)


def test_scan_errorhandling(session, log):
    t = session.getDevice('tdev')
    m = session.getDevice('motor')

    dataman = session.experiment.data
    # no errors, works fine
    scan(t, [0, 1, 2])
    dataset = dataman.getLastScans()[-1]
    assert dataset.devvaluelists == [[0], [1], [2]]

    with log.allow_errors():
        # limit error: skips the data points
        scan(t, [-10, 0, 10, 3])
        dataset = dataman.getLastScans()[-1]
        assert dataset.devvaluelists == [[0], [3]]

        # communication error during move: also skips the data points
        t._value = 0
        t._start_exception = CommunicationError()
        scan(t, [0, 1, 2, 3])
        dataset = dataman.getLastScans()[-1]
        assert dataset.devvaluelists == [[0]]  # tdev.move only raises when target != 0

        # position error during move: ignored
        t._value = 0
        t._read_exception = None
        t._start_exception = PositionError()
        scan(t, [0, 1, 2, 3])
        dataset = dataman.getLastScans()[-1]
        assert dataset.devvaluelists == [[0], [None], [None], [None]]

        # position error during readout: ignored
        t._read_exception = PositionError()
        t._start_exception = None
        scan(t, [0, 1, 2, 3])
        dataset = dataman.getLastScans()[-1]
        assert dataset.devvaluelists == [[None], [None], [None], [None]]
        # also as an environment device
        scan(m, [0, 1], t)
        dataset = dataman.getLastScans()[-1]
        assert dataset.devvaluelists == [[0.], [1.]]
        assert dataset.envvaluelists == [[None], [None]]

        # other errors: reraised
        t._start_exception = RuntimeError()
        assert raises(RuntimeError, scan, t, [0, 1, 2, 3])


def test_cscan(session):
    m = session.getDevice('motor')
    cscan(m, 0, 1, 2)
    dataman = session.experiment.data
    dataset = dataman.getLastScans()[-1]
    assert dataset.devvaluelists == [[-2.], [-1.], [0.], [1.], [2.]]


def test_sweeps(session):
    m = session.getDevice('motor')
    m.maw(1)
    timescan(5, m)
    dataman = session.experiment.data
    dataset = dataman.getLastScans()[-1]
    assert len(dataset.devvaluelists) == 5
    assert dataset.envvaluelists[0][0] < 1
    assert dataset.envvaluelists[0][1] == 1.0

    sweep(m, 1, 5)
    dataset = dataman.getLastScans()[-1]
    assert dataset.envvaluelists[-1][0] == 5


def test_contscan(session):
    m = session.getDevice('motor')
    mm = session.getDevice('manual')
    ContinuousScan.DELTA = 0.1
    session.experiment.detlist = [session.getDevice('det')]
    try:
        contscan(m, 0, 2, 10)
    finally:
        ContinuousScan.DELTA = 1.0
        session.experiment.detlist = []
    assert m.speed == 0  # reset to old value
    dataman = session.experiment.data
    dataset = dataman.getLastScans()[-1]
    assert dataset.devvaluelists
    assert all(0 <= res[0] <= 2 for res in dataset.devvaluelists)
    # no speed parameter
    assert raises(UsageError, contscan, mm, 0, 2)
    # preset and multistep not allowed
    assert raises(UsageError, contscan, m, 0, 2, 2, t=1)
    assert raises(UsageError, contscan, m, 0, 2, 2, manual=[0, 1])


def test_manualscan(session):
    mot = session.getDevice('motor')
    c = session.getDevice('coder')
    det = session.getDevice('det')
    mm = session.getDevice('manual')
    mm.maw(0)
    slow_motor = session.getDevice('slow_motor')
    slow_motor.maw(0)

    # normal
    with manualscan(mot, det, t=0.):
        assert mot in session._manualscan._envlist
        for i in range(3):
            mot.maw(i)
            count_result = count()
        assert raises(NicosError, manualscan)

    assert isinstance(count_result, CountResult) and len(count_result) == 5

    # with multistep
    SetEnvironment('slow_motor')
    try:
        with manualscan(mot, c, det, 'manscan', manual=[0, 1], t=0.):
            assert c in session._manualscan._envlist
            for i in range(3):
                mot.maw(i)
                count_result = count()
    finally:
        SetEnvironment()
    dataman = session.experiment.data
    dataset = dataman.getLastScans()[-1]
    assert dataset.info.startswith('manscan')
    # note: here, the env devices given in the command come first
    assert dataset.envvaluelists == [[0., 0., 0.], [0., 0., 0.],
                                     [1., 1., 0.], [1., 1., 0.],
                                     [2., 2., 0.], [2., 2., 0.]]

    assert isinstance(count_result, list)
    assert isinstance(count_result[0], CountResult)


def test_checkoffset(session):
    m = session.getDevice('motor')
    det = session.getDevice('det')

    checkoffset(m, 10, 0.05, 3, det, m=10, t=0.)


def test_appendscan(session):
    m1 = session.getDevice('motor')
    m2 = session.getDevice('motor2')
    det = session.getDevice('det')

    scan(m1, 0, 1, 3, det, t=0.)
    dataman = session.experiment.data
    dataset1 = dataman.getLastScans()[-1]
    assert dataset1.startpositions == [[0], [1], [2]]

    appendscan(3, 2)
    dataset2 = dataman.getLastScans()[-1]
    assert dataset2.continuation == [dataset1.uid]
    assert dataset2.startpositions == [[4], [6], [8]]

    appendscan(-3)
    dataset3 = dataman.getLastScans()[-1]
    assert dataset3.continuation == [dataset2.uid, dataset1.uid]
    assert dataset3.startpositions == [[-1], [-2], [-3]]

    appendscan(-3)
    dataset4 = dataman.getLastScans()[-1]
    assert dataset4.continuation == [dataset3.uid, dataset2.uid, dataset1.uid]
    assert dataset4.startpositions == [[-4], [-5], [-6]]

    scan([m2, m1], [0, 10], [1, 2], 3, det, t=0.)

    appendscan(3)
    dataset5 = dataman.getLastScans()[-1]
    assert dataset5.startpositions == [[3, 16], [4, 18], [5, 20]]

    appendscan(3, [0, 1])
    dataset5 = dataman.getLastScans()[-1]
    assert dataset5.startpositions == [[5, 21], [5, 22], [5, 23]]


def test_twodscan(session):
    m = session.getDevice('motor')
    m2 = session.getDevice('motor2')
    twodscan(m, 0, 1, 2, m2, 0, 1, 2, '2d')
    dataman = session.experiment.data
    dataset = dataman.getLastScans()[-1]
    assert dataset.info.startswith('2d')
    assert dataset.subsets[0].devvaluelist == [0.]
    assert dataset.subsets[0].envvaluelist == [1.]
    assert dataset.subsets[1].devvaluelist == [1.]
    assert dataset.subsets[1].envvaluelist == [1.]


def test_tomo(session):
    sry = session.getDevice('sry')
    sry.maw(0.0)
    tomo(10)
    assert sry.read() == 360.0

    sry.maw(0.0)
    tomo(10, sry)
    assert sry.read() == 360.0

    # use more than one moveable
    sry.maw(0.0)
    tomo(10, [sry, sry])
    assert sry.read() == 360.0

    # more than one picture per position
    sry.maw(0.0)
    tomo(10, sry, 2)
    assert sry.read() == 360.0

    # start not with the 180 deg picture
    sry.maw(0.0)
    tomo(10, sry, 2, False)
    assert sry.read() == 360.0

    # use a different detector
    det = session.getDevice('det')
    sry.maw(0.0)
    tomo(10, sry, 2, True, det, t=0.)
    assert sry.read() == 360.0

    # ref_first parameter is a detector device
    sry.maw(0.0)
    tomo(10, sry, 1, det, t=0.)
    assert sry.read() == 360.0

    # continue tomo
    sry.maw(0.0)
    tomo(10, sry, start=321.)
    assert sry.read() == 360.0


@pytest.mark.timeout(timeout=60, method='thread', func_only=True)
def test_live_count(session):
    det = session.getDevice('det')
    m = session.getDevice('motor')

    def _go_live(det):
        live(det)
        waitForState(det, BUSY)

    _go_live(det)
    det.stop()
    waitForState(det, OK)
    session._thd_acquire.join()

    _go_live(det)
    waitForState(det, BUSY)
    count(det, t=0)

    _go_live(det)
    waitForState(det, BUSY)
    scan(m, [0, 4, 5], 0., det)

    count(t=0)
    _go_live(det)
    count()  # t=0
    count()  # t=0
    scan(m, [0, 4, 5], 0., det, live=1)  # live will be ignored
