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
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

"""
Contains the NICOS session classes, which contain all low-level global state of
the NICOS runtime.

Only for internal usage by functions and methods.
"""

import os
import sys
import copy
import stat
import inspect
import logging
from os import path
from time import sleep, time as currenttime

import numpy

from nicos import config, nicos_version, get_custom_version
from nicos.core.acquire import stop_acquire_thread
from nicos.core.spm import SPMHandler
from nicos.core.data import DataSink, DataManager
from nicos.core.device import Device, DeviceAlias, DeviceMeta
from nicos.core.errors import NicosError, UsageError, ModeError, \
    ConfigurationError, AccessError, CacheError
from nicos.core.utils import system_user
from nicos.devices.notifiers import Notifier
from nicos.utils import formatDocstring, formatScriptError, which
from nicos.utils.loggers import initLoggers, NicosLogger, \
    ColoredConsoleHandler, NicosLogfileHandler
from nicos.devices.instrument import Instrument
from nicos.devices.cacheclient import CacheClient, CacheLockError, \
    SyncCacheClient
from nicos.protocols.cache import FLAG_NO_STORE
from nicos.core.sessions.utils import makeSessionId, sessionInfo, \
    NicosNamespace, SimClock, AttributeRaiser, EXECUTIONMODES, MASTER, SLAVE, \
    SIMULATION, MAINTENANCE, guessCorrectCommand
from nicos.core.sessions.setups import readSetups
from nicos.pycompat import builtins, exec_, string_types, itervalues, \
    iteritems, listvalues, getargspec
from nicos.core.constants import MAIN


class Session(object):
    """The Session class provides all low-level routines needed for NICOS
    operations and keeps the global state: devices, configuration, loggers.

    Within one NICOS process, there is only one singleton session object that
    is always importable using ::

        from nicos import session

    There are several specialized subclasses of `Session`; one of them will
    always be used in concrete applications.
    """

    autocreate_devices = True

    log = None
    name = 'session'
    cache_class = CacheClient
    sessiontype = MAIN
    has_datamanager = False

    def __str__(self):
        # used for cache operations
        return 'session'

    def __init__(self, appname, daemonized=False):
        # first, read the config if not done already
        config.apply()

        self.appname = appname
        # create a unique session id
        self.sessionid = makeSessionId()
        # contains all created device objects
        self.devices = {}
        # maps lower-cased device names to actual-cased device names
        self.device_case_map = {}
        # contains the name of all explicitly created devices
        self.explicit_devices = set()
        # contains the configuration for all configured devices
        self.configured_devices = {}
        # contains the name of all loaded modules with user commands
        self.user_modules = set()
        # contains all loaded setups
        self.loaded_setups = set()
        # contains all setups excluded from the currently loaded
        self.excluded_setups = set()
        # contains all explicitly loaded setups
        self.explicit_setups = []
        # current "sysconfig" dictionary resulting from setup files
        self.current_sysconfig = {}
        # current "alias preferences" config
        self.alias_config = {}
        # paths to setup files
        self._setup_paths = [path.join(config.setup_package_path, p.strip(), 'setups')
                             for p in config.setup_subdirs.split(',')]
        # devices failed and succeeded to create in the current setup process
        self._failed_devices = None
        self._success_devices = None
        self._multi_level = 0
        # info about all loadable setups
        self._setup_info = {}
        # namespace to place user-accessible items in
        self.namespace = NicosNamespace()
        # contains all NICOS-exported names
        self._exported_names = set()
        # action stack for status line
        self._actionStack = []
        # execution mode; initially always slave
        self._mode = SLAVE
        # simulation clock
        self.clock = SimClock()
        # traceback of last unhandled exception
        self._lastUnhandled = None
        # SPM mode or not?
        self._spmode = False
        self._spmhandler = SPMHandler(self)
        self.setSPMode(config.simple_mode)
        # plug&play info cache
        self._pnp_cache = {'descriptions': {}}
        # intrinsic request to influence the countloop
        self.countloop_request = None
        # when was the last script started?
        self._script_start = None
        self._script_name = ''
        self._script_text = ''
        # will be filled with the path to the sandbox helper if necessary
        self._sandbox_helper = None

        # cache connection
        self.cache = None
        # data manager
        self.data = DataManager() if self.has_datamanager else None
        # acquire thread, needed for live()
        self._thd_acquire = None
        # sysconfig devices
        self._instrument = None
        self._experiment = None
        self._datasinks = None
        self._notifiers = None

        # set up logging interface
        self._initLogging(console=not daemonized)

        # set up initial namespace
        self.initNamespace()

    def initNamespace(self):
        # add some useful mathematical functions
        for name in [
                'pi', 'sqrt', 'sin', 'cos', 'tan', 'arcsin', 'arccos',
                'arctan', 'exp', 'log', 'radians', 'degrees', 'ceil', 'floor']:
            self.namespace[name] = getattr(numpy, name)
        self.namespace['numpy'] = numpy
        # remove interactive Python interpreter stuff
        for name in ['credits', 'copyright', 'license', 'exit', 'quit']:
            builtins.__dict__.pop(name, None)

    @property
    def mode(self):
        """The current :term:`execution mode` of the session."""
        return self._mode

    def setMode(self, mode):
        """Set a new mode for the session.

        This raises `.ModeError` if the new mode cannot be switched to at the
        moment (for example, if switching to master mode, but another master is
        already active).
        """
        mode = mode.lower()
        oldmode = self._mode
        cache = self.cache
        if mode == oldmode:
            return
        if mode not in EXECUTIONMODES:
            raise UsageError('mode %r does not exist' % mode)
        if oldmode in [SIMULATION, MAINTENANCE]:
            # no way to switch back from special modes
            raise ModeError('switching from %s mode is not supported' %
                            oldmode)
        if mode == MASTER:
            # switching from slave to master
            if not cache:
                self.log.info('no cache present, switching to master anyway')
                # raise ModeError('no cache present, cannot get master lock')
            else:
                self.log.info('checking master status...')
                try:
                    cache.lock('master', cache._mastertimeout)
                except CacheLockError as err:
                    raise ModeError('another master is already active: %s' %
                                    sessionInfo(err.locked_by))
                else:
                    cache._ismaster = True
                # put version info into cache
                cache.put(self, 'nicosroot', config.nicos_root)
                cache.put(self, 'custompath', config.setup_package_path)
                cache.put(self, 'nicosversion', nicos_version)
                cache.put(self, 'customversion', get_custom_version())
                if set(self.explicit_setups) - set(['system', 'startup']):
                    cache.put(self, 'mastersetup', list(self.loaded_setups))
                    cache.put(self, 'mastersetupexplicit',
                              list(self.explicit_setups))
                    self.elogEvent('setup', list(self.explicit_setups))
        else:
            # switching from master (or slave) to slave or to maintenance
            if cache and cache._ismaster:
                cache._ismaster = False
                try:
                    cache._unlock_master()
                except CacheError:
                    self.log.warning('could not release master lock')
            elif mode == MAINTENANCE:
                self.log.warning('Switching from slave to maintenance mode: '
                                 "I'll trust that you know what you're doing!")
        # stop previous inner_count / acquisition thread if available
        stop_acquire_thread()

        self._mode = mode
        if self._master_handler:
            self._master_handler.enable(mode == MASTER)
        # switch mode, taking care to switch "higher level" devices before
        # "lower level" (because higher level devices may need attached devices
        # still working in order to read out their last value)
        devs = listvalues(self.devices)
        switched = set()
        while devs:
            for dev in devs[:]:
                if dev._sdevs <= switched:
                    switched.add(dev.name)
                    dev._setMode(mode)
                    devs.remove(dev)
        if mode == SIMULATION:
            if cache:
                cache.doShutdown()
                self.cache = None
            # reset certain global state
            self._manualscan = None
            self._currentscan = None
        self.log.info('switched to %s mode', mode)

    def setSPMode(self, on):
        """Switch simple parameter mode on or off."""
        self._spmode = on

    @property
    def spMode(self):
        return self._spmode

    def simulationSync(self, db=None):
        """Synchronize device values and parameters from current cached values.
        """
        if self._mode != SIMULATION:
            raise NicosError('must be in simulation mode')
        if not self.current_sysconfig.get('cache'):
            raise NicosError('no cache is configured')
        if db is None:
            client = SyncCacheClient('Syncer',
                                     cache=self.current_sysconfig['cache'],
                                     prefix='nicos/', lowlevel=True)
            try:
                db = client.get_values()
            finally:
                client.doShutdown()
        setups = db.get('session/mastersetupexplicit')
        if setups is not None and set(setups) != set(self.explicit_setups):
            self.unloadSetup()
            self.loadSetup(setups)
        # set alias parameter first, needed to set parameters on alias devices
        for devname, dev in iteritems(self.devices):
            aliaskey = '%s/alias' % devname.lower()
            if isinstance(dev, DeviceAlias) and aliaskey in db:
                dev.alias = db[aliaskey]
        # cache keys are always lowercase, while device names can be mixed,
        # so we build a map once to get fast lookup
        lowerdevs = dict((d.name.lower(), d) for d in itervalues(self.devices))
        umethods_to_call = []
        for key, value in iteritems(db):
            if key.count('/') != 1:
                continue
            dev, param = key.split('/')
            if dev not in lowerdevs:
                continue
            dev = lowerdevs[dev]
            if param == 'value':
                # getting/setting attributes on dangling aliases raises,
                # so don't try it
                if isinstance(dev, DeviceAlias) and not dev.alias:
                    continue
                dev._sim_value = value
                dev._sim_min = dev._sim_max = dev._sim_old_value = None
                if hasattr(dev, 'doUpdateValue'):
                    umethods_to_call.append((dev.doUpdateValue, value))
            # "status" is ignored: simulated devices are always "OK"
            elif param == 'name':
                # "name" is not necessary and leads to mixups with aliases
                continue
            elif param in dev.parameters:
                if dev.parameters[param].no_sim_restore:
                    continue
                dev._params[param] = value
                if isinstance(dev, DeviceAlias) and not dev.alias:
                    continue
                umethod = getattr(dev, 'doUpdate' + param.title(), None)
                if umethod:
                    umethods_to_call.append((umethod, value))
        for umethod, value in umethods_to_call:
            umethod(value)
        self.log.info('synchronization complete')

    @property
    def instrument(self):
        """Return the current instrument device."""
        if self._instrument is not None:
            return self._instrument
        if self.checkParallel():
            return None
        configured = self.current_sysconfig.get('instrument')
        if not configured:
            return AttributeRaiser(ConfigurationError,
                                   'You have not configured an instrument '
                                   'device in your sysconfig dictionary; this '
                                   'action cannot be completed.')
        self._instrument = self._createSysconfig('instrument')
        return self._instrument

    @property
    def experiment(self):
        """Return the current experiment device."""
        if self._experiment is not None:
            return self._experiment
        if self.checkParallel():
            return None
        configured = self.current_sysconfig.get('experiment')
        if not configured:
            return AttributeRaiser(ConfigurationError,
                                   'You have not configured an experiment '
                                   'device in your sysconfig dictionary; this '
                                   'action cannot be completed.')
        self._experiment = self._createSysconfig('experiment')
        return self._experiment

    @property
    def datasinks(self):
        """Return the list of configured data sinks."""
        if self._datasinks is not None:
            return self._datasinks
        if self.checkParallel():
            return []
        if not self.current_sysconfig.get('datasinks'):
            return []
        self._datasinks = self._createSysconfig('datasinks')
        return self._datasinks

    @property
    def notifiers(self):
        """Return the list of configured notifiers."""
        if self._notifiers is not None:
            return self._notifiers
        if self.checkParallel():
            return []
        if not self.current_sysconfig.get('notifiers'):
            return []
        self._notifiers = self._createSysconfig('notifiers')
        return self._notifiers

    def _createSysconfig(self, key):
        cls, is_list = {'instrument': (Instrument, False),
                        'experiment': (Experiment, False),
                        'datasinks':  (DataSink, True),
                        'notifiers':  (Notifier, True)}[key]
        configured = self.current_sysconfig[key]
        if not is_list:
            try:
                return self.getDevice(configured, cls)
            except Exception:
                self.log.exception('%s device %r failed to create',
                                   key, configured)
                raise
        else:
            devs = []
            for devname in configured:
                try:
                    dev = self.getDevice(devname, cls)
                except Exception:
                    self.log.exception('%s device %r failed to create',
                                       key, devname)
                    raise
                else:
                    devs.append(dev)
            return devs

    def setSetupPath(self, *paths):
        """Set the paths to the setup files.

        Normally, the setup paths are given in nicos.conf and do not need to be
        set explicitly.
        """
        self._setup_paths = paths
        self.readSetups()

    def getSetupPath(self):
        """Return the current list of setup paths."""
        return list(self._setup_paths)

    def readSetupInfo(self):
        """Read information of all existing setups, and validate them.

        Setup modules are looked for in subdirectories of the configured
        "setup_package".
        """
        return readSetups(self._setup_paths, self.log)

    def getSetupInfo(self):
        """Return information about all existing setups.

        This is a dictionary mapping setup name to another dictionary.  The
        keys of that dictionary are those present in the setup files:
        'description', 'group', 'sysconfig', 'includes', 'excludes', 'modules',
        'devices', 'alias_config', 'startupcode', 'display_order', 'extended'.

        If a setup file could not be read or parsed, the value for that key is
        ``None``.
        """
        return self._setup_info.copy()

    def readSetups(self):
        """Refresh the session's setup info."""
        self._setup_info = self.readSetupInfo()

    def _nicos_import(self, modname, member='*'):
        mod = __import__(modname, None, None, [member])
        if member == '*':
            return mod
        return getattr(mod, member)

    def loadSetup(self, setupnames, allow_special=False, raise_failed=False,
                  autocreate_devices=None, autoload_system=True,
                  allow_startupcode=True, update_aliases=True):
        """Load one or more setup modules given in *setupnames* and set up
        devices accordingly.

        If *allow_special* is true, special setups (with group "special") are
        allowed, otherwise `.ConfigurationError` is raised.  If *raise_failed*
        is true, errors when creating devices are re-raised (otherwise, they
        are reported as warnings).
        """
        if not self._setup_info:
            self.readSetups()

        if isinstance(setupnames, string_types):
            setupnames = [setupnames]
        else:
            setupnames = list(setupnames)

        for setupname in setupnames[:]:
            if setupname in self.loaded_setups:
                self.log.warning('setup %s is already loaded, use '
                                 'NewSetup() without arguments to reload',
                                 setupname)
                setupnames.remove(setupname)
            elif self._setup_info.get(setupname, Ellipsis) is None:
                raise ConfigurationError(
                    'Setup %s exists, but could not be read (see above); '
                    'please fix the file and try again'
                    % setupname)
            elif setupname not in self._setup_info:
                raise ConfigurationError(
                    'Setup %s does not exist (setup paths are %s)' %
                    (setupname,
                     ', '.join(path.normpath(p) for p in self._setup_paths)))

        from nicos.commands import usercommandWrapper
        failed_devs = []
        prev_alias_config = copy.deepcopy(self.alias_config)

        def load_module(modname):
            if modname in self.user_modules:
                return
            self.user_modules.add(modname)
            self.log.info('importing module %s... ', modname)
            try:
                mod = self._nicos_import(modname)
            except Exception as err:
                self.log.error('Exception importing %s: %s', modname, err)
                return
            for name, command in iteritems(mod.__dict__):
                if getattr(command, 'is_usercommand', False):
                    if name.startswith('_') and command.__name__ != name:
                        # it's a usercommand, but imported under a different
                        # name to be used by another module, don't export it
                        continue
                    self.export(name, usercommandWrapper(command))
                elif getattr(command, 'is_userobject', False):
                    self.export(name, command)

        def merge_sysconfig(old, new):
            for key, value in iteritems(new):
                if key == 'datasinks':
                    if not isinstance(value, list):
                        raise ConfigurationError('sysconfig entry %s must be '
                                                 'a list' % key)
                    old.setdefault('datasinks', set()).update(value)
                elif key == 'notifiers':
                    old.setdefault('notifiers', set()).update(value)
                else:
                    old[key] = value

        def inner_load(name, sysconfig, devlist, startupcode):
            if name in self.loaded_setups:
                return
            info = self._setup_info[name]
            if info is None:
                raise ConfigurationError(
                    'Setup %s exists, but could not be read; '
                    'please fix the file and try again'
                    % setupname)
            if name not in setupnames:
                self.log.debug('loading include setup %r (%s)',
                               name, info['description'])
            if name in self.excluded_setups:
                raise ConfigurationError('Cannot load setup %r, it is '
                                         'excluded by one of the current '
                                         'setups' % name)

            if info['group'] == 'special' and not allow_special:
                raise ConfigurationError('Cannot load special setup %r' % name)
            if info['group'] == 'configdata':
                raise ConfigurationError('Cannot load data-only setup %r' %
                                         name)
            for exclude in info['excludes']:
                if exclude in self.loaded_setups:
                    raise ConfigurationError('Cannot load setup %r when setup '
                                             '%r is already loaded' %
                                             (name, exclude))

            self.loaded_setups.add(name)
            self.excluded_setups.update(info['excludes'])

            for include in info['includes']:
                inner_load(include, sysconfig, devlist, startupcode)

            for modname in info['modules']:
                load_module(modname)

            self.configured_devices.update(info['devices'])

            merge_sysconfig(sysconfig, info['sysconfig'])
            devlist.update(iteritems(info['devices']))
            startupcode.append(info['startupcode'])

            for aliasname, targets in info['alias_config'].items():
                for target, prio in targets.items():
                    self.alias_config.setdefault(aliasname,
                                                 []).append((target, prio))

        sysconfig, devlist, startupcode = self.current_sysconfig, {}, []
        load_setupnames = setupnames[:]
        if autoload_system and 'system' in self._setup_info and \
           'system' not in self.loaded_setups:
            load_setupnames.insert(0, 'system')
        for setupname in load_setupnames:
            self.log.info('loading setup %r (%s)',
                          setupname,
                          self._setup_info[setupname]['description'])
            inner_load(setupname, sysconfig, devlist, startupcode)

        # sort the preferred aliases by priority
        for aliasname in self.alias_config:
            # first element has the highest priority
            self.alias_config[aliasname].sort(key=lambda x: -x[1])

        # initialize the cache connection
        if sysconfig.get('cache') and self._mode != SIMULATION:
            reuse_cache = False
            if self.cache:
                if self.cache.cache == sysconfig['cache']:
                    reuse_cache = True
                else:
                    self.cache.shutdown()
            if not reuse_cache:
                self.cache = self.cache_class('Cache',
                                              cache=sysconfig['cache'],
                                              prefix='nicos/', lowlevel=True)
                # be notified about plug-and-play sample environment devices
                self.cache.addPrefixCallback('se/', self._pnpHandler)
                # be notified about watchdog events
                self.cache.addPrefixCallback('watchdog/',
                                             self._watchdogHandler)
                # make sure we process all initial keys
                self.cache.waitForStartup(1)

        self.storeSysInfo()

        # create all devices
        if autocreate_devices is None:
            autocreate_devices = self.autocreate_devices
        if autocreate_devices:
            self.log.debug('autocreating devices...')
            for devname, (_, devconfig) in sorted(iteritems(devlist)):
                try:
                    lowlevel = devconfig.get('lowlevel', False)
                    self.createDevice(devname, explicit=not lowlevel)
                except Exception:
                    if raise_failed:
                        raise
                    self.log.exception('device %r failed to create', devname)
                    failed_devs.append(devname)

        # validate and try to attach sysconfig devices
        self.log.debug('creating sysconfig devices...')
        if sysconfig.get('experiment') not in (None, 'Exp'):
            raise ConfigurationError('the experiment device must be named '
                                     '"Exp", please fix your system setup')
        for key in ['instrument', 'experiment', 'datasinks', 'notifiers']:
            setattr(self, '_' + key, None)
            if sysconfig.get(key) is not None:
                try:
                    setattr(self, '_' + key, self._createSysconfig(key))
                except Exception:
                    if raise_failed:
                        raise

        # set aliases according to alias_config
        if update_aliases:
            self.log.debug('applying alias config...')
            self.applyAliasConfig(self.alias_config, prev_alias_config)

        # remove now nonexisting envlist devices
        self.log.debug('scrubbing environment lists...')
        if self._experiment and self.mode == MASTER:
            self._experiment._scrubDetEnvLists()

        # execute the startup code
        if allow_startupcode:
            for code in startupcode:
                if code:
                    try:
                        self.log.debug('executing startup code: %r', code)
                        # no local_namespace here
                        exec_(code, self.namespace)
                    except Exception:
                        self.log.exception('error running startup code, '
                                           'ignoring')

        if failed_devs:
            self.log.error('the following devices could not be created:')
            self.log.error(', '.join(failed_devs))
            self.log.info("use CreateDevice('device') or CreateAllDevices() "
                          "later to retry")

        for setupname in setupnames:
            if self._setup_info[setupname]['extended'].get('dynamic_loaded'):
                continue
            self.explicit_setups.append(setupname)

        if self.mode == MASTER and self.cache:
            self.cache._ismaster = True
            self.cache.put(self, 'mastersetup', list(self.loaded_setups))
            self.cache.put(self, 'mastersetupexplicit',
                           list(self.explicit_setups))
            self.elogEvent('setup', list(self.explicit_setups))

        self.log.debug('executing setup callback...')
        self.setupCallback(list(self.loaded_setups),
                           list(self.explicit_setups))
        if setupnames:
            self.log.info('setups loaded: %s', ', '.join(setupnames))

    def unloadSetup(self):
        """Unload the current setup.

        This shuts down all created devices and clears the NICOS namespace.
        """
        # shutdown according to device dependencies
        devs = listvalues(self.devices)
        already_shutdown = set()
        # outer loop: as long as there are devices...
        while devs:
            deadlock = True
            # inner loop: ... we try to shutdown each one of them...
            for dev in devs[:]:
                # ... but only if they don't have remaining dependencies
                if dev._sdevs <= already_shutdown:
                    already_shutdown.add(dev.name)
                    self.unexport(dev.name, warn=False)
                    try:
                        dev.shutdown()
                    except Exception:
                        dev.log.warning('exception while shutting down', exc=1)
                    devs.remove(dev)
                    # This round (of outer loop) we had no deadlock, as we
                    # shutdown at least one device: remember this fact
                    deadlock = False
            # inner loop complete: if we couldn't shutdown a single device,
            # complain
            if deadlock:
                for dev in devs:
                    dev.log.error('can not unload, dependency still active!')
                raise NicosError('Deadlock detected! Session.unloadSetup '
                                 'failed on these devices: %r' % devs)

        if self.data is not None:
            self.data.reset()
        self.deviceCallback('destroy', list(already_shutdown))
        self.setupCallback([], [])
        self.devices.clear()
        self.device_case_map.clear()
        self.configured_devices.clear()
        self.explicit_devices.clear()
        for name in list(self._exported_names):
            self.unexport(name, warn=False)
        if self.cache:
            self.cache.shutdown()
        self.cache = None
        self._instrument = None
        self._experiment = None
        self._datasinks = None
        self._notifiers = None
        self.current_sysconfig.clear()
        self.alias_config.clear()
        self.loaded_setups = set()
        self.excluded_setups = set()
        self.explicit_setups = []
        self.user_modules = set()
        for handler in self._log_handlers:
            self.log.removeHandler(handler)
        self._log_handlers = []

    def shutdown(self):
        """Shut down the session: unload the setup and give up master mode."""
        if self._mode == MASTER and self.cache:
            self.cache._ismaster = False
            try:
                self.cache._unlock_master()
            except CacheError:
                self.log.warning('could not release master lock', exc=1)
        self.unloadSetup()

    def export(self, name, obj):
        """Export an object *obj* into the NICOS namespace with given *name*.
        """
        self.namespace.setForbidden(name, obj)
        self.namespace.addForbidden(name)
        self._exported_names.add(name)

    def unexport(self, name, warn=True):
        """Unexport the object with *name* from the NICOS namespace."""
        if name not in self.namespace:
            if warn:
                self.log.warning('unexport: name %r not in namespace', name)
            return
        if name not in self._exported_names:
            if warn:
                self.log.warning('unexport: name %r not exported by NICOS',
                                 name)
        self.namespace.removeForbidden(name)
        del self.namespace[name]
        self._exported_names.discard(name)

    def getExportedObjects(self):
        """Return an iterable of all objects exported to the NICOS namespace.
        """
        for name in self._exported_names:
            if name in self.namespace:
                yield name, self.namespace[name]

    def applyAliasConfig(self, new_config, prev_config):
        """Apply the desired aliases from self.alias_config."""
        for aliasname, targets in iteritems(new_config):
            if aliasname not in self.devices:
                # complain about this; setups should make sure that the device
                # exists when configuring it
                self.log.warning('alias device %s does not exist, cannot set '
                                 'its target', aliasname)
                continue
            if targets == prev_config.get(aliasname):
                self.log.debug('not changing alias for %s, selections have '
                               'not changed', aliasname)
                continue
            aliasdev = self.getDevice(aliasname)
            for target, _ in targets:
                if target in self.devices:
                    if aliasdev.alias != target:
                        try:
                            aliasdev.alias = target
                        except Exception:
                            self.log.exception('could not set %s alias',
                                               aliasdev)
                    break
            else:
                self.log.warning('none of the desired targets for alias %s '
                                 'actually exist', aliasname)

    def handleInitialSetup(self, setup, mode=SLAVE):
        """Determine which setup to load, and try to become master.

        Called by sessions during startup.
        """
        # Create the initial instrument setup.
        self.startMultiCreate()
        try:
            self.loadSetup(setup)
        finally:
            self.endMultiCreate()

        if mode == MAINTENANCE:
            self.setMode(MAINTENANCE)
        elif mode == SLAVE:
            # Try to become master if the setup didn't already switch modes.
            try:
                self.setMode(MASTER)
            except ModeError:
                self.log.info('could not enter master mode; remaining slave',
                              exc=True)
            except Exception:
                self.log.warning('could not enter master mode', exc=True)
            if setup not in ('startup', ['startup']) or not self.cache:
                return
            # If we became master, the user didn't select a specific startup
            # setup and a previous master setup was configured, re-use that.
            setups = self.cache.get(self, 'mastersetupexplicit')
            if not setups or setups == ['startup']:
                return
            self.log.info('loading previously used master setups: %s',
                          ', '.join(setups))
            self.unloadSetup()
            self.startMultiCreate()
            try:
                try:
                    self.loadSetup(setups)
                finally:
                    self.endMultiCreate()
            except NicosError:
                self.log.warning('could not load previous setups, falling '
                                 'back to startup setup', exc=1)
                self.unloadSetup()
                self.loadSetup(setup)

    def commandHandler(self, command, compiler):
        """This method is called when the user executes a simple command.  It
        should return a compiled code object that is then executed instead of
        the command.
        """
        command = command.strip()
        if command.startswith('#'):
            return compiler('LogEntry(%r)' % command[1:].strip())
        if self._spmode:
            if command.startswith('.'):
                command = command[1:]
            return compiler(self._spmhandler.handle_line(command))
        try:
            return compiler(command)
        except SyntaxError:
            # shortcut for integrated help
            if command.endswith('?') or command.startswith('?'):
                return compiler('help(%s)' % command.strip('?'))
            # shortcut for running commands in simple mode
            if command.startswith('.'):
                return compiler(self._spmhandler.handle_line(command[1:]))
            # shortcut for simulation mode
            if command.startswith(':'):
                return compiler('sim(%r)' % command[1:].rstrip())
            raise

    def scriptHandler(self, script, filename, compiler):
        """This method should be called to process/handle a script."""
        if filename.endswith('.txt') or \
                (self._spmode and not filename.endswith('.py')):
            return compiler(self._spmhandler.handle_script(script, filename))
        return compiler(script)

    def showHelp(self, obj=None):
        """Show help for the given object.

        Can be overwritten in a derived session to provide other means of
        displaying help.
        """
        if obj is None:
            from nicos.commands.basic import ListCommands
            ListCommands()
        elif isinstance(obj, Device):
            self.log.info('%s is a device of class %s.',
                          obj.name, obj.__class__.__name__)
            if obj.description:
                self.log.info('Device description: %s', obj.description)
            if obj.__class__.__doc__:
                lines = obj.__class__.__doc__.strip().splitlines()
                self.log.info('Device class description: %s', lines[0])
                for line in lines[1:]:
                    self.log.info(line)
            from nicos.commands.device import ListMethods, ListParams
            ListMethods(obj)
            ListParams(obj)
        elif not inspect.isfunction(obj):
            builtins.help(obj)
        else:
            # for functions, print arguments and docstring
            real_func = getattr(obj, 'real_func', obj)
            if hasattr(real_func, 'help_arglist'):
                argspec = '(%s)' % real_func.help_arglist
            else:
                argspec = inspect.formatargspec(*getargspec(real_func))
            self.log.info('Usage: ' + real_func.__name__ + argspec)
            for line in formatDocstring(real_func.__doc__ or '', '   '):
                self.log.info(line)

    def getExecutingUser(self):
        return system_user

    def checkUserLevel(self, level=0, user=None):
        if user is None:
            user = self.getExecutingUser()
        return user.level >= level

    # -- Device control -------------------------------------------------------

    def startMultiCreate(self):
        """Store devices that fail to create so that they are not tried again
        and again during one setup process.
        """
        if not self._multi_level:
            self._failed_devices = {}
            self._success_devices = []
        self._multi_level += 1

    def endMultiCreate(self):
        """Mark the end of a multi-create."""
        self._multi_level -= 1
        if not self._multi_level:
            self._failed_devices = None
            self.deviceCallback('create', self._success_devices)
            self._success_devices = None

    def getDevice(self, dev, cls=None, source=None, replace_classes=None):
        """Return a device *dev* from the current setup.

        If *dev* is a string, the corresponding device will be looked up or
        created, if necessary.

        *cls* gives a class, or tuple of classes, that *dev* needs to be an
        instance of.

        *replace_classes* can be used to replace configured device classes.
        If given, it is a tuple of ``(old_class, new_class, new_devconfig)``.
        """
        if isinstance(dev, string_types):
            if dev in self.devices:
                dev = self.devices[dev]
            elif dev in self.configured_devices:
                if self.checkParallel():
                    raise NicosError('cannot create devices in parallel '
                                     'threads')
                dev = self.createDevice(dev, replace_classes=replace_classes)
            else:
                dev = self._deviceNotFound(dev, source)
        if not isinstance(dev, cls or Device):
            def clsrep(cls):
                if isinstance(cls, tuple):
                    return ', '.join(clsrep(c) for c in cls)
                return cls.__name__
            if isinstance(cls, tuple):
                raise UsageError(source,
                                 'device must be one of %s' % clsrep(cls))
            raise UsageError(source,
                             'device must be a %s' % (cls or Device).__name__)
        return dev

    def _deviceNotFound(self, devname, source=None):
        """Called when a required device was not found in the currently
        configured devices.  Normally this raises ConfigurationError, but can
        be overridden in subclasses to extend behavior.
        """
        raise ConfigurationError(source, 'device %r not found in '
                                 'configuration' % devname)

    def importDevice(self, devname, replace_classes=None):
        """Try to import the device class for the device.

        The device must exist in the `configured_devices` dict.
        """
        devclsname, devconfig = self.configured_devices[devname]
        self.log.debug('importing device class %s for device %r',
                       devclsname, devname)
        modname, clsname = devclsname.rsplit('.', 1)
        try:
            devcls = self._nicos_import(modname, clsname)
        except (ImportError, AttributeError) as err:
            raise ConfigurationError('failed to import device class %r: %s'
                                     % (devclsname, err))
        if not isinstance(devcls, DeviceMeta):
            raise ConfigurationError('configured device class %r is not a '
                                     'Device or derived class' % devclsname)
        if replace_classes is not None:
            for orig_class, replace_class, class_config in replace_classes:
                if issubclass(devcls, orig_class):
                    devcls = replace_class
                    devconfig = class_config
                    break
        return devcls, devconfig

    def createDevice(self, devname, recreate=False, explicit=False,
                     replace_classes=None):
        """Create device given by a device name.

        If device exists and *recreate* is true, destroy and create it again.
        If *explicit* is true, the device is added to the list of "explicitly
        created devices".
        """
        if self._failed_devices and devname in self._failed_devices:
            raise self._failed_devices[devname]
        if devname not in self.configured_devices:
            found_in = []
            for sname, info in iteritems(self._setup_info):
                if info is None:
                    continue
                if devname in info['devices']:
                    found_in.append(sname)
            if found_in:
                raise ConfigurationError(
                    'device %r not found in configuration, but you can load '
                    'one of these setups with AddSetup to create it: %s' %
                    (devname, ', '.join(map(repr, found_in))))
            raise ConfigurationError('device %r not found in configuration'
                                     % devname)
        if devname in self.devices:
            if not recreate:
                if explicit:
                    self.explicit_devices.add(devname)
                    self.export(devname, self.devices[devname])
                return self.devices[devname]
            self.destroyDevice(devname)

        devcls, devconfig = self.importDevice(devname, replace_classes)
        if 'description' in devconfig:
            self.log.info('creating device %r (%s)... ',
                          devname, devconfig['description'])
        else:
            self.log.info('creating device %r... ', devname)

        try:
            dev = devcls(devname, **devconfig)
            self.log.debug('device %r created', devname)
        except Exception as err:
            if self._failed_devices is not None:
                self._failed_devices[devname] = err
            raise
        if self._success_devices is not None:
            self._success_devices.append(devname)
        else:
            self.deviceCallback('create', [devname])
        if explicit:
            self.explicit_devices.add(devname)
            self.export(devname, dev)
        return dev

    def destroyDevice(self, devname):
        """Shutdown a device and remove it from the list of created devices."""
        if devname not in self.devices:
            self.log.warning('device %r not created', devname)
            return
        self.log.info('shutting down device %r...', devname)
        dev = self.devices[devname]
        try:
            dev.shutdown()
        except Exception:
            dev.log.warning('exception while shutting down', exc=1)
        self.deviceCallback('destroy', [devname])
        if devname in self.namespace:
            self.unexport(devname)

    def notifyConditionally(self, runtime, subject, body, what=None,
                            short=None, important=True):
        """Send a notification if the current runtime exceeds the configured
        minimum runtimer for notifications.
        """
        if self._mode == SIMULATION:
            return
        for notifier in self.notifiers:
            notifier.sendConditionally(runtime, subject, body, what,
                                       short, important)

    def notify(self, subject, body, what=None, short=None, important=True):
        """Send a notification unconditionally."""
        if self._mode == SIMULATION:
            return
        for notifier in self.notifiers:
            notifier.send(subject, body, what, short, important)

    # -- Special cache handlers -----------------------------------------------

    def _pnpHandler(self, key, value, time, expired=False):
        if self._mode != MASTER:
            return
        parts = key.split('/')
        self.log.debug('got PNP message: key %s, value %s, expired=%s',
                       key, value, expired)
        if key.endswith('/description'):
            self._pnp_cache['descriptions'][parts[1]] = value
            return
        elif key.endswith('/nicos/setupname'):
            setupname = value
            if (setupname in self._setup_info and
                    self._setup_info[setupname] is not None and
                    self._setup_info[setupname]['group'] in ('plugplay',
                                                             'optional')):
                description = self._pnp_cache['descriptions'].get(parts[1])
                # an event is either generated if
                # - the setup is unloaded and the key was added
                if setupname not in self.loaded_setups and not expired:
                    self.pnpEvent('added', setupname, description)
                # - or the setup is loaded and the key has expired (the
                #   equipment has been removed)
                elif setupname in self.loaded_setups and expired:
                    self.pnpEvent('removed', setupname, description)

    def pnpEvent(self, event, setupname, description):
        if event == 'added':
            self.log.info('new sample environment detected: %s',
                          description or '')
            self.log.info('load setup %r to activate', setupname)
        elif event == 'removed':
            self.log.info('sample environment removed: %s', description or '')
            self.log.info('unload setup %r to clear its devices', setupname)

    def _watchdogHandler(self, key, value, time, expired=False):
        """Handle a watchdog event."""
        # value[0] is a timestamp, value[1] a string
        if key.endswith(('/warning', '/action')):
            self.watchdogEvent(key.rsplit('/')[-1], value[0], value[1])
        elif key.endswith('/pausecount'):
            if self.experiment and self.mode == MASTER:
                self.experiment.pausecount = value
                if value:
                    self.countloop_request = ('pause', value)

    def watchdogEvent(self, event, time, data):
        if event == 'warning':
            self.log.warning('WATCHDOG ALERT: %s', data)
        elif event == 'action':
            self.log.warning('Executing watchdog action: %s', data)

    # -- Logging --------------------------------------------------------------

    def _initLogging(self, prefix=None, console=True):
        prefix = prefix or self.appname
        initLoggers()
        self._loggers = {}
        self._log_handlers = []
        self.createRootLogger(prefix, console)

    def createRootLogger(self, prefix='nicos', console=True):
        self.log = NicosLogger('nicos')
        self.log.setLevel(logging.INFO)
        self.log.parent = None
        log_path = path.join(config.nicos_root, config.logging_path)
        if console:
            self.log.addHandler(ColoredConsoleHandler())
        self._master_handler = None
        try:
            if prefix == 'nicos':
                self.log.addHandler(NicosLogfileHandler(
                    log_path, 'nicos', str(os.getpid())))
                # handler for master session only
                self._master_handler = NicosLogfileHandler(log_path)
                self._master_handler.disabled = True
                self.log.addHandler(self._master_handler)
            else:
                self.log.addHandler(NicosLogfileHandler(log_path, prefix))
        except (IOError, OSError) as err:
            self.log.error('cannot open log file: %s', err)

    def getLogger(self, name):
        """Return a new NICOS logger for the specified device name."""
        if name in self._loggers:
            return self._loggers[name]
        logger = NicosLogger(name)
        logger.parent = self.log
        logger.setLevel(logging.DEBUG)
        self._loggers[name] = logger
        return logger

    def addLogHandler(self, handler):
        """Add a new logging handler to the list of handlers for all NICOS
        loggers.
        """
        self._log_handlers.append(handler)
        self.log.addHandler(handler)

    def logUnhandledException(self, exc_info=None, cut_frames=0, msg=''):
        """Log an unhandled exception (occurred during user scripts).

        The exception is logged using the originating device's logger, if that
        information is available.
        """
        if exc_info is None:
            exc_info = sys.exc_info()
        self._lastUnhandled = exc_info
        if isinstance(exc_info[1], NicosError):
            if isinstance(exc_info[1].device, Device) and \
               exc_info[1].device.log:
                exc_info[1].device.log.error(exc_info=exc_info)
                return
        if cut_frames:
            etype, evalue, tb = exc_info  # pylint: disable=W0633
            while cut_frames:
                tb = tb.tb_next
                cut_frames -= 1
            exc_info = (etype, evalue, tb)
        if msg:
            self.log.error(msg, exc_info=exc_info)
        else:
            self.log.error(exc_info=exc_info)

    def elogEvent(self, eventtype, data):
        # NOTE: simulation mode is disconnected from cache, therefore no elog
        # events will be sent in simulation mode
        if self.cache:
            self.cache.put_raw('logbook/' + eventtype + FLAG_NO_STORE, data)

    def scriptEvent(self, eventtype, data):
        """Call this when an command/script event happens.

        eventtype can be "start", "finish" or "exception".  "exception" does
        not need to mean that the script has been aborted.

        data is script text (for start), or an exc_info tuple (for exception).
        """
        if eventtype == 'start':
            # record starting time to decide whether to send notification
            self._script_start = currenttime()
            self._script_name = data[0]
            self._script_text = data[1]
        elif eventtype == 'update':
            self._script_text = data[1]
        elif eventtype == 'exception':
            self.logUnhandledException(data)
            # don't raise exceptions on exceptions
            try:
                body, short = formatScriptError(data, self._script_name,
                                                self._script_text)
                self.notifyConditionally(
                    currenttime() - self._script_start,
                    'Error in script', body, 'error notification', short)
                if isinstance(data[1], NameError):
                    guessCorrectCommand(self._script_text)
                elif isinstance(data[1], AttributeError):
                    guessCorrectCommand(self._script_text, True)
            except Exception:
                pass

    # -- Action logging -------------------------------------------------------

    def beginActionScope(self, what):
        self._actionStack.append(what)
        joined = ' :: '.join(self._actionStack)
        self.log.action(joined)
        if self.cache:
            self.cache.put('exp', 'action', joined, flag=FLAG_NO_STORE)

    def endActionScope(self):
        if not self._actionStack:
            self.log.debug('popping from empty actionStack!')
            return
        self._actionStack.pop()
        joined = ' :: '.join(self._actionStack)
        self.log.action(joined)
        if self.cache:
            self.cache.put('exp', 'action', joined, flag=FLAG_NO_STORE)

    def action(self, what):
        joined = ' :: '.join(self._actionStack + [what])
        self.log.action(joined)
        if self.cache:
            self.cache.put('exp', 'action', joined, flag=FLAG_NO_STORE)

    def clearActions(self):
        if self._actionStack:
            del self._actionStack[:]
            self.log.action('')
            if self.cache:
                self.cache.put('exp', 'action', '', flag=FLAG_NO_STORE)

    # -- Simulation support ---------------------------------------------------

    def runSimulation(self, code, uuid='0', wait=True, quiet=False):
        """Spawn a simulation of *code*.

        If *wait* is true, wait until the process is finished.
        If *quiet* is true, only results will be emitted.
        """
        if not self.cache:
            raise NicosError('cannot start dry run, no cache is configured')

        # read out last values of all devices
        for dev in self.devices.values():
            try:
                dev.read()  # cached value is okay
            except Exception:
                pass

        # check sandboxing prerequisites
        if config.sandbox_simulation and not self._sandbox_helper:
            if not sys.platform.startswith('linux'):
                raise NicosError('Dry run is configured to run sandboxed, but '
                                 'this only works on Linux')
            helperpath = which('nicos-sandbox-helper')
            if not helperpath:
                raise NicosError('Dry run is configured to run sandboxed, but '
                                 'the nicos-sandbox-helper binary was not '
                                 'found')
            st = os.stat(helperpath)
            if st.st_uid != 0 or not st.st_mode & stat.S_ISUID:
                raise NicosError('Dry run is configured to run sandboxed, but '
                                 'the nicos-sandbox-helper binary is not '
                                 'set-uid root')
            self._sandbox_helper = helperpath

        # create a thread that that start the simulation and forwards its
        # messages to the client(s)
        from nicos.core.sessions.simulation import SimulationSupervisor
        emitter = getattr(self, 'daemon_device', None)
        setups = [setup for setup in self.loaded_setups if
                  setup in self.explicit_setups or
                  self._setup_info[setup]['extended'].get('dynamic_loaded')]
        user = self.getExecutingUser()
        supervisor = SimulationSupervisor(self._sandbox_helper, uuid, code,
                                          setups, user, emitter, quiet=quiet)
        supervisor.start()
        if wait:
            supervisor.join()

    # -- Session-specific behavior --------------------------------------------

    def updateLiveData(self, tag, uid, detector, filename, dtype, nx, ny, nt,
                       time, data):
        """Send new live data to clients.

        The parameters are:

        * tag - a string describing the type of data that is sent.  It is used
          by clients to determine if they can display this data.
        * uid - a unique id for the corresponding data point.
        * detector - name of the detector device.
        * filename - the filename displayed for cached data.
        * dtype - a string describing the data array in numpy style, if it is
          in array format.
        * nx, ny, nt - three integers giving the dimensions of the data array,
          if it is in array format.
        * time - the current measurement time, for determining count rate.
        * data - the actual data as a byte string.
        """

    def notifyDataFile(self, tag, uid, detector, filename):
        """Notify clients that a new data file has been written, which might
        be viewed by live-data views.

        The parameters are:

        * tag - a string describing the type of data saved.  It is used
          by clients to determine if they can open/display this data.
        * uid - a unique id for the corresponding data point.
        * detector - name of the detector device.
        * filename - a string giving the filename of the data.
        """

    def notifyFitCurve(self, dataset, title, xvalues, yvalues):
        """Notify clients that a new fit curve has been created and should
        be displayed for the given dataset.

        The parameters are:

        * title - a string describing the fit.
        * xvalues, yvalues - lists of data points.
        """

    def breakpoint(self, level):
        """Allow breaking or stopping the script at a well-defined time.
        *level* can be:

        - 1 to indicate a breakpoint "after current scan"
        - 2 to indicate a breakpoint "after current scan point"
        - 3 to indicate a breakpoint "during counting"
        - 5 to indicate a breakpoint for "immediate stop"
        """

    def pause(self, prompt):
        """Pause the script, prompting the user to continue with a message."""

    def delay(self, secs):
        """Sleep for a small time, allow immediate stop before and after."""
        self.breakpoint(5)
        sleep(secs)
        self.breakpoint(5)

    def checkAccess(self, required):
        """Check if the current user fulfills the requirements given in the
        *required* dictionary.  Raise `.AccessError` if check failed.

        This is called by the `.requires` decorator.
        """
        if 'mode' in required:
            if self.mode != required['mode']:
                raise AccessError('requires %s mode' % required['mode'])
        return True

    def checkParallel(self):
        """Check if the current thread is running parallel to the main
        NICOS scripts.
        """
        return False

    def clientExec(self, func, args):
        """Execute a function client-side."""
        raise NotImplementedError('clientExec is missing for this session')

    def deviceCallback(self, action, devnames):
        """Callback when devices were created or shut down."""

    def setupCallback(self, setupnames, explicit):
        """Callback when setups were loaded or unloaded."""

    def experimentCallback(self, proposal, proptype):
        """Callback when the experiment has been changed."""
        # clear user-specific names
        for name in list(self.namespace):
            if name == '__builtins__':
                continue
            if name not in self._exported_names:
                del self.namespace[name]
        # but need to put back the default imports
        self.initNamespace()

    def storeSysInfo(self):
        if self.cache:
            self.cache.storeSysInfo(self.appname)


# must be imported after class definitions due to module interdependencies
from nicos.devices.experiment import Experiment
