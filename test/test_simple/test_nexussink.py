# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************

import datetime
import os
import re
import time
from os import path

import numpy as np
import pytest

pytest.importorskip('h5py')

import h5py

from nicos import config
from nicos.commands.device import maw
from nicos.commands.measure import count
from nicos.commands.scan import scan
from nicos.nexus.elements import ConstDataset, DetectorDataset, \
    DeviceAttribute, DeviceDataset, EndTime, ImageDataset, NXAttribute, \
    NXExternalLink, NXLink, NXScanLink, StartTime
from nicos.utils import updateFileCounter

from test.nexus.TestTemplateProvider import setTemplate


year = time.strftime('%Y')

session_setup = 'nexussink'


class TestNexusSink:
    datadir = 'testdata2'

    @pytest.fixture(scope='class', autouse=True)
    def init_system(self, session):
        exp = session.experiment
        dataroot = path.join(config.nicos_root, self.datadir)
        if not os.path.isdir(dataroot):
            os.makedirs(dataroot)

        exp._setROParam('dataroot', dataroot)
        exp._setROParam('forcescandata', True)
        exp.new(1234, user='testuser', localcontact=exp.localcontact)
        exp.sample.new({'name': 'GurkenOxid'})
        assert path.abspath(exp.datapath) == path.abspath(
            path.join(config.nicos_root, self.datadir, year, 'p1234',
                      'data'))
        session.experiment.setEnvironment([])

    def setScanCounter(self, session, no):
        dataroot = path.join(config.nicos_root, self.datadir)
        counter = path.join(dataroot, session.experiment.counterfile)
        updateFileCounter(counter, 'scan', no)
        # print('SetCounter')
        updateFileCounter(counter, 'point', 167)

    def test_hierarchy(self, session):
        template = {
            'instrument': 'test',
            'entry:NXentry': {},
        }
        setTemplate(template)
        session.experiment.setDetectors(['det', ])
        self.setScanCounter(session, 44)

        count(t=0.1)

        with h5py.File(path.join(session.experiment.datapath,
                                 f'test{year}n000045.hdf'), 'r') as fin:
            att = fin.attrs['instrument']
            assert att == b'test'

            g = fin['entry']
            att = g.attrs['NX_class']
            assert att == b'NXentry'

    def test_Datasets(self, session):
        template = {
            'entry:NXentry': {
                'name': DeviceDataset('Exp', 'title'),
                'title': DeviceDataset('Exp', 'title2',
                                       defaultval='Default title'),
                'definition': ConstDataset('NXmonopd', 'string'),
                'sry': DeviceDataset('sry',
                                     units=NXAttribute('deg', 'string')),
            },
        }
        session.experiment.update(title='GurkenTitle')
        maw(session.getDevice('sry'), 23.7)
        session.experiment.setDetectors(['det', ])
        setTemplate(template)
        self.setScanCounter(session, 46)
        count(t=.1)

        with h5py.File(path.join(session.experiment.datapath,
                                 f'test{year}n000047.hdf'), 'r') as fin:
            ds = fin['entry/name']
            assert ds[()] == b'GurkenTitle'

            ds = fin['entry/title']
            assert ds[()] == b'Default title'

            ds = fin['entry/definition']
            assert ds[()] == b'NXmonopd'

            ds = fin['entry/sry']
            assert ds[0] == 23.7
            assert ds.attrs['units'] == b'deg'

    def test_Attributes(self, session):
        template = {
            'entry:NXentry': {
                'title': DeviceAttribute('Exp', 'title'),
                'title2': DeviceAttribute('Exp', 'title2',
                                          defaultval='Default title'),
                'units': NXAttribute('mm', 'string'),
            }
        }

        session.experiment.update(title='GurkenTitle')
        setTemplate(template)
        self.setScanCounter(session, 47)
        session.experiment.setDetectors(['det', ])

        count(t=.1)

        with h5py.File(path.join(session.experiment.datapath,
                                 f'test{year}n000048.hdf'), 'r') as fin:
            g = fin['entry']
            assert g.attrs['title'] == b'GurkenTitle'
            assert g.attrs['title2'] == b'Default title'
            assert g.attrs['units'] == b'mm'

    def test_Scan(self, session):
        template = {
            'entry:NXentry': {
                'time': DetectorDataset('timer', 'float32'),
                'mon': DetectorDataset('mon1', 'uint32'),
                'counts': ImageDataset(0, 0,
                                       signal=NXAttribute(1, 'int32')),
                'sry': DeviceDataset('sry'),
            },
            'data:NXdata': {'None': NXScanLink(), }
        }

        setTemplate(template)
        self.setScanCounter(session, 48)
        session.experiment.setDetectors(['det', ])
        sry = session.getDevice('sry')
        scan(sry, 0, 1, 5, t=0.001)

        with h5py.File(path.join(session.experiment.datapath,
                                 f'test{year}n000049.hdf'), 'r') as fin:

            ds = fin['entry/sry']
            assert len(ds) == 5

            ds = fin['entry/time']
            assert len(ds) == 5
            ds = fin['entry/mon']
            assert len(ds) == 5

            ds = fin['entry/counts']
            assert len(ds) == 5

            ds = fin['data/sry']
            assert len(ds) == 5
            assert ds[0] == 0
            assert ds[1] == 1
            assert ds[2] == 2
            assert ds[3] == 3
            assert ds.attrs['target'] == b'/entry/sry'

    def test_Detector(self, session):
        template = {
            'data:NXdata': {
                'time': DetectorDataset('timer', 'float32'),
                'mon': DetectorDataset('mon1', 'uint32'),
                'counts': ImageDataset(0, 0,
                                       signal=NXAttribute(1, 'int32')),
            },
        }

        setTemplate(template)
        self.setScanCounter(session, 49)
        session.experiment.setDetectors(['det', ])
        count(t=.1)

        with h5py.File(path.join(session.experiment.datapath,
                                 f'test{year}n000050.hdf'), 'r') as fin:
            ds = fin['data/time']
            ds = fin['data/mon']
            ds = fin['data/counts']
            assert ds.attrs['signal'] == 1

    def test_Link(self, session):
        template = {
            'entry:NXentry': {'sry': DeviceDataset('sry'), },
            'data:NXdata': {'srlink': NXLink('/entry/sry'), }
        }

        maw(session.getDevice('sry'), 77.7)
        session.experiment.setDetectors(['det', ])

        setTemplate(template)
        self.setScanCounter(session, 50)
        count(t=.1)

        with h5py.File(path.join(session.experiment.datapath,
                                 f'test{year}n000051.hdf'), 'r') as fin:
            ds = fin['entry/sry']
            assert ds[0] == 77.7

            ds = fin['data/srlink']
            assert ds[0] == 77.7

            assert ds.attrs['target'] == b'/entry/sry'

    def test_times(self, session):
        p = re.compile(r'^\d{4}(-\d{2}){2} \d{2}(:\d{2}){2}.\d{3}$')
        template = {
            'entry:NXentry': {
                'start_time': StartTime(),
                'end_time': EndTime(),
            },
        }
        setTemplate(template)
        session.experiment.setDetectors(['det', ])
        self.setScanCounter(session, 51)

        count(t=0.1)

        with h5py.File(path.join(session.experiment.datapath,
                                 f'test{year}n000052.hdf'), 'r') as fin:
            times = {}
            for s in ['start_time', 'end_time']:
                ts = fin['entry/%s' % s][0].decode('utf-8')
                assert p.match(ts)  # check format
                assert datetime.datetime.strptime(
                    ts, '%Y-%m-%d %H:%M:%S.%f').timetuple()  # check value
                times[s] = datetime.datetime.strptime(
                    ts, '%Y-%m-%d %H:%M:%S.%f').timestamp()

            assert (times['end_time'] - times['start_time']) >= 0.1

    def test_External_link(self, session):
        exp = session.experiment

        fname = path.join(exp.datapath, 'external_test.h5')
        with h5py.File(fname, 'w') as tst:
            entry = tst.create_group('entry')
            entry.attrs['NXclass'] = np.string_('NXGroup')
            ex = entry.create_dataset('external', (1,), dtype='f4')
            ex[0] = 47

        template = {
            'test': NXExternalLink(fname, '/entry/external')
        }
        exp.setDetectors(['det', ])
        self.setScanCounter(session, 52)
        setTemplate(template)
        count(t=.1)

        with h5py.File(path.join(session.experiment.datapath,
                                 'test%sn000053.hdf' % year), 'r') as fin:
            ds = fin['test']
            assert ds[0] == 47

    def test_External_link_failure(self, session, log):
        exp = session.experiment

        fname = path.join(exp.datapath, 'external_turd.h5')

        template = {
            'test': NXExternalLink(fname, '/entry/external')
        }
        exp.setDetectors(['det', ])
        self.setScanCounter(session, 55)
        setTemplate(template)
        #
        # with log.assert_warns(regex='.*Failed to create external link.*',
        #                      count=1):
        #    pytest.raises(Exception, count, 't=1')
        count(t=.1)
        for warn in log._warnings:
            if warn.find('Failed to create external link') > 0:
                return
        pytest.fail('external link created')
