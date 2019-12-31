#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

"""NICOS MARIA Experiment."""

from __future__ import absolute_import, division, print_function

from os import path

from nicos.core import SIMULATION
from nicos.utils import safeName

from nicos_mlz.devices.experiment import Experiment as _Experiment


class Experiment(_Experiment):
    """MARIA specific experiment class which creates a subdirectory for each
    sample and copies all template files to the corresponding scripts
    directory."""

    def newSample(self, parameters):
        if self._mode == SIMULATION:
            _Experiment.newSample(self, parameters)
            return

        self.sampledir = safeName(parameters["name"])
        _Experiment.newSample(self, parameters)
        self.log.debug("changed samplepath to: %s" % self.samplepath)
        # expand/copy templates
        if self.getProposalType(self.proposal) != 'service' and self.templates:
            params = dict(parameters) if parameters else dict()
            params.update(self.propinfo)
            self.handleTemplates(self.proposal, params)

    @property
    def elogpath(self):
        return path.join(self.proposalpath, 'logbook')
