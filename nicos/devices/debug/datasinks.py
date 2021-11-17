#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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

"""A NICOS data sink for debugging applications."""

from nicos.core.constants import BLOCK, POINT, SCAN, SUBSCAN
from nicos.core.data import DataSink, DataSinkHandler
from nicos.core.params import Override


class DebugDataSinkHandler(DataSinkHandler):

    def prepare(self):
        self.log.info('%r: prepare called #%s (%s)', self.dataset.settype,
                      self.dataset.number, len(self.dataset.subsets))

    def begin(self):
        self.log.info('%r: begin called #%s (%s)', self.dataset.settype,
                      self.dataset.number, len(self.dataset.subsets))

    def putMetainfo(self, metainfo):
        self.log.info('%r: putMetainfo called: #%s (%s): %r',
                      self.dataset.settype, self.dataset.number,
                      len(self.dataset.subsets), metainfo)
        self.log.info('devices: %r',
                      [dev.name for dev in self.dataset.devices])

    def putValues(self, values):
        # the values are set for each change of each devices so it may to many
        # class, if needed loglevel = 'debug' displays it
        self.log.debug('%r: putValues called', self.dataset.settype)
        self.log.debug('   values: %r', values)

    def putResults(self, quality, results):
        # To much output in case of 2D data, but may be enabled by
        # loglevel = 'debug'
        self.log.debug('%r: putResults called:', self.dataset.settype)
        self.log.debug('   quality: %r', quality)
        self.log.debug('   results: %r', results)

    def addSubset(self, subset):
        self.log.info('%r: addSubset called: %r', self.dataset.settype,
                      subset.settype)
        self.log.info('  subset.values: %r', subset.values)
        self.log.info('  subset.canonical values: %r', subset.canonical_values)
        if subset.devvaluelist:
            self.log.info('  subset.devvaluelist[0]: %s', subset.devvaluelist[0])
        self.log.info('  settype: %s, #%s (%s)', self.dataset.settype,
                      subset.number, len(self.dataset.subsets))

    def end(self):
        self.log.info('%r: end called', self.dataset.settype)


class DebugDataSink(DataSink):
    """Debug data sink.

    This device only displays some data handling specific information during
    the counts and scans.  It does not persist any data to files.

    .. note:: It should be used only for debugging purposes.
    """

    handlerclass = DebugDataSinkHandler

    parameter_overrides = {
        'settypes': Override(default=[POINT, SCAN, SUBSCAN, BLOCK]),
    }
