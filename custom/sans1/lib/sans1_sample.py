#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""Sans1 Sample device."""

from nicos import session
from nicos.core import Param, Override, dictof, none_or
from nicos.devices.sample import Sample as NicosSample


class Sans1Sample(NicosSample):
    """A special device to represent a sample.

    Represent a set of samples with a currently activated one.
    Can be used via a ParamDevice as an attached device of a samplechanger to
    autoselect the right entry.
    """

    parameters = {
        'samplenames':  Param('Sample names', type=dictof(int, str),
                              settable=True, category='sample', default={}),
        'activesample': Param('None or index of currently used sample on'
                              ' samplechanger', type=none_or(int),
                              settable=True, category='sample'),
    }
    parameter_overrides = {
        'samplename' : Override(volatile = True),
    }

    def reset(self):
        """Reset experiment-specific information."""
        NicosSample.reset(self)
        self.samplenames = {}

    def setName(self, idx, name):
        """ sets name of sample in sampleslot <idx> to <name>

        if <idx> is 0 or None, use self.activesample instead"""
        if not idx:
            idx = self.activesample or 0
        d = {}
        d.update(self.samplenames)
        d[int(idx)] = name
        self.samplenames = d  # trigger transfer to cache

    def getName(self, idx):
        """returns name of sample in slot <idx> or the current one,
        if <idx> is 0 or None
        """
        if idx:
            return self.samplenames.get(int(idx),
                '<unknown sample> at sample position %d' % idx)
        return self.samplenames.get(self.activesample or 0, '<unknown sample>')

    def doReadSamplename(self):
        """always derive samplename from the currently used one...."""
        return self.getName(None)

    def doWriteSamplename(self, name):
        NicosSample.doWriteSamplename(self, name)
        self.setName(None, name)

    def doWriteActivesample(self, num):
        """change the current sample to another one"""
        # self.samplename = self.getName(num)
        # maybe this is better (Exp.datapath adjustments?):
        # see for example the antares experiment.
        # sans people want to deviate from the default too :(
        self._setROParam('activesample', num)
        samplename = self.getName(num)
        if 'Exp' in session.devices and samplename:
            session.experiment.newSample(samplename, {})
