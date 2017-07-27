#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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

import warnings

from nicos.core import UsageError, PositionError, CommunicationError, \
    NicosError, ModeError
from nicos.core.scan import ContinuousScan

from nicos.commands.measure import count, live, avg, minmax, SetEnvironment
from nicos.commands.scan import scan, cscan, timescan, twodscan, contscan, \
    manualscan, sweep, appendscan
from nicos.commands.analyze import checkoffset
from nicos.commands.imaging import tomo
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

    try:
        # plain scan, with some extras: infostring, firstmove
        scan(m, 0, 1, 5, 0.005, 'test scan', manual=1)
        dataset = session.data._last_scans[-1]
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
        dataset = session.data._last_scans[-1]
        assert dataset.devvaluelists == [[float(i)] for i in [0, 4, 5]]

        # scan with multiple devices
        scan([m, m2], [0, 0], [1, 2], 3, t=0.)
        dataset = session.data._last_scans[-1]
        assert dataset.devvaluelists == [[float(i), float(i*2)] for i in [0, 1, 2]]

        # same with tuple arguments
        scan((m, m2), (0, 0), (1, 2), 2, t=0.)

        # scan with multiple devices and second basic syntax
        scan([m, m2], [[0, 0, 1], [4, 2, 1]], t=0.)
        dataset = session.data._last_scans[-1]
        assert dataset.devvaluelists == [[0., 4.], [0., 2.], [1., 1.]]

        # scan with different environment
        scan(m, [0, 1], c)
        dataset = session.data._last_scans[-1]
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

    try:
        session.experiment.setEnvironment([])

        # scan with different detectors
        scan(m, [0, 1], det, m=1, t=0.)
        dataset = session.data._last_scans[-1]
        assert dataset.devvaluelists == [[0.], [1.]]
        # 2 points, 5 detector channels
        assert len(dataset.detvaluelists) == 2
        assert len(dataset.detvaluelists[0]) == 5
        assert [v.name for v in dataset.detvalueinfo] == \
            ['timer', 'mon1', 'ctr1', 'ctr2', 'img.sum']

        # scan with multistep
        scan(m, [0, 1], det, manual=[3, 4], t=0.)
        dataset = session.data._last_scans[-1]
        assert dataset.devvaluelists == [[0., 3.], [0., 4.],
                                         [1., 3.], [1., 4.]]

    finally:
        session.experiment.envlist = []
        session.experiment.detlist = []


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


def test_scan_errorhandling(session):
    t = session.getDevice('tdev')
    m = session.getDevice('motor')

    # no errors, works fine
    scan(t, [0, 1, 2])
    dataset = session.data._last_scans[-1]
    assert dataset.devvaluelists == [[0], [1], [2]]

    # limit error: skips the data points
    scan(t, [-10, 0, 10, 3])
    dataset = session.data._last_scans[-1]
    assert dataset.devvaluelists == [[0], [3]]

    # communication error during move: also skips the data points
    t._value = 0
    t._start_exception = CommunicationError()
    scan(t, [0, 1, 2, 3])
    dataset = session.data._last_scans[-1]
    assert dataset.devvaluelists == [[0]]  # tdev.move only raises when target != 0

    # position error during move: ignored
    t._value = 0
    t._read_exception = None
    t._start_exception = PositionError()
    scan(t, [0, 1, 2, 3])
    dataset = session.data._last_scans[-1]
    assert dataset.devvaluelists == [[0], [None], [None], [None]]

    # position error during readout: ignored
    t._read_exception = PositionError()
    t._start_exception = None
    scan(t, [0, 1, 2, 3])
    dataset = session.data._last_scans[-1]
    assert dataset.devvaluelists == [[None], [None], [None], [None]]
    # also as an environment device
    scan(m, [0, 1], t)
    dataset = session.data._last_scans[-1]
    assert dataset.devvaluelists == [[0.], [1.]]
    assert dataset.envvaluelists == [[None], [None]]

    # other errors: reraised
    t._start_exception = RuntimeError()
    assert raises(RuntimeError, scan, t, [0, 1, 2, 3])


def test_cscan(session):
    m = session.getDevice('motor')
    cscan(m, 0, 1, 2)
    dataset = session.data._last_scans[-1]
    assert dataset.devvaluelists == [[-2.], [-1.], [0.], [1.], [2.]]


def test_sweeps(session):
    m = session.getDevice('motor')
    m.maw(1)
    timescan(5, m)
    dataset = session.data._last_scans[-1]
    assert len(dataset.devvaluelists) == 5
    assert dataset.envvaluelists[0][0] < 1
    assert dataset.envvaluelists[0][1] == 1.0

    sweep(m, 1, 5)
    dataset = session.data._last_scans[-1]
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
    dataset = session.data._last_scans[-1]
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
    with manualscan(mot):
        for i in range(3):
            mot.maw(i)
            count()
        assert raises(NicosError, manualscan)

    # with multistep
    SetEnvironment('slow_motor')
    try:
        with manualscan(mot, c, det, 'manscan', manual=[0, 1], t=0.1):
            for i in range(3):
                mot.maw(i)
                count()
    finally:
        SetEnvironment()
    dataset = session.data._last_scans[-1]
    assert dataset.info.startswith('manscan')
    # note: here, the env devices given in the command come first
    assert dataset.envvaluelists == [[0., 0., 0.], [0., 0., 0.],
                                     [1., 1., 0.], [1., 1., 0.],
                                     [2., 2., 0.], [2., 2., 0.]]


def test_specialscans(session):
    m = session.getDevice('motor')
    det = session.getDevice('det')

    checkoffset(m, 10, 0.05, 3, det, m=10, t=0.)

    dataset = session.data._last_scans[-1]
    uid = dataset.uid

    appendscan(5)
    dataset = session.data._last_scans[-1]
    assert dataset.continuation == [uid]
    uid2 = dataset.uid
    appendscan(-5)
    dataset = session.data._last_scans[-1]
    assert dataset.continuation == [uid2, uid]


def test_twodscan(session):
    m = session.getDevice('motor')
    m2 = session.getDevice('motor2')
    twodscan(m, 0, 1, 2, m2, 0, 1, 2, '2d')
    dataset = session.data._last_scans[-1]
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
