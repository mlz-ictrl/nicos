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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""
Setup file handling.
"""

import os
from os import path

from nicos.pycompat import exec_, iteritems, listitems


SETUP_GROUPS = set([
    'basic', 'optional', 'plugplay', 'lowlevel', 'special'
])


def readSetups(paths, logger):
    infodict = {}
    for rootpath in paths:
        for root, _, files in os.walk(rootpath, topdown=False):
            for filename in files:
                if not filename.endswith('.py'):
                    continue
                readSetup(infodict, path.join(root, filename), logger)
    # check if all includes exist
    for name, info in iteritems(infodict):
        if info is None:
            continue  # erroneous setup
        for include in info['includes']:
            if not infodict.get(include):
                logger.error('Setup %s includes setup %s which does not '
                             'exist or has errors' % (name, include))
                infodict[name] = None

    return infodict

class Device(tuple):
    pass

def prepareNamespace(setupname):
    """Return a namespace prepared for reading setup "setupname"."""
    # device() is a helper function to make configuration prettier
    ns = {
        'device': lambda cls, **params: Device((cls, params)),
        'setupname': setupname,
    }
    if path.basename(setupname).startswith('monitor'):
        ns['Row'] = lambda *args: args
        ns['Column'] = lambda *args: args
        ns['BlockRow'] = lambda *args: args
        ns['Block'] = lambda *args, **kwds: (args, kwds)
        ns['Field'] = lambda *args, **kwds: args or kwds
    if path.basename(setupname).startswith('guiconfig'):
        from nicos.clients.gui.config import vsplit, hsplit, window, panel, \
            tool, docked, tabbed, setups
        ns['vsplit'] = vsplit
        ns['hsplit'] = hsplit
        ns['window'] = window
        ns['panel'] = panel
        ns['tool'] = tool
        ns['docked'] = docked
        ns['tabbed'] = tabbed
        ns['setups'] = setups
    return ns

def fixup_stacked_devices(devdict):
    """replaces <adevname> = Device(..) entries in devices dict

    with a proper name and move the device definition under that name.
    """
    patched = True
    while patched:
        patched = False
        # iter over all devices
        for devname, dev in devdict.items():
            # iter over all key=value pairs for dict
            for k, v in dev[1].items():
                if isinstance(v, Device): #need to fixup!
                    # guess a name:
                    n = '%s_%s' % (devname, k)
                    # 'rename' device, keeping logical connection
                    devdict[n] = v
                    dev[1][k] = n
                    patched = True
                elif isinstance(v, (tuple, list)):
                    v = list(v)
                    for idx, item in enumerate(v):
                        if not isinstance(item, (Device, str)):
                            break
                        if isinstance(item, Device):
                            n = '%s_%s%d' % (devname, k, idx+1)
                            devdict[n] = item
                            v[idx] = n
                            dev[1][k] = v
                            patched = True
    return devdict


def readSetup(infodict, filepath, logger):
    modname = path.splitext(path.basename(filepath))[0]
    try:
        with open(filepath, 'r') as modfile:
            code = modfile.read()
    except IOError as err:
        logger.exception('Could not read setup '
                         'module %r: %s' % (filepath, err))
        return
    ns = prepareNamespace(modname)
    try:
        exec_(code, ns)
    except Exception as err:
        logger.exception('An error occurred while processing '
                         'setup %r: %s' % (filepath, err))
        return
    info = {
        'description': ns.get('description', modname),
        'group': ns.get('group', 'optional'),
        'sysconfig': ns.get('sysconfig', {}),
        'includes': ns.get('includes', []),
        'excludes': ns.get('excludes', []),
        'modules': ns.get('modules', []),
        'devices': fixup_stacked_devices(ns.get('devices', {})),
        'alias_config': ns.get('alias_config', []),
        'startupcode': ns.get('startupcode', ''),
        'extended': ns.get('extended', {}),
        'filename': filepath,
    }
    if info['group'] not in SETUP_GROUPS:
        logger.warning('Setup %s has an invalid group (valid groups '
                       'are: %s)' % (modname, ', '.join(SETUP_GROUPS)))
        info['group'] = 'optional'
    if modname in infodict:
        # setup already exists; override/extend with new values
        oldinfo = infodict[modname] or {}
        oldinfo['description'] = ns.get('description',
                                        oldinfo['description'])
        oldinfo['group'] = ns.get('group', oldinfo['group'])
        oldinfo['sysconfig'].update(info['sysconfig'])
        oldinfo['includes'].extend(info['includes'])
        oldinfo['excludes'].extend(info['excludes'])
        oldinfo['modules'].extend(info['modules'])
        oldinfo['devices'].update(info['devices'])
        # remove devices overridden by "None" entries completely
        for devname, value in listitems(oldinfo['devices']):
            if value is None:
                del oldinfo['devices'][devname]
        oldinfo['startupcode'] += '\n' + info['startupcode']
        oldinfo['alias_config'].extend(info['alias_config'])
        oldinfo['extended'].update(info['extended'])
        oldinfo['filename'] = filepath
        logger.debug('%r setup partially merged with version '
                     'from parent directory' % modname)
    else:
        infodict[modname] = info
