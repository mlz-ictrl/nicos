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
"""Methods to parse setup files."""

import glob
import inspect
import os

from nicos.core.device import Device as _Class_device
from nicos.core.sessions import Session

from setupfiletool.utilities.excluded_devices import excluded_device_classes
from setupfiletool.utilities.utilities import getNicosDir

modules = {}
session = Session('SetupFileTool')


def init(log):
    # uses the provided directories to search for *.py files.
    # then tries to import that file.
    # the imported module will be appended to a dictionary, the key being
    # it's path splitted by dots an without the prepending nicos directory.
    # e.g. nicos.services.cache.server is the key to the module
    # <nicos directory>/nicos/services/cache/server.py
    # returns the dictionary.

    paths = [os.path.join(getNicosDir(), 'nicos', 'devices'),
             os.path.join(getNicosDir(), 'nicos', 'services')] + glob.glob(
        getNicosDir() + '/nicos_mlz/*/devices')

    pys = []
    for pth in paths:
        for root, _, files in os.walk(pth):
            pys += [os.path.join(root, f) for f in files if f.endswith('.py')]

    for py in pys:
        fqdn = py.split('/')
        fqdn[-1] = str(fqdn[-1])[:-3]
        prependingPathCount = len(getNicosDir().split('/'))
        for _ in range(prependingPathCount):
            fqdn.pop(0)  # cutting the path to nicos directory
        moduleName = '.'.join(fqdn)
        if moduleName.endswith('__init__'):
            moduleName = moduleName[:-9]
        if moduleName.startswith('nicos_mlz'):
            # module is from custom instrument, remove lib in it's path
            moduleName = moduleName.split('.')
            moduleName.pop(2)
            moduleName.pop(0)
            moduleName = '.'.join(moduleName)
        if moduleName.startswith('nicos'):
            moduleName = moduleName[6:]
        try:
            mod = session._nicos_import(moduleName)
            modules[moduleName] = mod
        except (ImportError, KeyError) as e:
            log.warning('Error importing ' + moduleName + ': ' + str(e))


def getDeviceClasses(instrumentPrefix):
    modkeys = []
    if instrumentPrefix is not None:
        for mod in modules:
            if mod.startswith(instrumentPrefix):
                modkeys.append(mod)
            elif mod.startswith('devices'):
                modkeys.append(mod)
            elif mod.startswith('services'):
                modkeys.append(mod)
    else:
        modkeys = modules.keys()
    # Got all modules that contain device classes eligible for this instrument.
    classes = []
    for key in modkeys:
        classesOfModule = inspect.getmembers(modules[key], inspect.isclass)
        for _class in classesOfModule:
            if issubclass(_class[1], _Class_device) and\
                    _class[1] not in classes:
                classes.append((_class[1]))

    classes = [_class for _class in sorted(classes)
               if str(_class)[14:-2] not in excluded_device_classes]
    # classes (the list) may contain classes that were imported in some module.
    # parse out those classes and remove them from the returned list.
    return_classes = []
    for _class in classes:
        _class_str = str(_class)[14:-2]
        uncombinedModule = _class_str.split('.')
        uncombinedModule.pop()
        mod = '.'.join(uncombinedModule)
        if mod in modules.keys():
            return_classes.append(_class)
    return return_classes
