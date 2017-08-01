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
from os import path
from re import compile as regexcompile, escape as regexescape

from nicos.pycompat import configparser


class config(object):
    """Singleton for settings potentially overwritten later."""

    _applied = False  # make only one call to apply

    instrument = None

    user = None
    group = None
    umask = None

    nicos_root = path.normpath(path.dirname(path.dirname(__file__)))

    setup_package = None  # the root package to find setups in
    setup_subdirs = None  # setup groups to be used like 'panda,frm2'
    pid_path = 'pid'
    logging_path = 'log'

    simple_mode = False
    sandbox_simulation = False
    services = 'cache,poller'
    keystorepaths = ['/etc/nicos/keystore', '~/.config/nicos/keystore']

    @classmethod
    def apply(cls):
        """Read and then apply the NICOS configuration."""
        if cls._applied:
            return

        values, environment = readConfig()

        # Apply session configuration values.
        for key, value in values.items():
            setattr(cls, key, value)

        def to_bool(val):
            if not isinstance(val, bool):
                return val.lower() in ('yes', 'true', 'on')
            return val

        # Type-coerce booleans.
        cls.simple_mode = to_bool(cls.simple_mode)
        cls.sandbox_simulation = to_bool(cls.sandbox_simulation)

        # Apply environment variables.
        for key, value in environment.items():
            env_re = regexcompile(r'(?<![$])[$]' + regexescape(key))
            if key == 'PYTHONPATH':
                # needs to be special-cased
                # We only need to set the additions here
                for comp in env_re.sub('', value).split(':'):
                    if comp:
                        sys.path.insert(0, comp)
            oldvalue = os.environ.get(key, "")
            value = env_re.sub(oldvalue, value)
            os.environ[key] = value

        # Set a default setup_subdirs
        if cls.setup_subdirs is None:
            cls.setup_subdirs = cls.instrument

        # Set up PYTHONPATH for Taco libraries.
        try:
            tacobase = os.environ['DSHOME']
        except KeyError:
            tacobase = '/opt/taco'
        sys.path.extend(glob.glob(tacobase + '/lib*/python%d.*/site-packages'
                                  % sys.version_info[0]))

        cls._applied = True


# read nicos.conf files

class NicosConfigParser(configparser.SafeConfigParser):
    def optionxform(self, key):
        return key


def findSetupPackage(nicos_root, global_cfg):
    """Get the setup package of the NICOS install.

    The package can be specified by:

    * environment variable NICOS_SETUP_PACKAGE
    * setup_package in main `nicos.conf`

    Default is `nicos_demo`.
    """
    setup_package = None

    if 'INSTRUMENT' in os.environ:
        if '.' in os.environ['INSTRUMENT']:
            setup_package = os.environ['INSTRUMENT'].split('.')[0]

    if setup_package is None and \
       global_cfg.has_option('nicos', 'setup_package'):
        setup_package = global_cfg.get('nicos', 'setup_package')

    if setup_package is None:
        setup_package = 'nicos_demo'

    return setup_package


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

    # Apply global PYTHONPATH, so that we can find the setup package in it.
    if global_cfg.has_option('environment', 'PYTHONPATH'):
        pypath = global_cfg.get('environment', 'PYTHONPATH')
        sys.path[:0] = pypath.split(':')

    # Find setup package and its path.
    setup_package = findSetupPackage(nicos_root, global_cfg)
    try:
        setup_package_mod = __import__(setup_package)
    except ImportError:
        print('Setup package %r does not exist, cannot continue.' %
              setup_package, file=sys.stderr)
        raise RuntimeError('Setup package %r does not exist.' % setup_package)
    setup_package_path = path.dirname(setup_package_mod.__file__)

    # Try to find a good value for the instrument name, either from the
    # environment, from the local config,  or from the hostname.
    instr = None
    if 'INSTRUMENT' in os.environ:
        instr = os.environ['INSTRUMENT']
        if '.' in instr:
            instr = instr.split('.')[1]
    elif global_cfg.has_option('nicos', 'instrument'):
        instr = global_cfg.get('nicos', 'instrument')
    elif hasattr(setup_package_mod, 'determine_instrument'):
        # Let the setup package have a try.
        instr = setup_package_mod.determine_instrument(setup_package_path)

    # No luck: let the user know.  This cannot happen if setup_package is
    # not set, because the default is nicos_demo, which always finds the
    # demo instrument.
    if instr is None:
        print('No instrument configured or detected (setup package is %r), '
              'cannot continue.' % setup_package, file=sys.stderr)
        print('Please either set INSTRUMENT="setup_package.instrument" in the '
              'environment, or set the "instrument" key in nicos.conf.',
              file=sys.stderr)
        raise RuntimeError('No instrument configured or detected.')

    # Now read the instrument-specific nicos.conf.
    instr_cfg = NicosConfigParser()
    instr_cfg.read(path.join(setup_package_path, instr, 'nicos.conf'))

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
    values['setup_package'] = setup_package
    values['setup_package_path'] = setup_package_path
    return values, environment
