#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id $
#
# Description:
#   NICOS Experiment devices
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
NICOS Experiment devices.
"""

__author__  = "$Author $"
__date__    = "$Date $"
__version__ = "$Revision $"


from nicm.device import Device


class User(Device):
    """A special singleton device that represents the user."""

    parameters = {
        'name': ('', True, 'User name.'),
        'email': ('', True, 'E-Mail address of user.'),
        'affiliation': ('FRM II', False, 'User affiliation.'),
    }

    def __repr__(self):
        return '<User "%s">' % self.getName()

    def doSetName(self, value):
        self._params['name'] = value

    def doSetEmail(self, value):
        self._params['email'] = value

    def doSetAffiliation(self, value):
        self._params['affiliation'] = value


class Experiment(Device):
    """A special singleton device to represent the experiment."""

    parameters = {
        'title': ('', False, 'Experiment title.'),
        'proposalnumber': (0, False, 'Proposal number.'),
    }

    attached_devices = {
        'users': [User],
    }

    def getUsers(self):
        return self._adevs['users']

    def doSetTitle(self, value):
        self._params['title'] = value

    def doSetProposalnumber(self, value):
        self._params['proposalnumber'] = value

    def new(self, proposalnumber, title=None):
        if not isinstance(proposalnumber, int):
            proposalnumber = int(proposalnumber)
        self.setProposalnumber(proposalnumber)
        if title is not None:
            self.setTitle(title)
        self._adevs['users'] = []

    def addUser(self, name, email, affiliation=None):
        config = {'name': name, 'email': email}
        if affiliation is not None:
            config['affiliation'] = affiliation
        user = User(name, config)
        self._adevs['users'].append(user)
