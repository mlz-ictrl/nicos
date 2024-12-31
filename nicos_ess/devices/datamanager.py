# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Matt Clarke <matt.clarke@ess.eu>
#
# *****************************************************************************
"""ESS datamanager device."""
import os

from nicos import session
from nicos.core.data.manager import DataManager as BaseDataManager
from nicos.utils import readFileCounter, updateFileCounter


class DataManager(BaseDataManager):
    def incrementCounters(self, countertype):
        """Increment the counters for the given *countertype*.

        This should update the counter files accordingly.

        Returns a list of (counterattribute, value) tuples to set on the
        dataset.
        """
        exp = session.experiment
        filepath = os.path.join(exp.dataroot, exp.counterfile)
        if not os.path.isfile(filepath):
            session.log.warning('creating new empty file counter file at %s',
                                filepath)
        nextnum = readFileCounter(filepath, countertype) + 1
        updateFileCounter(filepath, countertype, nextnum)
        return [('counter', nextnum)]
