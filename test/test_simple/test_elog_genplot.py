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
#
# *****************************************************************************

"""NICOS tests for nicos.commands.scan and nicos.core.scan modules."""

from os import path

from nicos import session
from nicos.core.data import ScanData
from nicos.commands.scan import scan
from nicos.services.elog import genplot
from nicos.core.sessions.utils import MASTER

from test.utils import rootdir, requires, hasGnuplot


def setup_module():
    session.loadSetup('scanning')
    session.setMode(MASTER)


def teardown_module():
    session.unloadSetup()


@requires(hasGnuplot(), 'Skipped due to missing gnuplot')
def test_scan_gen_elog():
    m = session.getDevice('motor')
    mm = session.getDevice('manual')
    mm.move(0)

    session.experiment.setDetectors([session.getDevice('det')])

    try:
        # plain scan, with some extras: infostring, firstmove
        scan(m, 0, 1, 5, 0., 'test scan', manual=1)
        dataset = ScanData(session.data._last_scans[-1])
        genplot.plotDataset(dataset, path.join(rootdir, 'testplt'), 'svg')
    finally:
        session.experiment.detlist = []
