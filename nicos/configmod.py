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
Global configuration for the NICOS system.
"""

from __future__ import print_function

import os
import sys
import glob
import socket
from os import path

from nicos.pycompat import configparser


class config(object):
    """Singleton for settings potentially overwritten later."""
    instrument = None

    user = None
    group = None
    umask = None

    nicos_root = path.normpath(path.dirname(path.dirname(__file__)))

    custom_path = None    # the path to find custom subdirs
    setup_subdirs = None  # groups to be used like 'panda,frm2'
    pid_path = 'pid'
    logging_path = 'log'

    simple_mode = False
    services = 'cache,poller'


# read nicos.conf files

class NicosConfigParser(configparser.SafeConfigParser):
    def optionxform(self, key):
        return key

def findValidCustomPath(nicos_root, global_cfg):
    """Get the custom dir path of the NICOS install.

    The custom dirs can be specified by:
    * environment variable NICOS_CUSTOM_DIR
    * custom_paths in main `nicos.conf` (here a :-separated list is accepted,
      the first existing dir wins).

    Default is custom in nicos_root.
    """
    custom_path = None
    if 'NICOS_CUSTOM' in os.environ:
        cdir = os.environ['NICOS_CUSTOM']
        if not path.isabs(cdir):
            cdir = path.join(nicos_root, cdir)
        if path.isdir(cdir):
            custom_path = cdir

    if custom_path is None and global_cfg.has_option('nicos', 'custom_paths'):
        custom_paths = global_cfg.get('nicos', 'custom_paths')
        for cdir in custom_paths.split(':'):
            if not path.isabs(cdir):
                cdir = path.join(nicos_root, cdir)
            if path.isdir(cdir):
                # use first existing custom dir from list
                custom_path = cdir
                break

    if custom_path is None:
        #print('The specified custom path does not exist, falling back '
        #      'to built-in!', file=sys.stderr)
        custom_path = path.abspath(path.join(nicos_root, 'custom'))

    return custom_path

def readConfig():
    """Read the basic NICOS configuration.  This is a multi-step process:

    * First, we read the "local" nicos.conf (the one in the root dir)
      and try to find out our instrument from it or the environment.
    * Then, find the instrument-specific nicos.conf and read its values.
    * Finally, go back to the "local" config and overwrite values from the
      instrument-specific config with those given in the root.
    """
    # Read the local config from the standard path.
    # Get the root path of the NICOS install.
    nicos_root = config.nicos_root
    global_cfg = NicosConfigParser()
    global_cfg.read(path.join(nicos_root, 'nicos.conf'))

    custom_path = findValidCustomPath(nicos_root, global_cfg)

    # Try to find a good value for the instrument name, either from the
    # environment, from the local config,  or from the hostname.
    instr = None
    if 'INSTRUMENT' in os.environ:
        instr = os.environ['INSTRUMENT']
    elif global_cfg.has_option('nicos', 'instrument'):
        instr = global_cfg.get('nicos', 'instrument')
    else:
        try:
            # Take the middle part of the domain name (machine.instrument.frm2)
            domain = socket.getfqdn().split('.')[1]
        except (ValueError, IndexError, socket.error):
            pass
        else:
            # ... but only if a customization exists for it
            if path.isdir(path.join(custom_path, domain)):
                instr = domain
    if instr is None:
        instr = 'demo'
        print('No instrument configured or detected, using "%s" instrument.' %
              instr, file=sys.stderr)

    # Now read the instrument-specific nicos.conf.
    instr_cfg = NicosConfigParser()
    instr_cfg.read(path.join(custom_path, instr, 'nicos.conf'))

    # Now read the whole configuration from both locations, where the
    # local config overrides the instrument specific config.
    values = {'instrument': instr}
    environment = {}
    for cfg in (instr_cfg, global_cfg):
        # Get nicos config values.
        if cfg.has_section('nicos'):
            for option in cfg.options('nicos'):
                values[option] = cfg.get('nicos', option)
        # Get environment variables.
        if cfg.has_section('environment'):
            for name in cfg.options('environment'):
                environment[name] = cfg.get('environment', name)

    values['nicos_root'] = nicos_root
    values['custom_path'] = custom_path
    return values, environment


def applyConfig():
    """Read and then apply the NICOS configuration."""
    values, environment = readConfig()

    # Apply session configuration values.
    for key, value in values.items():
        setattr(config, key, value)

    # Apply environment variables.
    for key, value in environment.items():
        if key == 'PYTHONPATH':
            # needs to be special-cased
            sys.path[:0] = value.split(':')
        else:
            os.environ[key] = value

    # Set a default setup_subdirs
    if config.setup_subdirs is None:
        config.setup_subdirs = config.instrument

    # Set up PYTHONPATH for Taco libraries.
    try:
        tacobase = os.environ['DSHOME']
    except KeyError:
        tacobase = '/opt/taco'
    sys.path.extend(glob.glob(tacobase + '/lib*/python%d.*/site-packages'
                              % sys.version_info[0]))

applyConfig()
