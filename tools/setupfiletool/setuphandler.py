#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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
#   Andreas Schulz <andreas.schulz@frm2.tum.de>
#
# *****************************************************************************

from os import path
import logging

from nicos.core.sessions.setups import readSetup

class SetupHandler(object):
    def __init__(self, parent = None):
        self.log = logging.getLogger()
        self.info = {}
        self.unsavedChanges = False
        self.currentSetupPath = ''
        self.setupDisplayed = False
        self.isCustomFile = False


    def changedSlot(self):
        self.unsavedChanges = True


    def clear(self):
        self.info.clear()
        self.unsavedChanges = False
        self.currentSetupPath = ''
        self.setupDisplayed = False
        self.isCustomFile = False


    def readSetupFile(self, setupFile):
        # uses nicos.core.sessions.setups.readSetup() to read a setup file and
        # put the information in the self.info dictionary.
        self.clear()
        readSetup(self.info,
                  path.dirname(setupFile),
                  setupFile,
                  self.log)
        self.currentSetupPath = setupFile


    def readSetupReturnDict(self, setupFile):
        #for when you want to read a setup but don't destroy the currently
        #loaded info
        info = {}
        readSetup(info,
                  path.dirname(setupFile),
                  setupFile,
                  self.log)
        return info


    def save(self):
        self.clear()
