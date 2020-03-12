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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""NICOS data manager test suite."""

from __future__ import absolute_import, division, print_function

from contextlib import contextmanager

from nicos.commands.measure import count

session_setup = 'data'


def test_cleanup(session):
    # check that data manager cleans up unsuitable datasets still open
    dataman = session.experiment.data
    dataman.beginPoint()
    dataman.beginPoint()
    assert len(dataman._stack) == 1
    dataman.finishPoint()


@contextmanager
def dataset_scope(session, settype, **kwds):
    dataman = session.experiment.data
    getattr(dataman, 'begin' + settype.capitalize())(**kwds)
    yield dataman._current
    getattr(dataman, 'finish' + settype.capitalize())()


def test_dataset_stack(session, log):
    dataman = session.experiment.data
    session.experiment.new(0, user='user')
    # create some datasets on the stack, check nesting
    with dataset_scope(session, 'block') as blockset:
        with log.assert_warns('no scan to finish'):
            dataman.finishScan()
        with log.assert_warns('no data point to finish'):
            dataman.finishPoint()

        with dataset_scope(session, 'scan') as scanset:
            with log.assert_warns('no block to finish'):
                dataman.finishBlock()
            assert dataman._current.number == 1

            with dataset_scope(session, 'point') as pointset:
                assert list(dataman.iterParents(pointset)) == \
                    [scanset, blockset]

                with dataset_scope(session, 'scan', subscan=True):
                    with dataset_scope(session, 'point'):
                        assert len(dataman._stack) == 5
                        assert [s.settype for s in dataman._stack] == \
                            ['block', 'scan', 'point', 'subscan', 'point']

                        assert dataman._current.number == 1

                    with dataset_scope(session, 'point'):
                        assert dataman._current.number == 2


def test_empty_manager(session):
    dataman = session.experiment.data
    # check for empty data stack
    assert dataman._stack == []
    assert dataman._current is None
    # check for empty scan cache
    dataman.reset_all()
    assert dataman.getLastScans() == []


def test_temp_point(session):
    dataman = session.experiment.data
    dataman.beginTemporaryPoint()
    assert dataman._current.handlers == []
    dataman.finishPoint()


def test_point_dataset(session):
    dataman = session.experiment.data
    assert len(dataman._stack) == 0  # pylint: disable=len-as-condition
    with dataset_scope(session, 'point'):
        ds = dataman._current

        # only assigned if a parent dataset is open
        assert ds.number == 0

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


def test_force_scandata(session):
    dataman = session.experiment.data
    session.experiment._setROParam('forcescandata', True)
    try:
        count(1)
        # ensure that a scan dataset was produced
        ds = dataman.getLastScans()[-1]
        assert ds.npoints == 1
        assert session.experiment.lastscan == ds.counter
    finally:
        session.experiment._setROParam('forcescandata', False)
