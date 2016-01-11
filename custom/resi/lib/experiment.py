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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#   Björn Pedersen <bjoern.pedersen@frm2.tum.de>
#
# *****************************************************************************

"""
NICOS Resi Experiment.
"""

import os
from os import path

from nicos.core import Param, UsageError
from nicos.utils import disableDirectory
from nicos.devices.experiment import Experiment
from nicos.frm2.proposaldb import queryCycle


class ResiExperiment(Experiment):

    parameters = {
        'cycle': Param('Current reactor cycle', type=str, settable=True),
    }

    def proposalpath_of(self, proposal):
        """deviate from default of <dataroot>/<year>/<proposal>"""
        return path.join(self.dataroot, proposal)

    def new(self, proposal, title=None, **kwds):
        # Resi-specific handling of proposal number
        if isinstance(proposal, int):
            proposal = 'p%s' % proposal
        if proposal in ('template', 'current'):
            raise UsageError(self, 'The proposal names "template" and "current"'
                             ' are reserved and cannot be used')

        try:
            old_proposal = path.basename(os.readlink(self.proposalsymlink))
        except Exception:
            if path.exists(self.proposalsymlink):
                self.log.error('"current" link to old experiment dir exists '
                                'but cannot be read', exc=1)
            else:
                self.log.warning('no old experiment dir is currently set',
                                  exc=1)
        else:
            if old_proposal.startswith('p'):
                disableDirectory(self.proposalpath_of(old_proposal), logger=self.log)
            os.unlink(self.proposalsymlink)

        # query new cycle
        if 'cycle' not in kwds:
            try:
                cycle, _started = queryCycle()
                kwds['cycle'] = cycle
            except Exception:
                self.log.error('cannot query reactor cycle, please give a '
                                '"cycle" keyword to this function')
        self.cycle = kwds['cycle']

        # checks are done, set the new experiment
        Experiment.new(self, proposal, title)

        # fill proposal info from database
        if proposal.startswith('p'):
            try:
                propnumber = int(proposal[1:])
            except ValueError:
                pass
            else:
                self._fillProposal(propnumber)  # wrong way around !

        # create new data path and expand templates
        os.symlink(proposal, self.proposalsymlink)
        Experiment.datapathChanged(self)  # is this needed here?

        self._handleTemplates(proposal, kwds)

    def _handleTemplates(self, proposal, kwds):
        """hhm"""
        pass

    def finish(self):
        pass
