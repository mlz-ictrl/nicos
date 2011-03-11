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

from __future__ import with_statement

"""Module for basic user commands."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import inspect
import __builtin__

from nicos import session
from nicos.utils import formatDocstring, printTable
from nicos.device import Device
from nicos.system import EXECUTIONMODES
from nicos.commands import usercommand
from nicos.commands.output import printinfo, printexception


# -- help and introspection ----------------------------------------------------

@usercommand
def help(obj=None):
    """Show help for a command or other object."""
    if obj is None:
        listcommands()
    elif isinstance(obj, Device):
        printinfo('%s is a device of class %s.' % (obj.getPar('name'),
                                                   obj.__class__.__name__))
        printinfo('Its description is: %s.' % obj.getPar('description'))
    elif not inspect.isfunction(obj):
        __builtin__.help(obj)
    else:
        # for functions, print arguments and docstring
        real_func = getattr(obj, 'real_func', obj)
        argspec = inspect.formatargspec(*inspect.getargspec(real_func))
        printinfo('Usage: ' + real_func.__name__ + argspec)
        printinfo(formatDocstring(real_func.__doc__ or '', '   '))

__builtin__.__orig_dir = dir

@usercommand
def dir(obj=None):
    if obj is None:
        return __builtin__.__orig_dir()
    return [name for name in __builtin__.__orig_dir(obj)
            if not name.startswith(('_', 'do'))]

@usercommand
def listcommands():
    """List all available commands."""
    printinfo('Available commands:')
    items = []
    for obj in session.getExportedObjects():
        if hasattr(obj, 'is_usercommand'):
            real_func = getattr(obj, 'real_func', obj)
            argspec = inspect.formatargspec(*inspect.getargspec(real_func))
            docstring = real_func.__doc__ or ' '
            items.append((real_func.__name__ + argspec,
                          docstring.splitlines()[0]))
    items.sort()
    printTable(('name', 'description'), items, printinfo)


# -- other basic commands ------------------------------------------------------

@usercommand
def NewSetup(setupname):
    """Load the given setup instead of the current one."""
    # refresh setup files
    session.readSetups()
    session.unloadSetup()
    try:
        session.loadSetup(setupname)
    except Exception:
        printexception()
        session.loadSetup('startup')

@usercommand
def AddSetup(setupname):
    """Load the given setup additional to the current one."""
    session.readSetups()
    session.loadSetup(setupname)

@usercommand
def ListSetups():
    """Print a list of all known setups."""
    printinfo('Available setups:')
    items = []
    for name, info in session.getSetupInfo().iteritems():
        if info['group'] == 'special':
            continue
        items.append((name, info['name'], ', '.join(sorted(info['devices']))))
    items.sort()
    printTable(('name', 'description', 'devices'), items, printinfo)

@usercommand
def Keep(name, object):
    """Export the given object into the NICOS namespace."""
    session.export(name, object)

@usercommand
def CreateDevice(*devnames):
    """Create all given devices."""
    for devname in devnames:
        session.createDevice(devname, explicit=True)

@usercommand
def DestroyDevice(*devnames):
    """Destroy all given devices."""
    for devname in devnames:
        if isinstance(devname, Device):
            devname = devname.name
        session.destroyDevice(devname)

@usercommand
def CreateAllDevices():
    """Create all devices in the current setup that are not marked as
    lowlevel devices.
    """
    for devname, (_, devconfig) in session.configured_devices.iteritems():
        if devconfig.get('lowlevel', False):
            continue
        session.createDevice(devname, explicit=True)

@usercommand
def NewExperiment(proposalnumber, title):
    """Start a new experiment."""
    session.system.experiment.new(proposalnumber, title)

@usercommand
def SaveState():
    """Return statements that restore the current state."""
    ret = ['NewSetup(%r)\n' % session.explicit_setups[0]]
    ret += ['AddSetup(%r)\n' % setup
            for setup in session.explicit_setups[1:]]
    return ''.join(ret + [session.devices[dev].save()
                          for dev in sorted(session.devices)])

@usercommand
def SetMode(mode):
    """Set the execution mode.

    Valid modes are: """
    session.system.setMode(mode)
    printinfo('execution mode set to %s' % mode)

SetMode.__doc__ += ', '.join(EXECUTIONMODES)

@usercommand
def ClearCache(devname):
    """Clear all cached information for a given device."""
    if isinstance(devname, Device):
        devname = devname.name
    session.system.cache.clear(devname)
    printinfo('cleared cached information for %s' % devname)


class _Scope(object):
    def __init__(self, name):
        self.name = name
    def __enter__(self):
        session.beginActionScope(self.name)
    def __exit__(self, *args):
        session.endActionScope()

@usercommand
def UserInfo(name):
    """Return an object that can be used like this:

    with UserInfo('Qscan around (1,1,0)'):
        qscan(...)
    """
    return _Scope(name)


@usercommand
def run(filename):
    """Run a script file."""
    # XXX standard script dir?
    printinfo('running user script: ' + filename)
    with open(filename, 'r') as fp:
        code = unicode(fp.read(), 'utf-8')
        with _Scope(filename):
            exec code in session.getLocalNamespace(), session.getNamespace()
    printinfo('finished user script: ' + filename)
