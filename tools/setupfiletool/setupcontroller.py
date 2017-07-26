#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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

"""'Singleton' module for managing setups.

A Setup object represents a setup file.
Setups are distinguishable by their absolute path.
"""

import os
from copy import copy

from nicos.core.sessions.setups import readSetup
from setupfiletool.utilities.utilities import getNicosDir

# root directory containing all the setups or subdirs with setups.
setup_root = os.path.join(getNicosDir(), 'nicos_mlz')
setup_directories = {}

log = None


def __walkForSetups(log, previousDir, newDir, listOfSetups):
    # gets a root directory: previousDir and a subdirectory in the root
    # walks down every directory starting from newDir and appends every
    # *.py file it finds to the initial listOfSetups which is passed to
    # each level of recursion
    # actually appends a list of strings: first string is filename, second
    # string is the full path.
    for item in os.listdir(os.path.join(previousDir, newDir)):
        if item.endswith('.py'):
            try:
                listOfSetups.append(Setup(os.path.join(previousDir,
                                                       newDir,
                                                       item), log))
            except RuntimeError as e:
                log.warning(e.message)
        elif os.path.isdir(os.path.join(previousDir, newDir, item)):
            __walkForSetups(log, os.path.join(
                previousDir, newDir), item, listOfSetups)


def addSetup(setupDir, abspath):
    setup_directories[setupDir].append(Setup(abspath, log))


def init(logger):
    setup_directories.clear()
    log = logger
    for item in os.listdir(setup_root):
        if os.path.isdir(os.path.join(setup_root, item)):
            setup_directories[item] = []

    for setup_directory in list(setup_directories):
        abspath = os.path.join(setup_root, setup_directory)
        if not os.path.isdir(os.path.join(abspath, 'setups')):
            setup_directories[setup_directory] = []
            continue

        setups = []
        __walkForSetups(log, abspath, 'setups', setups)
        setup_directories[setup_directory] = setups


class Setup(object):
    def __init__(self, abspath, log):
        info = {}
        readSetup(info, abspath, log)

        self.abspath = abspath
        if not info:
            raise RuntimeError('Could not load setup ' + abspath)
        self.name = info.keys()[0]
        self.edited = False

        self.extended = copy(info[self.name]['extended'])
        self.description = copy(info[self.name]['description'])
        self.includes = copy(info[self.name]['includes'])
        self.sysconfig = copy(info[self.name]['sysconfig'])
        self.alias_config = copy(info[self.name]['alias_config'])
        self.excludes = copy(info[self.name]['excludes'])
        self.group = copy(info[self.name]['group'])
        self.modules = copy(info[self.name]['modules'])
        self.startupcode = copy(info[self.name]['startupcode'])
        self.devices = {}
        devs = info[self.name]['devices']
        for deviceName in devs:
            self.devices[deviceName] = (Device(deviceName,
                                               devs[deviceName][0],
                                               copy(devs[deviceName][1]))
                                        )


class Device(object):
    def __init__(self, name, classString='', parameters=None):
        if parameters is None:
            parameters = {}
        self.name = name
        self.classString = classString
        self.parameters = parameters
