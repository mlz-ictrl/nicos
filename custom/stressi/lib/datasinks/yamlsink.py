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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************
"""YAML data sink classes for STRESS-SPEC."""

import re
import time

from collections import OrderedDict

from nicos import session
from nicos.core import Override, Param, listof
from nicos.devices.datasinks.scan import AsciiScanfileSink, \
    AsciiScanfileSinkHandler, TIMEFMT
from nicos.pycompat import TextIOWrapper, iteritems, to_utf8

from yaml import add_representer, dump, representer

add_representer(OrderedDict,
                representer.SafeRepresenter.represent_dict)


class YamlDatafileSinkHandler(AsciiScanfileSinkHandler):
    """YAML format datafile writing class."""

    _data = OrderedDict()
    _identifier = 'MLZ.StressSpec.2.0 / proposal 0.2'
    _objects = ['time', 'angle', 'clearance', 'collimator_fhwm', 'position',
                'wavelength']
    _millimeter = 'millimeter'
    _units = ['second', 'degree', _millimeter, _millimeter, _millimeter,
              'angstrom']

    def _fill_format(self, formats):
        formats['identifier'] = self._identifier
        _units = formats['units'] = OrderedDict()
        for obj, unit in zip(self._objects, self._units):
            _units[obj] = unit

    def _fill_position(self, position, value, offset, precision):
        position['value'] = value
        position['offset_coder'] = offset
        position['precision'] = precision

    def _fill_user(self, user, name, roles):
        _user = re.split(r'(<)?(\w+(?:[\.-]\w+)+@\w+(?:\.\w+)+)(?(1)>)',
                         to_utf8(name))
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
            elif device == 'tths':
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
            else:
                # print('%s.%s: %s' % (device, _key, value))
                pass

    def _write_offsets(self, valuelist):
        sample = self._data['measurement']['sample']
        setup = self._data['measurement']['setup']
        for device, _key, value in valuelist:
            if device in ['xt', 'yt', 'zt']:
                p = sample['position'][device]
                p['offset_coder'] = value
            elif device == 'tths':
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
            else:
                # print('%s.%s: %s' % (device, _key, value))
                pass

    def _write_sample(self, valuelist):
        # print('Sample:')
        # print(valuelist)
        sample = self._data['measurement']['sample']
        for _device, key, value in valuelist:
            if key == 'samplename':
                sample['description']['name'] = value

    def _write_experiment(self, valuelist):
        # print('Experiment:')
        # print(valuelist)
        experiment = self._data['experiment']
        for _device, key, value in valuelist:
            if key in ['proposal', 'title', 'remark']:
                experiment[key] = value
            elif key == 'users':
                authors = experiment['authors']
                author = OrderedDict()
                self._fill_user(author, value, ['principal_investigator', ])
                authors.append(author)
            elif key == 'localcontact':
                authors = experiment['authors']
                author = OrderedDict()
                self._fill_user(author, value, ['local_contact', ])
                authors.append(author)

    def _write_status(self, valuelist):
        # print('Status:')
        # print(valuelist)
        # for device, _key, value in valuelist:
        #     print('%s.%s: %s' % (device, _key, value))
        pass

    def _write_instrument(self, valuelist):
        # print('Instrument:')
        # print(valuelist)
        instrument = self._data['instrument']
        for device, key, value in valuelist:
            if device not in ['demo', 'DEMO']:
                if key in ['facility', 'website', ]:
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
        # print('Limits:')
        # for device, _key, value in valuelist:
        #     print('%s.%s: %s' % (device, _key, value))
        pass

    def _write_general(self, valuelist):
        sample = self._data['measurement']['sample']
        setup = self._data['measurement']['setup']
        for device, _key, value in valuelist:
            if device in ['xt', 'yt', 'zt']:
                p = sample['position'][device]
                p['value'] = value
            elif device == 'tths':
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
            else:
                # print('%s.%s: %s' % (device, _key, value))
                pass

    def __init__(self, sink, dataset, detector):
        AsciiScanfileSinkHandler.__init__(self, sink, dataset, detector)
        self._wrote_header = False
        self._file = None
        self._fname = None
        self._template = sink.filenametemplate

    def prepare(self):
        self._number = session.data.assignCounter(self.dataset)
        fp = session.data.createDataFile(self.dataset, self._template)
        self._fname = fp.shortpath
        self._filepath = fp.filepath
        self._file = TextIOWrapper(fp)

        self._data['instrument'] = OrderedDict()
        self._data['format'] = OrderedDict()
        self._data['experiment'] = OrderedDict()
        self._data['measurement'] = OrderedDict()
        self._fill_format(self._data['format'])

    def begin(self):
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

        history = measurement['history'] = OrderedDict()
        history['started'] = time.strftime(TIMEFMT)
        history['stopped'] = time.strftime(TIMEFMT)
        history['scan'] = self.dataset.info

        sample = measurement['sample'] = OrderedDict()
        sample['description'] = OrderedDict()
        sample['description']['name'] = ''
        sample['temperature'] = OrderedDict()
        sample['orientation'] = OrderedDict()
        tths = sample['orientation']['tths'] = OrderedDict()
        self._fill_position(tths, 0, 0, 0)
        sample['position'] = OrderedDict()
        xt = sample['position']['xt'] = OrderedDict()
        self._fill_position(xt, 0, 0, 0)
        yt = sample['position']['yt'] = OrderedDict()
        self._fill_position(yt, 0, 0, 0)
        zt = sample['position']['zt'] = OrderedDict()
        self._fill_position(zt, 0, 0, 0)

        setup = measurement['setup'] = OrderedDict()
        setup['collimator_1'] = "15'"

        setup['slit_m'] = OrderedDict()
        for x in ['horizontal_clearance', 'vertical_clearance']:
            p = setup['slit_m'][x] = OrderedDict()
            self._fill_position(p, 0, 0, 0)

        setup['monochromator'] = OrderedDict()

        setup['slit_e'] = OrderedDict()
        p = setup['slit_e']['clearance'] = OrderedDict()
        self._fill_position(p, 0, 0, 0)

        setup['slit_p'] = OrderedDict()
        for x in ['horizontal_clearance', 'horizontal_translation',
                  'vertical_clearance', 'vertical_translation']:
            p = setup['slit_p'][x] = OrderedDict()
            self._fill_position(p, 0, 0, 0)

        setup['collimator_2'] = OrderedDict()

        measurement['scan'] = []
        self._wrote_headers = False

    def _float(self, value):
        return float(eval(value))

    def _integer(self, value):
        return int(eval(value))

    def _fill_header(self):
        bycategory = {}
        for (dev, key), (v, _, _, cat) in iteritems(self.dataset.metainfo):
            if cat:
                bycategory.setdefault(cat, []).append((dev.name, key, v))
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
        self.log.info('ADD META INFO %r', metainfo)
        return

    def addValues(self, values):
        self.log.info('ADD VALUES %r', values)
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

    def addSubset(self, point):
        if not self._wrote_header:
            self._fill_header()
            self._wrote_header = True

        scanpoint = OrderedDict()
        scanparams = OrderedDict()
        scanparams[point.devvalueinfo[0].name] = self._float(
            '%.2f' % point.devvaluelist[0])
        scanpoint['scan_parameters'] = scanparams
        for (info, val) in zip(self.dataset.detvalueinfo, point.detvaluelist):
            if info.type == 'time':
                scanpoint['time'] = self._float('%.2f' % val)
            elif info.type == 'counter':
                scanpoint['sum'] = self._integer('%d' % val)
            elif info.type == 'filename':
                scanpoint['image'] = '%s' % val
            elif info.type == 'monitor':
                scanpoint['monitor'] = self._integer('%d' % val)
            else:
                self.log.info('%s %s', info.name, info.type)
        self._data['measurement']['scan'].append(scanpoint)

    def end(self):
        history = self._data['measurement']['history']
        history['stopped'] = time.strftime(TIMEFMT)
        dump(self._data, self._file, allow_unicode=True, canonical=False,
             default_flow_style=False, indent=4)
        # self._file.close()
        # self._file = None


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
        'settypes': Override(default=['scan', 'subscan', 'point', ]),
        'semicolon': Override(default=''),
        'commentchar': Override(default='',)
    }
