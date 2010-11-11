#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   NICOS System device
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
#   The basic NICOS methods for the NICOS daemon (http://nicos.sf.net)
#
#   Copyright (C) 2009 Jens Krüger <jens.krueger@frm2.tum.de>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# *****************************************************************************

"""
NICOS system device.
"""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"


from nicm.data import DataSink
from nicm.device import Device, Param


class System(Device):
    """A special singleton device that serves for global configuration of
    the NICM system.
    """

    parameters = {
        'logpath': Param('Path for logfiles', type=str, mandatory=True),
        'datapath': Param('Path for data files', type=str, mandatory=True),
    }

    attached_devices = {
        'cache': Device,
        'sinks': [DataSink],
    }

    def __repr__(self):
        return '<NICM System>'

    @property
    def cache(self):
        return self._adevs['cache']

    def getSinks(self, scantype=None):
        if scantype is None:
            return self._adevs['sinks']
        else:
            return [sink for sink in self._adevs['sinks']
                    if not sink.scantypes or scantype in sink.scantypes]

    def doWriteDatapath(self, value):
        for sink in self._adevs['sinks']:
            sink.setDatapath(value)
