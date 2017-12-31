#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************
"""YAML data sink classes for STRESS-SPEC."""

import re
import time

from nicos import session
from nicos.core import Override, Param, listof
from nicos.core.constants import FINAL, POINT, SCAN, SUBSCAN
from nicos.devices.datasinks.scan import AsciiScanfileSink, \
    AsciiScanfileSinkHandler, TIMEFMT

from nicos.pycompat import TextIOWrapper, iteritems, to_utf8
from nicos.utils import AutoDefaultODict

import numpy as np

try:
    import quickyaml
    import io
except ImportError:
    quickyaml = None
    try:
        import yaml
        yaml.add_representer(AutoDefaultODict,
                             yaml.representer.SafeRepresenter.represent_dict)
    except ImportError:
        yaml = None


class YamlDatafileSinkHandler(AsciiScanfileSinkHandler):
    """Write the STRESS-SPEC specific yaml-formatted scan data file."""

    filetype = 'MLZ.StressSpec.2.0 / proposal 0.2'
    accept_file_images_only = False
    max_yaml_width = 120

    # def _readdev(self, devname, mapper=lambda x: x):
    #     try:
    #         return mapper(session.getDevice(devname).read())
    #     except NicosError:
    #         return None

    # def _devpar(self, devname, parname, mapper=lambda x: x):
    #     try:
    #         return mapper(getattr(session.getDevice(devname), parname))
    #     except NicosError:
    #         return None

    def _dict(self):
        return AutoDefaultODict()

    # def _flowlist(self, *args):
    #     return None
    #     # return quickyaml.flowlist(*args)

    objects = ['time', 'angle', 'clearance', 'collimator_fhwm', 'position',
               'wavelength']
    _millimeter = 'millimeter'
    units = ['second', 'degree', _millimeter, _millimeter, _millimeter,
             'angstrom']

    def _fill_format(self, formats):
        formats['identifier'] = self.filetype
        _units = formats['units'] = self._dict()
        for obj, unit in zip(self.objects, self.units):
            _units[obj] = unit

    def _fill_position(self, position, value, offset, precision):
        position['value'] = value
        position['offset_coder'] = offset
        position['precision'] = precision

    def _fill_user(self, user, name, roles):
        _user = re.split(r'(<)?(\w+(?:[\.-]\w+)+@\w+(?:\.\w+)+)(?(1)>)',
                         to_utf8(name).decode())
        user['name'] = _user[0].strip()
        user['email'] = _user[2] if len(_user) > 2 else ''
        user['roles'] = roles

    def _write_tolerances(self, valuelist):
        sample = self._data['measurement']['sample']
        setup = self._data['measurement']['setup']
        for device, _key, value in valuelist:
            if device in ['xt', 'yt', 'zt']:
                p = sample['position'][device]
                p['precision'] = value
            elif device in ['tths', 'omgs', 'chis', 'phis']:
                p = sample['orientation'][device]
                p['precision'] = value
            elif device == 'slitm':
                p = setup['slit_m']['horizontal_clearance']
                p['precision'] = value[0]
                p = setup['slit_m']['vertical_clearance']
                p['precision'] = value[1]
            elif device == 'slitp':
                p = setup['slit_p']['horizontal_clearance']
                p['precision'] = value[0]
                p = setup['slit_p']['vertical_clearance']
                p['precision'] = value[1]
            elif device == 'slite':
                p = setup['slit_e']['clearance']
                p['precision'] = value
            elif device in ['omgm', 'tthm']:
                p = setup['monochromator'][device]
                p['precision'] = value
            else:
                self.log.debug('tolerance: %s.%s: %s', device, _key, value)

    def _write_offsets(self, valuelist):
        sample = self._data['measurement']['sample']
        setup = self._data['measurement']['setup']
        for device, _key, value in valuelist:
            if device in ['xt', 'yt', 'zt']:
                p = sample['position'][device]
                p['offset_coder'] = value
            elif device in ['tths', 'omgs', 'chis', 'phis']:
                p = sample['orientation'][device]
                p['offset_coder'] = value
            elif device == 'slitm':
                p = setup['slit_m']['horizontal_clearance']
                p['offset_coder'] = value[0]
                p = setup['slit_m']['vertical_clearance']
                p['offset_coder'] = value[1]
            elif device == 'slitp':
                p = setup['slit_p']['horizontal_clearance']
                p['offset_coder'] = value[0]
                p = setup['slit_p']['vertical_clearance']
                p['offset_coder'] = value[1]
            elif device == 'slite':
                p = setup['slit_e']['clearance']
                p['offset_coder'] = value
            elif device in ['omgm', 'tthm']:
                p = setup['monochromator'][device]
                p['offset_coder'] = value
            else:
                self.log.debug('offset: %s.%s: %s', device, _key, value)

    def _write_sample(self, valuelist):
        # self.log.info('Sample: %r', valuelist)
        sample = self._data['measurement']['sample']
        for _device, key, value in valuelist:
            if key == 'samplename':
                sample['description']['name'] = value

    def _write_experiment(self, valuelist):
        # self.log.info('Experiment: %r', valuelist)
        experiment = self._data['experiment']
        for _device, key, value in valuelist:
            if key in ['proposal', 'title', 'remark']:
                experiment[key] = value
            elif key == 'users':
                authors = experiment['authors']
                author = self._dict()
                self._fill_user(author, value, ['principal_investigator'])
                authors.append(author)
            elif key == 'localcontact':
                authors = experiment['authors']
                author = self._dict()
                self._fill_user(author, value, ['local_contact'])
                authors.append(author)

    def _write_status(self, valuelist):
        # self.log.info('Status: %r', valuelist)
        # for device, _key, value in valuelist:
        #     self.log.info('%s.%s: %s', device, _key, value)
        pass

    def _write_instrument(self, valuelist):
        # self.log.info('Instrument: %r', valuelist)
        instrument = self._data['instrument']
        for device, key, value in valuelist:
            if device not in ['demo', 'DEMO']:
                if key in ['facility', 'website']:
                    instrument[key] = to_utf8(value)
                elif key == 'instrument':
                    instrument['name'] = value
                elif key == 'operators':
                    instrument[key] = []
                    for operator in value:
                        instrument[key].append(to_utf8(operator))
                elif key == 'doi':
                    instrument['references'] = []
                    instrument['references'].append(to_utf8(value))

    def _write_limits(self, valuelist):
        # self.log.info('Limits: %r', valuelist)
        # for device, _key, value in valuelist:
        #     self.log.info('%s.%s: %s', device, _key, value)
        pass

    def _write_general(self, valuelist):
        sample = self._data['measurement']['sample']
        setup = self._data['measurement']['setup']
        for device, _key, value in valuelist:
            if device in ['xt', 'yt', 'zt']:
                p = sample['position'][device]
                p['value'] = value
            elif device in ['tths', 'omgs', 'chis', 'phis']:
                p = sample['orientation'][device]
                p['value'] = value
            elif device == 'slitm':
                p = setup['slit_m']['horizontal_clearance']
                p['value'] = value[0]
                p = setup['slit_m']['vertical_clearance']
                p['value'] = value[1]
            elif device == 'slitp':
                p = setup['slit_p']['horizontal_clearance']
                p['value'] = value[0]
                p = setup['slit_p']['vertical_clearance']
                p['value'] = value[1]
            elif device == 'slite':
                p = setup['slit_e']['clearance']
                p['value'] = value
            elif device == 'transm':
                setup['monochromator']['crystal'] = value
            elif device == 'wav':
                setup['monochromator']['incident_wavelength'] = value
            elif device in ['omgm', 'tthm']:
                p = setup['monochromator'][device]
                p['value'] = value
            else:
                self.log.debug('general: %s.%s: %s', device, _key, value)

    def __init__(self, sink, dataset, detector):
        AsciiScanfileSinkHandler.__init__(self, sink, dataset, detector)
        self._wrote_header = False
        self._file = None
        self._fname = None
        self._template = sink.filenametemplate
        self._data = None
        self._scan_type = None

    def prepare(self):
        self.log.debug('prepare: %r', self.dataset.settype)
        if self.dataset.settype == POINT:
            return
        if self._data is None:
            self._data = self._dict()
            self._scan_type = 'SGEN1'
        self._number = session.data.assignCounter(self.dataset)
        fp = session.data.createDataFile(self.dataset, self._template[0])
        self._fname = fp.shortpath
        self._filepath = fp.filepath
        if not quickyaml:
            self._file = TextIOWrapper(fp)
        else:
            fp.close()
            self._file = io.FileIO(self._filepath, 'w')

        self._data['instrument'] = self._dict()
        self._data['format'] = self._dict()
        self._data['experiment'] = self._dict()
        self._data['measurement'] = self._dict()
        self._fill_format(self._data['format'])

    def begin(self):
        if self.dataset.settype == POINT:
            return
        ds = self.dataset
        scaninfo = ds.info.split('-')[-1].strip()
        if scaninfo.startswith('contscan'):
            self._scan_type = 'SGEN2'
        elif scaninfo.startswith('scan'):
            self._scan_type = 'SGEN1'
        else:
            self._scan_type = 'SGEN1'

        instrument = self._data['instrument']
        instrument['name'] = ''
        instrument['operators'] = []
        instrument['facility'] = ''
        instrument['website'] = ''
        instrument['references'] = []

        measurement = self._data['measurement']
        measurement['unique_identifier'] = self.dataset.uid.urn

        experiment = self._data['experiment']
        experiment['number'] = measurement['number'] = self.dataset.counter
        experiment['proposal'] = ''
        experiment['title'] = ''
        experiment['authors'] = []

        history = measurement['history'] = self._dict()
        history['started'] = time.strftime(TIMEFMT)
        history['stopped'] = time.strftime(TIMEFMT)
        history['scan'] = self.dataset.info

        sample = measurement['sample'] = self._dict()
        sample['description'] = self._dict()
        sample['description']['name'] = ''
        sample['temperature'] = self._dict()
        sample['orientation'] = self._dict()
        for dev in ['tths', 'omgs', 'chis', 'phis']:
            sample['orientation'][dev] = self._dict()
            self._fill_position(sample['orientation'][dev], 0, 0, 0)
        sample['position'] = self._dict()
        for dev in ['xt', 'yt', 'zt']:
            sample['position']['xt'] = self._dict()
            self._fill_position(sample['position']['xt'], 0, 0, 0)

        setup = measurement['setup'] = self._dict()
        setup['collimator_1'] = "15'"

        setup['slit_m'] = self._dict()
        for x in ['horizontal_clearance', 'vertical_clearance']:
            p = setup['slit_m'][x] = self._dict()
            self._fill_position(p, 0, 0, 0)

        p = setup['monochromator'] = self._dict()
        p['crystal'] = 'Si'
        for dev in ['omgm', 'tthm']:
            p[dev] = self._dict()
            self._fill_position(p[dev], 0, 0, 0)
        p['angle'] = 0
        p['incident_wavelength'] = 0

        setup['slit_e'] = self._dict()
        p = setup['slit_e']['clearance'] = self._dict()
        self._fill_position(p, 0, 0, 0)

        setup['slit_p'] = self._dict()
        for x in ['horizontal_clearance', 'horizontal_translation',
                  'vertical_clearance', 'vertical_translation']:
            p = setup['slit_p'][x] = self._dict()
            self._fill_position(p, 0, 0, 0)

        setup['collimator_2'] = self._dict()
        p = setup['collimator_2']['fhwm'] = 5

        measurement['scan'] = []
        self._wrote_headers = False
        self._detvalues = None

    def _float(self, value):
        return float(eval(value))

    def _integer(self, value):
        return int(eval(value))

    def _fill_header(self):
        bycategory = {}
        for (dev, key), (_v, v, _, cat) in iteritems(self.dataset.metainfo):
            if cat:
                if key == 'operators':  # don't use the formatted list
                    bycategory.setdefault(cat, []).append((dev, key, _v))
                else:
                    bycategory.setdefault(cat, []).append((dev, key, v,))
        if 'experiment' in bycategory:
            self._write_experiment(bycategory['experiment'])
        if 'sample' in bycategory:
            self._write_sample(bycategory['sample'])
        if 'instrument' in bycategory:
            self._write_instrument(bycategory['instrument'])
        if 'offsets' in bycategory:
            self._write_offsets(bycategory['offsets'])
        if 'limits' in bycategory:
            self._write_limits(bycategory['limits'])
        if 'precisions' in bycategory:
            self._write_tolerances(bycategory['precisions'])
        if 'status' in bycategory:
            self._write_status(bycategory['status'])
        if 'general' in bycategory:
            self._write_general(bycategory['general'])

    def putMetainfo(self, metainfo):
        self.log.debug('ADD META INFO %r', metainfo)
        return

    def putResults(self, quality, results):
        """Called when the point dataset main results are updated.

        The *quality* is one of the constants defined in the module:

        * LIVE is for intermediate data that should not be written to files.
        * INTERMEDIATE is for intermediate data that should be written.
        * FINAL is for final data.
        * INTERRUPTED is for data that has been read after the counting was
          interrupted by an exception.

        Argument *results* contains the new results.  ``dataset.results``
        contains all results so far.
        """
        self.log.debug('%s', quality)
        if quality != FINAL and self.dataset.settype != POINT:
            return

    def addSubset(self, point):
        if not self._wrote_header:
            self._fill_header()
            self._wrote_header = True

        if point.settype != POINT:
            self.log.info('add subset: %s', point.settype)
            return
        self.log.debug('%r - %r', self.dataset.detvalueinfo,
                       point.detvaluelist)

        # the image data are hopefully always at this place
        try:
            if not self.sink.detectors:
                det = session.experiment.detectors[0]
            else:
                det = session.getDevice(self.sink.detectors[0])
            self._detvalues = point.results[det.name][1][0]
        except IndexError:
            # create empty data set
            self.log.error('Could not get the image data from %s', det.name)
            self._detvalues = np.zeros((256, 256))

        scanpoint = self._dict()
        scanparams = self._dict()
        if point.devvaluelist:
            scanparams[point.devvalueinfo[0].name] = self._float(
                '%.2f' % point.devvaluelist[0])
        scanpoint['scan_parameters'] = scanparams
        for (info, val) in zip(self.dataset.detvalueinfo, point.detvaluelist):
            if info.type == 'time':
                scanpoint['time'] = self._float('%.2f' % val)
            elif info.type == 'counter':
                scanpoint['sum'] = self._integer('%d' % val)
            # elif info.type == 'filename':
            #     scanpoint['image'] = '%s' % val
            elif info.type == 'monitor':
                scanpoint['monitor'] = self._integer('%d' % val)
            else:
                self.log.info('%s %s', info.name, info.type)
        scanpoint['image'] = [] if self._detvalues is None else self._detvalues
        self._data['measurement']['scan'].append(scanpoint)

    def _dump(self):
        if quickyaml:
            quickyaml.Dumper(width=self.max_yaml_width,
                             array_handling=quickyaml.ARRAY_AS_SEQ).dump(
                                 self._data, self._file)
        elif yaml:
            yaml.dump(self._data, self._file, allow_unicode=True, canonical=False,
                      default_flow_style=False, indent=4)

    def end(self):
        if self.dataset.settype == POINT:
            return
        history = self._data['measurement']['history']
        history['stopped'] = time.strftime(TIMEFMT)
        self._dump()
        self._file.flush()
        self._file.close()
        self._file = None
        self._data = None


class YamlDatafileSink(AsciiScanfileSink):
    """A data sink that writes to a YAML compatible data file.

    The `lastpoint` parameter is managed automatically.

    The current file counter as well as the name of the most recently written
    scanfile is managed by the experiment device.
    """

    handlerclass = YamlDatafileSinkHandler

    parameters = {
        'filenametemplate': Param('Name template for the files written',
                                  type=listof(str), userparam=False,
                                  settable=False,
                                  default=['%(proposal)s_'
                                           '%(scancounter)08d.yaml'],
                                  ),
    }

    parameter_overrides = {
        'settypes': Override(default=[SCAN, SUBSCAN]),
        'semicolon': Override(default=''),
        'commentchar': Override(default='',)
    }
