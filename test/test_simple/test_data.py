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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""NICOS data manager test suite."""

from contextlib import contextmanager

from nicos.core import dataman, ProgrammingError

from test.utils import raises


def teardown_module():
    dataman.reset()


def test_empty_manager():
    # check for empty data stack
    assert dataman._stack == []
    assert dataman._current is None
    # check for empty scan cache
    dataman.reset()
    assert dataman._last_scans == []


def test_cleanup():
    # check that data manager cleans up unsuitable datasets still open
    dataman.beginPoint()
    dataman.beginPoint()
    assert len(dataman._stack) == 1
    dataman.finishPoint()


@contextmanager
def dataset_scope(settype, **kwds):
    getattr(dataman, 'begin' + settype.capitalize())(**kwds)
    yield
    getattr(dataman, 'finish' + settype.capitalize())()


def test_dataset_stack():
    # create some datasets on the stack, check nesting
    with dataset_scope('block'):
        assert raises(ProgrammingError, dataman.finishScan)
        assert raises(ProgrammingError, dataman.finishPoint)

        with dataset_scope('scan'):
            assert raises(ProgrammingError, dataman.finishBlock)

            with dataset_scope('point'):
                with dataset_scope('scan', subscan=True):
                    with dataset_scope('point'):
                        assert len(dataman._stack) == 5
                        assert [s.settype for s in dataman._stack] == \
                            ['block', 'scan', 'point', 'subscan', 'point']

                        ds = dataman._current
                        assert ds.pointnumber == 1

                    dataman.beginTemporaryPoint()
                    dataman.finishPoint()


def test_point_dataset():
    with dataset_scope('point'):
        ds = dataman._current

        # only assigned if scan is open
        assert ds.pointnumber is None

        # fresh dataset, nothing in there
        assert not ds.results
        assert not ds.values
        assert not ds._valuestats
        assert not ds.metainfo

        # now fill it with some device values
        for (ts, value) in [(0, 5.), (2, 7.), (3, 5.), (4, 4.)]:
            dataman.putValues({'dev': (ts, value)})
        dataman.putValues({'dev2': (2, 5.)})

        # check value stats for devices with multiple values
        mean, stdev, mini, maxi = ds.valuestats['dev']
        assert mini == 4.
        assert maxi == 7.
        assert mean == 5.5
        assert 0.866 < stdev < 0.867  # sqrt(3)/2

        # check value stats for devices with only one value
        mean, stdev, mini, maxi = ds.valuestats['dev2']
        assert mini == maxi == mean == 5.
        assert stdev == float('inf')
