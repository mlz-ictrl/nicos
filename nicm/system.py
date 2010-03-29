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


from nicm.data import Storage, Detector
from nicm.device import Device


class Logging(Device):
    """A special singleton device to configure logging."""

    parameters = {
        'logpath': ('', True, 'Path for logfiles.'),
    }


class User(Device):
    """A special singleton device that represents the user."""

    parameters = {
        'username': ('', True, 'User name.'),
        'affiliation': ('FRM II', False, 'User affiliation.'),
    }

    def __repr__(self):
        return '<User "%s">' % self.getUsername()

    def doSetUsername(self, value):
        self._params['username'] = value

    def doSetAffiliation(self, value):
        self._params['affiliation'] = value


class System(Device):
    """A special singleton device that serves for global configuration of
    the whole NICM system.
    """

    parameters = {
        'histories': ([], False, 'Global history managers for all devices.'),
    }

    attached_devices = {
        'logging': Logging,
        'user': User,
        'storage': Storage,
    }

    def __repr__(self):
        return '<NICM System>'

    def getStorage(self):
        return self._adevs['storage']

    def getUser(self):
        return self._adevs['user']
