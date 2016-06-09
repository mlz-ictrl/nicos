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

"""Base classes for YAML based datasinks."""

from datetime import datetime
from time import time as currenttime

import yaml

from nicos import session
from nicos.core import NicosError
from nicos.devices.datasinks.image import SingleFileSinkHandler
from nicos.pycompat import from_maybe_utf8
from nicos.utils import AutoDefaultODict


# Subclass to support flowed (inline) lists
class FlowSeq(list):
    pass


# The improved YAML dumper
class ImprovedDumper(yaml.Dumper):
    pass


def odict_representer(dumper, data):
    return dumper.represent_mapping(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        data.items())


def flowseq_representer(dumper, data):
    return dumper.represent_sequence(
        yaml.resolver.BaseResolver.DEFAULT_SEQUENCE_TAG,
        data, flow_style=True)

ImprovedDumper.add_representer(AutoDefaultODict, odict_representer)
ImprovedDumper.add_representer(FlowSeq, flowseq_representer)
ImprovedDumper.add_representer(
    str, yaml.representer.SafeRepresenter.represent_str)
ImprovedDumper.add_representer(
    unicode, yaml.representer.SafeRepresenter.represent_unicode)


def improved_dump(data, stream=None, **kwds):
    return yaml.dump(data, stream, ImprovedDumper, allow_unicode=True,
                     encoding='utf-8', default_flow_style=False, indent=4,
                     width=70, **kwds)


def nice_datetime(dt):
    if isinstance(dt, float):
        dt = datetime.fromtimestamp(dt)
    rounded = dt.replace(microsecond=0)
    return rounded.isoformat()


class YAMLBaseFileSinkHandler(SingleFileSinkHandler):

    filetype = 'MLZ.YAML'  # to be overwritten in derived classes
    accept_final_images_only = True

    def _readdev(self, devname):
        try:
            return session.getDevice(devname).read()
        except NicosError:
            return None

    def _devpar(self, devname, parname):
        try:
            return getattr(session.getDevice(devname), parname)
        except NicosError:
            return None

    def _dict(self):
        return AutoDefaultODict()

    def _flowlist(self, *args):
        return FlowSeq(*args)

    def writeData(self, fp, image):
        """Save in YAML format."""
        fp.seek(0)

        expdev = session.experiment
        instrdev = session.instrument

        o = AutoDefaultODict()
        instr = o['instrument']
        instr['name'] = instrdev.instrument
        instr['facility'] = instrdev.facility
        instr['operator'] = ', '.join(instrdev.operators)
        instr['website'] = instrdev.website
        instr['references'] = [AutoDefaultODict({'doi': instrdev.doi})]

        objects = ['angle', 'clearance', 'current', 'displacement', 'duration',
                   'energy', 'frequency', 'temperature', 'wavelength']
        units = ['deg', 'mm', 'A', 'mm', 's', 'eV', 'hertz', 'K', 'A']

        o['format']['identifier'] = self.__class__.filetype
        for obj, unit in zip(objects, units):
            o['format']['units'][obj] = unit

        exp = o['experiment']
        # TODO: use experiment number when we have it in NICOS
        exp['number'] = expdev.proposal
        exp['proposal'] = expdev.proposal
        exp['title'] = from_maybe_utf8(expdev.title)
        exp['authors'] = []
        authors = [
            {'name': from_maybe_utf8(expdev.users),
             'roles': ['principal_investigator']},
            {'name':  from_maybe_utf8(expdev.localcontact),
             'roles': ['local_contact']},
        ]
        for author in authors:
            a = AutoDefaultODict()
            a['name'] = author['name']
            a['roles'] = FlowSeq(author['roles'])
            exp['authors'].append(a)

        meas = o['measurement']
        meas['number'] = self.dataset.number
        meas['unique_identifier'] = '%s/%s/%s' % (
            expdev.proposal, self.dataset.counter, self.dataset.number)

        hist = meas['history']
        hist['started'] = nice_datetime(self.dataset.started)
        hist['stopped'] = nice_datetime(currenttime())

        sample = meas['sample']['description']
        sample['name'] = from_maybe_utf8(expdev.sample.samplename)

        self._write_instr_data(meas, image)

        improved_dump(o, fp)
        fp.flush()

    def _write_instr_data(self, meas_root, image):
        raise NotImplementedError('implement _write_instr_data')
