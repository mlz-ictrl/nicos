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
NICOS Experiment devices.
"""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"


from nicos import session
from nicos.data import NeedsDatapath
from nicos.utils import listof
from nicos.device import Device, Param


class Sample(Device):
    """A special device to represent a sample."""

    parameters = {
        'samplename':  Param('Sample name', type=str, settable=True),
    }


class Experiment(Device):
    """A special singleton device to represent the experiment."""

    parameters = {
        'title':          Param('Experiment title', type=str, settable=True,
                                category='experiment'),
        'proposalnumber': Param('Proposal number', type=int, settable=True,
                                category='experiment'),
        'users':          Param('User names', type=listof(str), settable=True,
                                category='experiment'),
        'datapath':       Param('Path for data files', type=str,
                                settable=True, category='experiment'),
    }

    attached_devices = {
        'sample': Sample,
    }

    def new(self, proposalnumber, title=None):
        if not isinstance(proposalnumber, int):
            proposalnumber = int(proposalnumber)
        self.proposalnumber = proposalnumber
        if title is not None:
            self.title = title
        self.users = []

    def addUser(self, name, email, affiliation=None):
        user = '%s <%s>' % (name, email)
        if affiliation is not None:
            user += ' -- ' + affiliation
        self.users = self.users + [user]

    def doWriteDatapath(self, value):
        for dev in session.devices.itervalues():
            if isinstance(dev, NeedsDatapath):
                dev._setDatapath(value)
