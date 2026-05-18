# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-present by the NICOS contributors (see AUTHORS)
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

"""NICOS device class test suite."""

import os
import sys
import time
from os import path

import pytest

from nicos.commands.basic import run
from nicos.commands.scan import scan
from nicos.core.acquire import Average, DevStatistics
from nicos.utils import enableDirectory, ensureDirectory, readFileCounter

from test.utils import runtime_root

year = time.strftime('%Y')

session_setup = 'asciisink'


@pytest.fixture()
def cleanup(session):
    """Ensure to make all data paths writable again"""

    yield
    # clean up "disabled" directory so that the next test run can remove it
    if path.isdir(datapath('p999')):
        enableDirectory(datapath('p999'))
    session.experiment._setROParam('managerights', None)


@pytest.fixture
def exp(session):

    return session.experiment


def datapath(*parts, **kwds):
    extra = kwds.get('extra', 'data')
    return path.join(runtime_root, extra, year, *parts)


def test_experiment(session, cleanup, exp):
    # setup test scenario
    exp._setROParam('dataroot', path.join(runtime_root, 'data'))
    exp._setROParam('proposal', 'service')
    exp._setROParam('proptype', 'service')
    # if there is no exp.new, we need to adjust proposalpath ourselves!
    exp.proposalpath = exp.proposalpath_of(exp.proposal)

    # create the needed script file
    spath = path.join(runtime_root, 'data', year,
                      'service', 'scripts')

    assert exp.scriptpath == spath
    ensureDirectory(spath)
    with open(path.join(spath, 'servicestart.py'), 'w',
              encoding='utf-8') as fp:
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
    assert exp.remark == ''  # pylint: disable=compare-to-empty-string

    # check that directories have been created
    assert path.isdir(datapath('p999'))
    assert path.isdir(datapath('p999', 'scripts'))
    assert path.isdir(datapath('p999', 'data'))

    # check that templating works
    assert path.isfile(datapath('p999', 'scripts', 'start_p999.py'))
    run('start_p999.py')
    assert exp.remark == 'proposal p999 started now; sample is unknown'

    # try a small scan; check for data file written
    scan(session.getDevice('axis'), 0, 1, 5, 0.01, 'Meßzeit')
    assert path.isfile(datapath('..', 'counters'))
    nr = readFileCounter(datapath('..', 'counters'), 'scan')
    fn = datapath('p999', 'data', 'p999_%08d.dat' % nr)
    assert path.isfile(fn)
    with open(fn, 'r', encoding='utf-8') as fp:
        assert 'Meßzeit' in fp.read()

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
    assert exp.users == ''  # pylint: disable=compare-to-empty-string
    # has the zip file been created?
    assert path.isfile(datapath('p999', 'p999.zip'))

    exp.addUser('A User')

    assert exp.users == 'A User'
    exp.addUser('Another User', 'another.user@experiment.com')
    assert exp.users == 'A User; Another User <another.user@experiment.com>'
    exp.addUser('Athird User', 'athird.user@experiment.com',
                'An Institute, Anywhere street, 12345 Anywhere')
    assert exp.users == 'A User; Another User <another.user@experiment.com>; ' \
        'Athird User <athird.user@experiment.com> ' \
        '(An Institute, Anywhere street, 12345 Anywhere)'

    exp.update(users=[{'name': 'Jülich'}])
    assert exp.users == 'Jülich'
    exp.update(users='A. Name')
    assert exp.users == 'A. Name'

    exp.scripts = ['Test ümlauts']
    assert exp.scripts == ['Test ümlauts']

    # and back to service
    exp.new('service', localcontact=exp.localcontact)


def test_experiment_add_user(session, exp):
    # Try writing random stuff to the user parameter
    exp.addUser('Jon', 'jon@doe.com', 'myfacility')
    with pytest.raises(ValueError,
                       match='name must be a non-empty string!'):
        exp.addUser(37)
    with pytest.raises(ValueError,
                       match=r"'\[\]' is not a valid email address"):
        exp.addUser('James', [])
    with pytest.raises(ValueError,
                       match='affiliation must be a non-empty string!'):
        exp.addUser('Jane', 'jane@doe.com', {})

    # Check if reading the users parameter still works
    assert exp.users == 'Jon <jon@doe.com> (myfacility)'


def test_experiment_update_user(session, exp):
    # Update the users parameter with valid data
    exp.update(users=[
        {'name': 'Jon', 'affiliation': 'myfacility'},
        {'name': 'Jane', 'affiliation': 'myfacility'},
    ])
    assert exp.users == 'Jon (myfacility); Jane (myfacility)'

    # Update the users parameter with invalid data
    for users in [12, {}, '']:
        with pytest.raises(ValueError, match='users must be a non-empty string!'):
            exp.update(users=users)
    exp.update(users='BadInput')
    assert exp.users == 'BadInput'

    exp.update(users='Jon (myfacility); Jane (myfacility)')
    assert exp.users == 'Jon (myfacility); Jane (myfacility)'


def test_expanduser_dataroot(session, exp):
    dataroot = '~/data'
    exp._setROParam('dataroot', dataroot)
    assert exp.dataroot == path.expanduser(dataroot)


def test_update_title(session, exp):
    assert exp.title == 'Unknown'
    exp.update(title='blah blubb')
    assert exp.title == 'blah blubb'

    for title in ([], {}, '', ()):
        with pytest.raises(ValueError,
                           match='title must be a non-empty string!'):
            exp.update(title=title)


def test_update_localcontact(session, exp):
    assert exp.localcontact == 'R. Esponsible <r.esponsible@frm2.tum.de>'
    name = 'R. Esponsible'
    for lc in (name, [{'name': name}], [{'name': name, 'email': None}]):
        exp.update(localcontacts=lc)
        assert exp.localcontact == name

    email = 'r.esponsible@frm2.tum.de'
    for lc in (f'{name} <{email}>', [{'name': name, 'email': email}]):
        exp.update(localcontacts=lc)
        assert exp.localcontact == f'{name} <{email}>'
    for lc in ([], {}, '', ()):
        with pytest.raises(ValueError,
                           match='localcontacts must be a non-empty string!'):
            exp.update(localcontacts=lc)


def test_expandenv_dataroot(session, exp):
    os.environ['TESTVAR'] = path.join(runtime_root, 'xxx')
    dataroot2 = '$TESTVAR' if sys.platform != 'win32' else '%TESTVAR%'
    exp._setROParam('dataroot', dataroot2)
    assert exp.dataroot == path.expandvars(dataroot2)
    exp.finish()
    exp.new('p888', 'etitle2', 'me2 <m.e2@me.net>', 'you2')
    assert os.access(datapath('p888', extra='xxx'), os.X_OK)


def test_envlist(session, exp):
    motor = session.getDevice('motor')
    coder = session.getDevice('coder')

    exp.setEnvironment([motor, 'coder', 'motor:avg', coder, Average(coder),
                        'unknown'])
    assert exp.envlist == ['motor', 'coder', 'motor:avg', 'coder:avg',
                           'unknown']
    assert len(exp.sampleenv) == 4
    assert exp.sampleenv[:2] == [motor, coder]
    assert isinstance(exp.sampleenv[2], DevStatistics)

    exp._scrubDetEnvLists()
    assert exp.envlist == ['motor', 'coder', 'motor:avg', 'coder:avg']
