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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""
Global configuration for the NICOS system.
"""

import importlib
import os
import sys
from os import path
from re import compile as regexcompile, escape as regexescape

import toml


class config:
    """Singleton for settings potentially overwritten later."""

    _applied = False  # make only one call to apply

    instrument = None

    user = None
    group = None
    umask = None  # as a string!

    nicos_root = path.normpath(path.dirname(path.dirname(__file__)))

    setup_package = None  # the root package to find setups in
    setup_subdirs = []  # setup groups to be used, as a list
    pid_path = 'pid'
    logging_path = 'log'
    systemd_props = []  # additional systemd Service properties

    sandbox_simulation = False
    sandbox_simulation_debug = False
    services = ['cache', 'poller']
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

        # Apply environment variables.
        for key, value in environment.items():
            env_re = regexcompile(r'(?<![$])[$]' + regexescape(key))
            if key == 'PYTHONPATH':
                # needs to be special-cased
                # We only need to set the additions here
                for comp in env_re.sub('', value).split(':'):
                    if comp:
                        sys.path.insert(0, comp)
            oldvalue = os.environ.get(key, '')
            value = env_re.sub(oldvalue, value)
            os.environ[key] = value

        # Set a default setup_subdirs
        if not cls.setup_subdirs:
            cls.setup_subdirs = [cls.instrument]

        cls._applied = True


def findSetupPackageAndInstrument(nicos_root, global_cfg):
    """Get the setup package and instrument of the NICOS install.

    The setup package and instrument can be specified by:

    * environment variable INSTRUMENT
    * setup_package and instrument in main `nicos.conf`

    Default is `nicos_demo, None`.
    """

    instr = None
    if 'INSTRUMENT' in os.environ:
        if '.' in os.environ['INSTRUMENT']:
            return os.environ['INSTRUMENT'].rsplit('.', 1)
        instr = os.environ['INSTRUMENT']

    nicos_section = global_cfg.get('nicos', {})
    setup_package = nicos_section.get('setup_package', 'nicos_demo')

    # Try to find a good value for the instrument name, either from the
    # environment, from the local config,  or from the hostname.
    if instr is None:
        instr = nicos_section.get('instrument')

    return setup_package, instr


def readToml(filename):
    """Read a single TOML configuration file, or return an empty dict
    if it doesn't exist.
    """
    try:
        with open(filename, encoding='utf-8') as fp:
            return toml.load(fp)
    except OSError:
        return {}
    except toml.TomlDecodeError as err:
        raise RuntimeError(
            f'could not read NICOS config file at {filename!r},'
            f' please make sure it is valid TOML: {err}') from None


def readConfig():
    """Read the basic NICOS configuration.  This is a multistep process:

    * First, we read the "local" nicos.conf (the one in the root dir)
      and try to find out our instrument from it or the environment.
    * Then, find the instrument-specific nicos.conf and read its values.
    * Finally, go back to the "local" config and overwrite values from the
      instrument-specific config with those given in the root.
    """
    # Read the local config from the standard path.
    # Get the root path of the NICOS install.
    nicos_root = config.nicos_root
    global_cfg = readToml(path.join(nicos_root, 'nicos.conf'))

    # Apply global PYTHONPATH, so that we can find the setup package in it.
    if 'PYTHONPATH' in global_cfg.get('environment', {}):
        sys.path[:0] = global_cfg['environment']['PYTHONPATH'].split(':')

    # Find setup package and its path.
    setup_package, instr = findSetupPackageAndInstrument(
        nicos_root, global_cfg)
    try:
        setup_package_mod = importlib.import_module(setup_package)
    except ImportError:
        print('Setup package %r does not exist, cannot continue.' %
              setup_package, file=sys.stderr)
        raise RuntimeError(
            'Setup package %r does not exist.' % setup_package) from None
    setup_package_path = path.dirname(setup_package_mod.__file__)

    if instr is None and hasattr(setup_package_mod, 'determine_instrument'):
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
    instr_cfg = readToml(
        path.join(setup_package_path, *instr.split('.'), 'nicos.conf'))

    # Now read the whole configuration from both locations, where the
    # local config overrides the instrument specific config.
    values = {}
    environment = {}
    for cfg in (instr_cfg, global_cfg):
        values.update(cfg.get('nicos', {}))
        environment.update(cfg.get('environment', {}))
    values.update({'instrument': instr})

    values['nicos_root'] = nicos_root
    values['setup_package'] = setup_package
    values['setup_package_path'] = setup_package_path
    return values, environment
