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

"""NICOS device class test suite."""

import os
import sys
import time
from os import path

import pytest

from nicos.utils import ensureDirectory, enableDirectory, readFileCounter
from nicos.commands.scan import scan
from nicos.commands.basic import run

from test.utils import runtime_root

year = time.strftime('%Y')

session_setup = 'asciisink'


@pytest.fixture()
def cleanup(session):
    """Ensure to make all data pathes writable again"""

    yield
    # clean up "disabled" directory so that the next test run can remove it
    if path.isdir(datapath('p999')):
        enableDirectory(datapath('p999'))
    session.experiment._setROParam('managerights', None)


def datapath(*parts, **kwds):
    extra = kwds.get('extra', 'data')
    return path.join(runtime_root, extra, year, *parts)


def test_experiment(session, cleanup):
    exp = session.experiment

    # setup test scenario
    exp._setROParam('dataroot', path.join(runtime_root, 'data'))
    exp.proposal = 'service'
    exp._setROParam('proptype', 'service')
    # if there is no exp.new, we need to adjust proposalpath ourselfs!
    exp.proposalpath = exp.proposalpath_of(exp.proposal)

    # create the needed script file
    spath = path.join(runtime_root, 'data', year,
                      'service', 'scripts')

    assert exp.scriptpath == spath
    ensureDirectory(spath)
    with open(path.join(spath, 'servicestart.py'), 'w') as fp:
        fp.write('Remark("service time")\n')

    # first, go in service mode
    exp.servicescript = 'servicestart.py'
    try:
        exp.new('service', localcontact=exp.localcontact)
    finally:
        exp.servicescript = ''
    assert exp.proposal == 'service'
    assert exp.proptype == 'service'
    assert exp.remark == 'service time'
    assert exp.scriptpath == spath

    # check correct operation of sampledir
    exp.sampledir = 'sample'
    assert exp.datapath == path.join(exp.dataroot, year, 'service',
                                     'sample', 'data')
    exp.sampledir = ''

    # for this proposal, remove access rights after switching back
    exp._setROParam('managerights', dict(disableFileMode=0, disableDirMode=0))

    # then, go in proposal mode
    exp.new(999, 'etitle', 'me <m.e@me.net>', 'you')
    # check that all properties have been set accordingly
    assert exp.proposal == 'p999'
    assert exp.proptype == 'user'
    assert exp.title == 'etitle'
    assert exp.localcontact == 'me <m.e@me.net>'
    assert exp.users == 'you'
    assert exp.remark == ''

    # check that directories have been created
    assert path.isdir(datapath('p999'))
    assert path.isdir(datapath('p999', 'scripts'))
    assert path.isdir(datapath('p999', 'data'))

    # check that templating works
    assert path.isfile(datapath('p999', 'scripts', 'start_p999.py'))
    run('start_p999.py')
    assert exp.remark == 'proposal p999 started by you; sample is unknown'

    # try a small scan; check for data file written
    scan(session.getDevice('axis'), 0, 1, 5, 0.01, u'Meßzeit')
    assert path.isfile(datapath('..', 'counters'))
    nr = readFileCounter(datapath('..', 'counters'), 'scan')
    fn = datapath('p999', 'data', 'p999_%08d.dat' % nr)
    assert path.isfile(fn)
    with open(fn, 'rb') as fp:
        assert u'Meßzeit'.encode('utf-8') in fp.read()

    # now, finish the experiment
    thd = exp.finish()
    if thd:
        thd.join()
    # have the access rights been revoked?
    if os.name != 'nt':
        assert not os.access(datapath('p999'), os.X_OK)

    # did we switch back to service proposal?
    assert exp.proposal == 'service'

    # switch back to proposal (should re-enable directory)
    exp.new('p999', localcontact=exp.localcontact)
    assert os.access(datapath('p999'), os.X_OK)
    assert exp.users == ''
    # has the zip file been created?
    assert path.isfile(datapath('p999', 'p999.zip'))

    exp.addUser('A User')

    assert exp.users == 'A User'
    exp.addUser('Another User', 'another.user@experiment.com')
    assert exp.users == 'A User, Another User <another.user@experiment.com>'
    exp.addUser('Athird User', 'athird.user@experiment.com',
                'An Institute, Anywhere street, 12345 Anywhere')
    assert exp.users == 'A User, Another User <another.user@experiment.com>, '\
                        'Athird User <athird.user@experiment.com> ' \
                        '(An Institute, Anywhere street, 12345 Anywhere)'

    exp.users = 'Jülich'
    exp.users = u'Jülich'

    exp.scripts = ['Test ümlauts']
    exp.scripts = [u'Test ümlauts']
    assert exp.scripts == ['Test ümlauts']

    # and back to service
    exp.new('service', localcontact=exp.localcontact)


def test_expanduser_dataroot(session):
    exp = session.experiment
    dataroot = "~/data"
    exp._setROParam("dataroot", dataroot)
    assert exp.dataroot == path.expanduser(dataroot)


def test_expandenv_dataroot(session):
    exp = session.experiment
    os.environ['TESTVAR'] = path.join(runtime_root, 'xxx')
    dataroot2 = "$TESTVAR" if sys.platform != "win32" else "%TESTVAR%"
    exp._setROParam('dataroot', dataroot2)
    assert exp.dataroot == path.expandvars(dataroot2)
    exp.finish()
    exp.new('p888', 'etitle2', 'me2 <m.e2@me.net>', 'you2')
    assert os.access(datapath('p888', extra='xxx'), os.X_OK)
