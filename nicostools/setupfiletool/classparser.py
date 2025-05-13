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
#   Andreas Schulz <andreas.schulz@frm2.tum.de>
#
# *****************************************************************************
"""Methods to parse setup files."""

import inspect
import os
from pathlib import Path

from nicos.core.device import Device as _Class_device
from nicos.core.sessions import Session

from .utilities.excluded_devices import excluded_device_classes
from .utilities.utilities import getClass, getNicosDir

modules = {}
session = Session('SetupFileTool')


def init(log):
    # uses the provided directories to search for *.py files.
    # then tries to import that file.
    # the imported module will be appended to a dictionary, the key being
    # its path split by dots and without the prepending nicos directory.
    # e.g. nicos.services.cache.server is the key to the module
    # <nicos directory>/nicos/services/cache/server.py
    # returns the dictionary.

    paths = [
        Path().joinpath(getNicosDir(), 'nicos', 'devices'),
        Path().joinpath(getNicosDir(), 'nicos', 'services')] + list(
        Path(getNicosDir()).glob(
            '%s' % Path().joinpath('nicos_*', 'devices'))) + list(
        Path(getNicosDir()).glob(
            '%s' % Path().joinpath('nicos_*', '*', 'devices')))

    pys = []
    for pth in paths:
        for root, _, files in os.walk(pth):
            pys += [Path().joinpath(root, f)
                    for f in files if f.endswith('.py')]

    for py in pys:
        moduleFile = py.relative_to(getNicosDir())
        if moduleFile.name == '__init__.py':
            moduleName = '.'.join(moduleFile.parent.parts)
        else:
            moduleName = '.'.join(moduleFile.with_suffix('').parts)
        try:
            mod = session._nicos_import(moduleName)
            modules[moduleName] = mod
        except (ImportError, KeyError, NameError) as e:
            log.warning('Error importing %s: %s', moduleName, e)


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
        modkeys = list(modules.keys())
    # Got all modules that contain device classes eligible for this instrument.
    classes = []
    for key in modkeys:
        classesOfModule = inspect.getmembers(modules[key], inspect.isclass)
        for _class in classesOfModule:
            if issubclass(_class[1], _Class_device) and \
                    _class[1] not in classes:
                classes.append(_class[1])

    classes = [_class for _class in classes
               if getClass(_class) not in excluded_device_classes]
    # classes (the list) may contain classes that were imported in some module.
    # parse out those classes and remove them from the returned list.
    return_classes = []
    for _class in classes:
        mod = '.'.join(getClass(_class).split('.')[:-1])
        if mod in modules:
            return_classes.append(_class)
    return return_classes
