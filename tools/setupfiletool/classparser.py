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

import os
import glob
import imp

from setupfiletool.utilities.utilities import getNicosDir


def importModules():
    # uses the provided directories to search for *.py files.
    # then tries to import that file.
    # the imported module will be appended to a dictionary, the key being
    # it's path splitted by dots an without the prepending nicos directory.
    # e.g. nicos.services.cache.server is the key to the module
    # <nicos directory>/nicos/services/cache/server.py
    # returns the dictionary.
    modules = {}

    paths = [os.path.join(getNicosDir(), 'nicos', 'devices'),
             os.path.join(getNicosDir(), 'nicos', 'services')] + glob.glob(
        getNicosDir() + '/custom/*/lib')

    pys = []
    for pth in paths:
        for root, _, files in os.walk(pth):
            pys += [os.path.join(root, f) for f in files if f.endswith('.py')]

    for py in pys:
        name, _ = os.path.splitext(os.path.basename(py))
        pyfile, filename, data = imp.find_module(name, [os.path.dirname(py)])
        try:
            # load module
            try:
                m = imp.load_module(name, pyfile, filename, data)
            except KeyError:
                # Todo: Fix special cases!
                continue
            # loading successful. create name for dictionary key
            fqdn = py.split("/")
            fqdn[-1] = str(fqdn[-1])[:-3]
            prependingPathCount = len(getNicosDir().split("/"))
            for _ in range(prependingPathCount):
                fqdn.pop(0)  # cutting the path to nicos directory
            moduleName = ".".join(fqdn)
            # add to dictionary
            if moduleName.endswith("__init__"):
                moduleName = moduleName[:-9]
            if not moduleName.startswith("nicos"):
                # module is from custom instrument, remove lib in it's path
                moduleName = moduleName.split(".")
                moduleName.pop(2)
                moduleName = ".".join(moduleName)
            modules[moduleName] = m
        except (ImportError, ValueError, NameError):  # as e:
            pass
            # print('failed in: ' + py + '\n    because: ' + e.args[0])
    return modules
