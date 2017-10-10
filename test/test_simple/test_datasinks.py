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

"""NICOS data handlers test suite."""

import os
import time
from os import path

import pytest

try:
    import astropy.io.fits as pyfits
except ImportError:
    try:
        import pyfits
    except ImportError:
        pyfits = None

try:
    import PIL
except ImportError:
    PIL = None

try:
    import quickyaml
except ImportError:
    quickyaml = None

try:
    import yaml
except ImportError:
    yaml = None

from nicos import config
from nicos.pycompat import cPickle as pickle
from nicos.utils import readFile, updateFileCounter
from nicos.commands.scan import scan

from test.utils import raises

year = time.strftime('%Y')

session_setup = 'data'


@pytest.fixture(scope='class', autouse=True)
def setup_module(session):
    """Setup dataroot and generate a dataset by scanning"""
    exp = session.experiment
    dataroot = path.join(config.nicos_root, 'testdata')
    os.makedirs(dataroot)

    counter = path.join(dataroot, exp.counterfile)
    open(counter, 'w').close()
    updateFileCounter(counter, 'scan', 42)
    updateFileCounter(counter, 'point', 167)

    exp._setROParam('dataroot', dataroot)
    exp.new(1234, user='testuser', localcontact=exp.localcontact)
    exp.sample.new({'name': 'mysample'})
    assert path.abspath(exp.datapath) == \
        path.abspath(path.join(config.nicos_root, 'testdata',
                               year, 'p1234', 'data'))
    m = session.getDevice('motor2')
    det = session.getDevice('det')
    tdev = session.getDevice('tdev')
    session.experiment.setEnvironment([])

    scan(m, 0, 1, 5, det, tdev, t=0.005)

    yield


class TestSinks(object):

    def test_sink_class(self, session):
        scansink = session.getDevice('testsink1')
        # this saves the handlers created for the last dataset
        handlers = scansink._handlers
        assert len(handlers) == 1
        calls = handlers[0]._calls
        # this was called for a scan
        assert calls == ['prepare', 'begin'] + ['addSubset'] * 5 + ['end']

        pointsink = session.getDevice('testsink2')
        handlers = pointsink._handlers
        assert len(handlers) == 1
        calls = handlers[0]._calls
        # this was called for a point
        # first putValues: devices, second putValues: environment
        assert calls[:3] == ['prepare', 'begin', 'putValues']
        assert calls[-1] == 'end'
        assert calls.count('putMetainfo') == 1
        assert calls.count('putResults') == 1

    def test_console_sink(self, session):
        msgs = session.testhandler.get_messages()
        assert ('INFO    : nicos : ' + '=' * 100 + '\n') in msgs
        assert any(msg.startswith('INFO    : nicos : Starting scan:      '
                                  'scan(motor2, 0, 1, 5, det, tdev, t=0.00')
                   for msg in msgs)

    def test_filecounters(self, session):
        # check contents of counter files
        exp = session.experiment
        for directory, ctrs in zip(
                [exp.dataroot, exp.proposalpath, exp.samplepath],
                [('scan 43', 'point 172'), ('scan 1', 'point 5'),
                 ('scan 1', 'point 5')]):
            counterfile = path.join(directory, exp.counterfile)
            assert path.isfile(counterfile)
            contents = readFile(counterfile)
            assert set(contents) == set(ctrs)

    def test_scan_sink(self, session):
        # check contents of ASCII scan data file
        scanfile = path.join(session.experiment.datapath, 'p1234_00000043.dat')
        assert path.isfile(scanfile)
        contents = readFile(scanfile)
        assert contents[0].startswith('### NICOS data file')
        assert '### Scan data' in contents
        assert contents[-1].startswith('### End of NICOS data file')

        # check counter attributes
        scan = session.data._last_scans[-1]
        assert scan.counter == 43
        assert scan.propcounter == 1
        assert scan.samplecounter == 1
        assert session.experiment.lastscan == 43
        assert session.experiment.lastpoint == 172

    def test_raw_sinks(self, session):
        # check contents of files written by the raw sink
        rawfile = path.join(session.experiment.datapath, 'p1234_1.raw')
        assert path.isfile(rawfile)
        assert path.getsize(rawfile) == 128 * 128 * 4  # 128x128 px, 32bit ints

        headerfile = path.join(session.experiment.datapath, 'p1234_1.header')
        assert path.isfile(headerfile)
        contents = readFile(headerfile)
        assert contents[0] == '### NICOS Raw File Header V2.0'
        assert '### Sample and alignment' in contents
        assert any(line.strip() == 'Exp_proposal : p1234' for line in contents)

        logfile = path.join(session.experiment.datapath, 'p1234_1.log')
        assert path.isfile(logfile)
        contents = readFile(logfile)
        assert contents[0].startswith('# dev')
        assert len(contents) >= 3  # at least: header, motor2, tdev
        for line in contents[1:]:
            name, mean, stdev, minv, maxv = line.split()
            if name == 'motor2':
                assert mean == minv == maxv == '0.000'
                assert stdev == 'inf'

        if hasattr(os, 'link'):
            linkfile = path.join(session.experiment.datapath, '00000168.raw')
            assert path.isfile(linkfile)  # hardlink
            assert os.stat(linkfile).st_ino == os.stat(rawfile).st_ino

        # check files written by the single-raw sink
        rawfile = path.join(session.experiment.datapath, 'single', '43_172.raw')
        assert path.isfile(rawfile)
        assert path.getsize(rawfile) > 128 * 128 * 4  # data plus header

        if hasattr(os, 'link'):
            # this entry in filenametemplate is absolute, which means relative to
            # the dataroot, not the current experiment's datapath
            linkfile = path.join(session.experiment.dataroot, '00000172.raw')
            assert path.isfile(linkfile)  # hardlink
            assert os.stat(linkfile).st_ino == os.stat(rawfile).st_ino

    def test_bersans_sink(self, session):
        bersansfile = path.join(session.experiment.datapath, 'D0000168.001')
        assert path.isfile(bersansfile)
        contents = readFile(bersansfile)
        assert '%File' in contents
        assert 'User=testuser' in contents  # BerSANS headers
        assert 'Exp_proposal=p1234' in contents  # NICOS headers
        assert ('0,' * 127 + '0') in contents  # data

    def test_serialized_sink(self, session):
        serial_file = path.join(session.experiment.datapath, '.all_datasets')
        assert path.isfile(serial_file)
        try:
            with open(serial_file, 'rb') as fp:
                datasets = pickle.load(fp)
        except Exception:
            assert False, 'could not read serialized sink'
        assert len(datasets) == 1
        assert datasets[43]
        assert raises(KeyError, lambda: datasets[41])
        data = datasets[43]
        assert data.samplecounter == 1
        assert data.counter == 43
        assert data.propcounter == 1
        assert data.samplecounter == 1
        assert data.number == 0
        assert data.started
        assert data.finished
        assert data.info == 'scan(motor2, 0, 1, 5, det, tdev, t=0.005)'
        # pylint: disable=len-as-condition
        assert len(data.metainfo)
        assert len(data.envvaluelists)
        assert len(data.devvaluelists)
        assert len(data.detvaluelists)

    @pytest.mark.skipif(not PIL, reason='PIL library missing')
    def test_tiff_sink(self, session):
        tifffile = path.join(session.experiment.datapath, '00000168.tiff')
        assert path.isfile(tifffile)

    @pytest.mark.skipif(not pyfits, reason='pyfits library missing')
    def test_fits_sink(self, session):
        fitsfile = path.join(session.experiment.datapath, '00000168.fits')
        assert path.isfile(fitsfile)
        with pyfits.open(fitsfile) as ffile:
            hdu = ffile[0]
            assert hdu.data.shape == (128, 128)
            assert hdu.header['Exp/proposal'] == 'p1234'

    @pytest.mark.skipif(not quickyaml, reason='QuickYAML library missing')
    def test_yaml_sink_1(self, session):
        yamlfile = path.join(session.experiment.datapath, '00000168.yaml')
        assert path.isfile(yamlfile)
        with open(yamlfile) as df:
            data = df.read()
            # note: whitespace is significant in the following lines!
            assert '''instrument:
    name: INSTR''' in data
            assert '''experiment:
    number: p1234
    proposal: p1234''' in data
            assert '''    sample:
        description:
            name: mysample''' in data

    @pytest.mark.skipif(not (quickyaml and yaml),
                        reason='QuickYAML/PyYAML libraries missing')
    def test_yaml_sink_2(self, session):
        yamlfile = path.join(session.experiment.datapath, '00000168.yaml')
        assert path.isfile(yamlfile)
        with open(yamlfile) as df:
            contents = yaml.load(df)
        assert contents['instrument']['name'] == 'INSTR'
        assert contents['experiment']['proposal'] == 'p1234'
        assert contents['measurement']['sample']['description']['name'] == \
            'mysample'
