#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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
# *****************************************************************************

"""
NICOS MIRA Experiment.
"""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import os
import time

from nicos import session
from nicos.experiment import Experiment
from nicos.data import NeedsDatapath, Dataset
from nicos.utils import listof
from nicos.device import Device, Param
from nicos.loggers import UserLogfileHandler


class MiraExperiment(Experiment):
    def doInit(self):
        Experiment.doInit(self)
        self._uhandler = UserLogfileHandler(os.path.join(self.datapath, 'log'))
        session.addLogHandler(self._uhandler)

    def new(self, proposalnumber, title=None):
        Experiment.new(self, proposalnumber, title)
        self.datapath = '/data/%s/%s' % (time.strftime('%Y'), proposalnumber)
        if not os.path.isdir(os.path.join(self.datapath, 'scripts')):
            os.mkdir(os.path.join(self.datapath, 'scripts'))
        if not os.path.isdir(os.path.join(self.datapath, 'log')):
            os.mkdir(os.path.join(self.datapath, 'log'))
        self._uhandler.changeDirectory(os.path.join(self.datapath, 'log'))
