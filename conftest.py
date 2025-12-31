# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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

"""Py.test configuration file containing fixtures for individual tests."""

import os


def pytest_configure(config):
    os.environ['PYTEST_QT_API'] = 'pyqt%s' % os.environ.get('NICOS_QT', 5)


pytest_plugins = [
    'test.fixtures.setup_test_suite',
    'test.fixtures.session',
    'test.fixtures.log',
    'test.fixtures.dataroot',
    'test.fixtures.guiclient',
]
