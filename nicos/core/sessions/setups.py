#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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

"""Setup file handling."""

from __future__ import absolute_import, division, print_function

from nicos.core.params import nicosdev_re
from nicos.pycompat import exec_, iteritems, listitems
from nicos.utils import Device
from nicos.utils.files import iterSetups

SETUP_GROUPS = {
    'basic', 'optional', 'plugplay', 'lowlevel', 'special', 'configdata'
}


class MonitorElement(object):
    pass


class HasChildren(object):

    def __init__(self, *children):
        self._children = children

    def __iter__(self):
        return iter(self._children)

    def __len__(self):
        return len(self._children)

    def __getitem__(self, index):
        return self._children[index]

    def __repr__(self):
        return '%s<%r>' % (self.__class__.__name__, self._children)


class Row(HasChildren, MonitorElement):
    pass


class Column(HasChildren, MonitorElement):

    def __add__(self, other):
        if isinstance(other, tuple):
            return Column(*(self._children + other))
        elif isinstance(other, Column):
            return Column(*(self._children + other._children))
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, tuple):
            return Column(*(other + self._children))
        elif isinstance(other, Column):
            return Column(*(other._children + self._children))
        return NotImplemented


class Block(HasChildren, MonitorElement):

    def __init__(self, title, children, **options):
        self._title = title
        HasChildren.__init__(self, *children)
        self._options = options

    def __repr__(self):
        return 'Block<%r, %r, %r>' % (self._title, self._children,
                                      self._options)


class Field(MonitorElement):
    def __init__(self, **options):
        self._options = options

    def __contains__(self, key):
        return key in self._options

    def __len__(self):
        return len(self._options)

    def __iter__(self):
        return iter(self._options)

    def __getitem__(self, key):
        return self._options.get(key)

    def __setitem__(self, key, value):
        self._options.__setitem__(key, value)

    def get(self, key, default=None):
        return self._options.get(key, default)

    def pop(self, key):
        return self._options.pop(key)

    def __repr__(self):
        return 'Field<%r>' % self._options


class SetupBlock(MonitorElement):
    def __init__(self, setupname, blockname='default'):
        self._setupname = setupname
        self._blockname = blockname

    def __repr__(self):
        return 'SetupBlock<%s:%s>' % (self._setupname, self._blockname)


def readSetups(paths, logger):
    """Read all setups on the given paths."""
    infodict = {}
    all_setups = dict(iterSetups(paths))
    for (setupname, filename) in all_setups.items():
        readSetup(infodict, setupname, filename, all_setups, logger)
    # check if all includes exist
    for name, info in iteritems(infodict):
        if info is None:
            continue  # erroneous setup
        for include in info['includes']:
            if not infodict.get(include):
                logger.error('Setup "%s" includes setup "%s" which does not '
                             'exist or has errors', name, include)
                infodict[name] = None
    return infodict


def prepareNamespace(setupname, filepath, all_setups):
    """Return a namespace prepared for reading setup "setupname"."""
    # set of all files consulted via configdata()
    dep_files = set()
    # device() is a helper function to make configuration prettier
    ns = {
        'device': lambda cls, **params: Device((cls, params)),
        'configdata': make_configdata(filepath, all_setups, dep_files),
        'setupname': setupname,
        '_dep_files': dep_files,
        'Row': Row, 'Column': Column, 'BlockRow': Row,
        'Block': Block, 'Field': Field, 'SetupBlock': SetupBlock,
    }
    return ns


def make_configdata(filepath, all_setups, dep_files):
    """Create a configdata() function for use in setups."""
    def configdata(name):
        from nicos.core.errors import ConfigurationError
        try:
            setupname, element = name.split('.')
        except ValueError:
            raise ConfigurationError('configdata() argument must be in the '
                                     'form \'module.valuename\'')
        if setupname not in all_setups:
            raise ConfigurationError('config setup "%s" not found' % setupname)
        else:
            fullname = all_setups[setupname]
        ns = {}
        with open(fullname) as fp:
            exec_(fp.read(), ns)
        dep_files.add(fullname)
        try:
            return ns[element]
        except KeyError:
            raise ConfigurationError('value named %s not found in config '
                                     'setup "%s"' % (element, setupname))
    return configdata


def fixup_stacked_devices(logger, devdict):
    """
    Replace <adevname> = Device(..) entries in devices dict with a proper
    name and move the device definition under that name.
    """
    def add_new_dev(devname, subname, devconfig):
        # guess a name:
        newname = '%s_%s' % (devname, subname)
        while newname in devdict:
            logger.error('Device %r already exists, but is also a '
                         'subdevice of %r which should be renamed',
                         newname, devname)
            newname = '_' + newname
        # set subDevice lowlevel if not specified otherwise
        if 'lowlevel' not in devconfig[1]:
            devconfig[1]['lowlevel'] = True
        # 'rename' device, keeping logical connection
        devdict[newname] = devconfig
        return newname

    patched = True
    while patched:
        patched = False
        # iter over all devices
        for devname, dev in listitems(devdict):
            # iter over all key=value pairs for dict
            for subname, config in listitems(dev[1]):
                if isinstance(config, Device):  # need to fixup!
                    newname = add_new_dev(devname, subname, config)
                    dev[1][subname] = newname
                    patched = True
                elif isinstance(config, (tuple, list)) and \
                        any(isinstance(e, Device) for e in config):
                    dev[1][subname] = list(config)
                    for idx, item in enumerate(config):
                        if isinstance(item, Device):
                            subentryname = '%s%d' % (subname, idx + 1)
                            newname = add_new_dev(devname, subentryname, item)
                            dev[1][subname][idx] = newname
                            patched = True
    return devdict


def readSetup(infodict, modname, filepath, all_setups, logger):
    try:
        with open(filepath, 'rb') as modfile:
            code = modfile.read()
    except IOError as err:
        logger.exception('Could not read setup '
                         'module %r: %s', filepath, err)
        return
    ns = prepareNamespace(modname, filepath, all_setups)
    try:
        exec_(code, ns)
    except Exception as err:
        logger.exception('An error occurred while processing '
                         'setup %r: %s', filepath, err)
        return
    devices = fixup_stacked_devices(logger, ns.get('devices', {}))
    for devname in devices:
        if not nicosdev_re.match(devname):
            logger.exception('While processing setup %r: device name %r is '
                             'invalid, names must be Python identifiers',
                             filepath, devname)
            return
    info = {
        'description': ns.get('description', modname),
        'group': ns.get('group', 'optional'),
        'sysconfig': ns.get('sysconfig', {}),
        'includes': ns.get('includes', []),
        'excludes': ns.get('excludes', []),
        'modules': ns.get('modules', []),
        'devices': devices,
        'alias_config': ns.get('alias_config', {}),
        'startupcode': ns.get('startupcode', ''),
        'display_order': ns.get('display_order', 50),
        'extended': ns.get('extended', {}),
        'filenames': [filepath] + list(ns.get('_dep_files', ())),
        'monitor_blocks': ns.get('monitor_blocks', {}),
        'watch_conditions': ns.get('watch_conditions', []),
    }
    if info['group'] not in SETUP_GROUPS:
        logger.warning('Setup %s has an invalid group (valid groups '
                       'are: %s)', modname, ', '.join(SETUP_GROUPS))
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
        oldinfo['alias_config'].update(info['alias_config'])
        oldinfo['display_order'] = ns.get('display_order',
                                          oldinfo['display_order'])
        oldinfo['extended'].update(info['extended'])
        oldinfo['filenames'].extend(info['filenames'])
        oldinfo['monitor_blocks'].update(info['monitor_blocks'])
        oldinfo['watch_conditions'].extend(info['watch_conditions'])
        logger.debug('%r setup partially merged with version '
                     'from parent directory', modname)
    else:
        infodict[modname] = info
