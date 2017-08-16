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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

"""NICOS Sample device."""

from nicos import session
from nicos.core import Moveable, Param, Override, status, oneof, none_or, \
    dictof, anytype, InvalidValueError
from nicos.utils import safeName


class Sample(Moveable):
    """A special device to represent a sample.

    An instance of this class is used as the *sample* attached device of the
    `Experiment` object.  It can be subclassed to add special sample
    properties, such as lattice and orientation calculations, or more
    parameters describing the sample.

    The device stores the collection of all currently defined samples in
    its `samples` parameter.  When changing samples, it will overwrite the
    device's other parameters with these values.
    """

    parameters = {
        'samplename':   Param('Current sample name', type=str, settable=True,
                              category='sample'),
        'samplenumber': Param('Current sample number: e.g. the position in '
                              'a sample changer or the index of the sample '
                              'among all defined samples', type=none_or(int),
                              settable=True),
        'samples':      Param('Information about all defined samples',
                              type=dictof(int, dictof(str, anytype)),
                              settable=True, userparam=False, preinit=True),
    }

    parameter_overrides = {
        'unit': Override(mandatory=False, default=''),
    }

    valuetype = str

    def doRead(self, maxage=0):
        return self.samplename

    def doStatus(self, maxage=0):
        return status.OK, ''

    def doStart(self, target):
        self.select(target)

    def doIsAtTarget(self, pos):
        # never warn about self.target mismatch
        return True

    @property
    def filename(self):
        return safeName(self.samplename)

    def doWriteSamplename(self, name):
        if name:
            session.elogEvent('sample', name)

    def clear(self):
        """Clear experiment-specific information."""
        self.samplename = ''
        self.samplenumber = None
        self.samples = {}

    def new(self, parameters):
        """Create and select a new sample."""
        # In this simple base class, we expect the user to use only NewSample,
        # so we remove stored sample information every time to avoid a buildup
        # of unused sample information.
        self.samples = {0: parameters}
        self.select(0)

    def set(self, number, parameters):
        """Set sample information for sample no. *number*."""
        if number is None:
            raise InvalidValueError(self, 'cannot use None as sample number')
        info = self.samples.copy()
        if number in info:
            self.log.warning('overwriting parameters for sample %s (%s)',
                             number, info[number]['name'])
        info[number] = parameters
        self.samples = info

    def select(self, number_or_name):
        """Select sample with given number or name."""
        number = self._findIdent(number_or_name)
        try:
            parameters = self.samples[number]
        except KeyError:
            raise InvalidValueError(self, 'cannot find sample with number '
                                    'or name %r' % number_or_name)
        self._applyParams(number, parameters)
        session.experiment.newSample(parameters)
        self.poll()

    def _findIdent(self, number_or_name):
        """Find sample number.  Can be overridden in subclasses."""
        # look by number
        if number_or_name in self.samples:
            return number_or_name
        # look by name
        found = None
        for (number, parameters) in self.samples.items():
            if parameters['name'] == number_or_name:
                if found is not None:
                    # two samples with same name found...
                    raise InvalidValueError(self, 'two samples with name %r '
                                            'were found, please use the '
                                            'sample number (%s or %s)' %
                                            (number_or_name, found, number))
                found = number
        return found

    def _applyParams(self, number, parameters):
        """Apply sample parameters.  Override in subclasses.

        All parameters beside the name should be treated as optional by
        subclasses, since they will not be provided for the empty sample
        created by NewExperiment.
        """
        self.samplenumber = number
        self.samplename = parameters['name']
        self._setROParam('target', parameters['name'])

    def doUpdateSamples(self, info):
        self.valuetype = oneof(*(info[n]['name'] for n in sorted(info)))
