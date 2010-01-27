#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   NICOS fundamental user commands
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#   $Author$
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
Module for basic user commands.
"""

import inspect
import __builtin__

from nicm import nicos
from nicm.device import Device
from nicm.utils import format_docstring, print_table

from nicm.commands.output import printinfo, printexception

__commands__ = [
    'NicmSetup', 'NicmAddSetup', 'NicmFactory', 'NicmDestroy',
    'NicmPrint', 'NicmExport', 'listcommands', 'help', #'dir',
]


# -- new versions of builtins --------------------------------------------------

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
        printinfo(format_docstring(real_func.__doc__ or '', '   '))

def dir(obj=None):
    if obj is None:
        return __builtin__.dir()
    return [name for name in __builtin__.dir(obj) if not name.startswith('_')]


# -- other basic commands ------------------------------------------------------

def NicmSetup(setupname):
    """Load the given setup instead of the current one."""
    nicos.unload_setup()
    try:
        nicos.load_setup(setupname)
    except Exception:
        printexception()
        nicos.load_setup('startup')

def NicmAddSetup(setupname):
    """Load the given setup additional to the current one."""
    nicos.load_setup(setupname)

def NicmExport(name, object):
    """Export the given object into the NICOS namespace."""
    nicos.export(name, object)

def NicmFactory(*devnames):
    """Create all given devices."""
    for devname in devnames:
        nicos.create_device(devname, explicit=True)

def NicmDestroy(*devnames):
    """Destroy all given devices."""
    for devname in devnames:
        nicos.destroy_device(devname)

def NicmPrint(pm, text):
    printinfo(text)

def listcommands():
    printinfo('Available commands:')
    items = []
    for obj in nicos.get_exported_objects():
        if hasattr(obj, 'is_usercommand'):
            real_func = getattr(obj, 'real_func', obj)
            argspec = inspect.formatargspec(*inspect.getargspec(real_func))
            docstring = real_func.__doc__ or ' '
            items.append((real_func.__name__ + argspec,
                          docstring.splitlines()[0]))
    items.sort()
    print_table(('name', 'description'), items, printinfo)
