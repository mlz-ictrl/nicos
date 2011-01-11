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

"""
Contains the NICOS class, which contains all low-level global state
of the NICOS runtime.

Only for internal usage by functions and methods.
"""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import os
import imp
import sys
import code
import signal
import logging
import readline
import rlcompleter
from os import path
from wsgiref.simple_server import make_server

from nicos import session, nicos_version
from nicos.web import WebHandler, FakeInput, NicosApp
from nicos.utils import makeSessionId, colorcode, daemonize, writePidfile, \
     removePidfile
from nicos.errors import NicosError, UsageError, ConfigurationError, ModeError
from nicos.loggers import NicosLogfileHandler, ColoredConsoleHandler, \
     initLoggers, OUTPUT, INPUT


class NicosNamespace(dict):
    """
    A dict subclass that has a list of identifiers that cannot be set, except
    using the setForbidden() method.
    """

    def __init__(self):
        self.__forbidden = set()

    def addForbidden(self, name):
        self.__forbidden.add(name)

    def removeForbidden(self, name):
        self.__forbidden.discard(name)

    def setForbidden(self, name, value):
        dict.__setitem__(self, name, value)

    def __setitem__(self, name, value):
        if name in self.__forbidden:
            raise UsageError('%s cannot be assigned to' % name)
        dict.__setitem__(self, name, value)

    def __delitem__(self, name):
        if name in self.__forbidden:
            raise UsageError('%s cannot be deleted' % name)
        dict.__delitem__(self, name)


class Session(object):
    """
    The Session class provides all low-level routines needed for NICOS
    operations and keeps the global state: devices, configuration, loggers.
    """

    auto_modules = ['nicos.commands']
    autocreate_devices = True

    class config(object):
        """Singleton for settings potentially overwritten later."""
        user = None
        group = None
        bin_path = path.join(path.dirname(__file__), '..', '..', 'bin')
        control_path = path.join(path.dirname(__file__), '..', '..')

    def __init__(self, appname):
        self.appname = appname
        # create a unique session id
        self.sessionid = makeSessionId()
        # contains all created device objects
        self.devices = {}
        # contains the name of all explicitly created devices
        self.explicit_devices = set()
        # contains the configuration for all configured devices
        self.configured_devices = {}
        # contains the name of all loaded modules with user commands
        self.user_modules = set()
        # contains all loaded setups
        self.loaded_setups = set()
        # contains all explicitly loaded setups
        self.explicit_setups = []
        # path to setup files
        self.__setup_path = path.join(self.config.control_path, 'setup')
        # info about all loadable setups
        self.__setup_info = {}
        # namespace to place user-accessible items in
        self.__namespace = NicosNamespace()
        self.__local_namespace = NicosNamespace()
        # contains all NICOS-exported names
        self.__exported_names = set()
        # cache special device
        self.__system_device = None
        # action stack for status line
        self._actionStack = []

        # set up logging interface
        self._initLogging()
        self.log = self.getLogger('nicos')

    def setNamespace(self, ns):
        """Set the namespace to export commands and devices into."""
        self.__namespace = ns
        self.__exported_names = set()

    def getNamespace(self):
        return self.__namespace

    def setSetupPath(self, path):
        """Set the path to the setup files."""
        self.__setup_path = path
        self.readSetups()

    def readSetups(self):
        """Read information of all existing setups.

        Setup modules are looked for in the setup/ directory which
        should be a sibling to this package's directory.
        """
        self.__setup_info.clear()
        for filename in os.listdir(self.__setup_path):
            if not filename.endswith('.py'):
                continue
            modname = filename[:-3]
            try:
                modfile = imp.find_module(modname, [self.__setup_path])
                code = modfile[0].read()
                modfile[0].close()
            except (ImportError, IOError), err:
                raise ConfigurationError('Could not find or read setup '
                                         'module %r: %s' % (modname, err))
            # device() is a helper function to make configuration prettier
            ns = {'device': lambda cls, **params: (cls, params)}
            try:
                exec code in ns
            except Exception, err:
                raise ConfigurationError('An error occurred while reading '
                                         'setup %s: %s' % (modname, err))
            info = {
                'name': ns.get('name', modname),
                'group': ns.get('group', 'base'),
                'includes': ns.get('includes', []),
                'modules': ns.get('modules', []),
                'devices': ns.get('devices', {}),
                'startupcode': ns.get('startupcode', ''),
            }
            self.__setup_info[modname] = info
        # check if all includes exist
        for name, info in self.__setup_info.iteritems():
            for include in info['includes']:
                if include not in self.__setup_info:
                    raise ConfigurationError('Setup %s includes setup %s which '
                                             'does not exist' % (name, include))

    def getSetupInfo(self):
        return self.__setup_info.copy()

    def loadSetup(self, setupname, allow_special=False):
        """Load a setup module and set up devices accordingly."""
        if not self.__setup_info:
            self.readSetups()

        if setupname in self.loaded_setups:
            self.log.warning('setup %s is already loaded' % setupname)
            return
        if setupname not in self.__setup_info:
            raise ConfigurationError('Setup %s does not exist (setup path is '
                                     '%s)' % (setupname, self.__setup_path))

        self.log.info('loading setup %s' % setupname)

        from nicos.commands import usercommandWrapper
        failed_devs = []

        def load_module(modname):
            if modname in self.user_modules:
                return
            self.user_modules.add(modname)
            self.log.info('importing module %s... ' % modname)
            try:
                __import__(modname)
                mod = sys.modules[modname]
            except Exception, err:
                self.log.error('Exception importing %s: %s' % (modname, err))
                return
            for name, command in mod.__dict__.iteritems():
                if getattr(command, 'is_usercommand', False):
                    self.export(name, usercommandWrapper(command))

        def inner_load(name):
            if name in self.loaded_setups:
                return
            if name != setupname:
                self.log.info('loading include setup %s' % name)

            info = self.__setup_info[name]
            if info['group'] == 'special' and not allow_special:
                raise ConfigurationError('Cannot load special setup %r' % name)

            self.loaded_setups.add(name)

            devlist = {}
            startupcode = []

            for include in info['includes']:
                ret = inner_load(include)
                if ret:
                    devlist.update(ret[0])
                    startupcode.extend(ret[1])

            for modname in info['modules']:
                load_module(modname)

            self.configured_devices.update(info['devices'])

            devlist.update(info['devices'].iteritems())
            startupcode.append(info['startupcode'])

            return devlist, startupcode

        # always load nicos.commands in interactive mode
        for modname in self.auto_modules:
            load_module(modname)

        devlist, startupcode = inner_load(setupname)

        # System must be created first
        if 'System' not in self.devices:
            if 'System' not in self.configured_devices:
                self.configured_devices['System'] = ('nicos.system.System', dict(
                    datasinks=[], cache=None, instrument=None, experiment=None,
                    notifiers=[], datapath=''))
            try:
                self.createDevice('System')
            except Exception:
                self.log.exception('error creating System device')

        # create all devices
        if self.autocreate_devices:
            for devname, (_, devconfig) in sorted(devlist.iteritems()):
                if devconfig.get('lowlevel', False):
                    continue
                try:
                    self.createDevice(devname, explicit=True)
                except Exception:
                    #raise
                    self.log.exception('failed')
                    failed_devs.append(devname)

        for code in startupcode:
            if code:
                exec code in self.__namespace

        if failed_devs:
            self.log.error('the following devices could not be created:')
            self.log.error(', '.join(failed_devs))

        self.explicit_setups.append(setupname)
        self.resetPrompt()
        self.log.info('setup loaded')

    def unloadSetup(self):
        """Unload the current setup: destroy all devices and clear the
        NICOS namespace.
        """
        # shutdown according to device dependencies
        devs = self.devices.values()
        already_shutdown = set()
        while devs:
            for dev in devs[:]:
                # shutdown only those devices that don't have remaining
                # dependencies
                if dev._sdevs <= already_shutdown:
                    already_shutdown.add(dev.name)
                    self.unexport(dev.name, warn=False)
                    dev.shutdown()
                    devs.remove(dev)
        self.devices.clear()
        self.configured_devices.clear()
        self.explicit_devices.clear()
        for name in list(self.__exported_names):
            self.unexport(name)
        self.loaded_setups = set()
        self.explicit_setups = []
        self.user_modules = set()
        # XXX remember running mode
        self.__system_device = None
        self.__exp_device = None

    def shutdown(self):
        self.unloadSetup()

    def resetPrompt(self):
        base = self.system.mode != 'master' and self.system.mode + ' ' or ''
        expsetups = '+'.join(self.explicit_setups)
        sys.ps1 = base + '(%s) >>> ' % expsetups
        sys.ps2 = base + ' %s  ... ' % (' ' * len(expsetups))

    def export(self, name, object):
        self.__namespace.setForbidden(name, object)
        self.__namespace.addForbidden(name)
        self.__local_namespace.addForbidden(name)
        self.__exported_names.add(name)

    def unexport(self, name, warn=True):
        if name not in self.__namespace:
            if warn:
                self.log.warning('unexport: name %r not in namespace' % name)
            return
        if name not in self.__exported_names:
            self.log.warning('unexport: name %r not exported by NICOS' % name)
        self.__namespace.removeForbidden(name)
        self.__local_namespace.removeForbidden(name)
        del self.__namespace[name]
        self.__exported_names.remove(name)

    def getExportedObjects(self):
        for name in self.__exported_names:
            if name in self.__namespace:
                yield self.__namespace[name]

    # -- Device control --------------------------------------------------------

    def getDevice(self, dev, cls=None):
        """Convenience: get a device by name or instance."""
        if isinstance(dev, str):
            if dev in self.devices:
                dev = self.devices[dev]
            elif dev in self.configured_devices:
                dev = self.createDevice(dev)
            else:
                raise ConfigurationError(
                    'device %r not found in configuration' % dev)
        from nicos.device import Device
        if not isinstance(dev, cls or Device):
            raise UsageError('dev must be a %s' % (cls or Device).__name__)
        return dev

    def createDevice(self, devname, recreate=False, explicit=False):
        """Create device given by a device name.

        If device exists and *recreate* is true, destroy and create it again.
        """
        if devname not in self.configured_devices:
            raise ConfigurationError('device %r not found in configuration'
                                     % devname)
        if devname in self.devices:
            if not recreate:
                if explicit:
                    self.export(devname, self.devices[devname])
                return self.devices[devname]
            self.destroyDevice(devname)
        self.log.info('creating device %r... ' % devname)
        devclsname, devconfig = self.configured_devices[devname]
        modname, clsname = devclsname.rsplit('.', 1)
        try:
            devcls = getattr(__import__(modname, None, None, [clsname]),
                             clsname)
        except (ImportError, AttributeError), err:
            raise ConfigurationError('failed to import device class %r: %s'
                                     % (devclsname, err))
        dev = devcls(devname, **devconfig)
        if explicit:
            self.explicit_devices.add(devname)
            self.export(devname, dev)
        return dev

    def destroyDevice(self, devname):
        """Shutdown and destroy a device."""
        if devname not in self.devices:
            raise UsageError('device %r not created' % devname)
        self.log.info('shutting down device %r...' % devname)
        dev = self.devices[devname]
        dev.shutdown()
        for adev in dev._adevs.values():
            if isinstance(adev, list):
                [real_adev._sdevs.discard(dev.name) for real_adev in adev]
            else:
                adev._sdevs.discard(dev.name)
        del self.devices[devname]
        self.explicit_devices.discard(devname)
        if devname in self.__namespace:
            self.unexport(devname)

    @property
    def system(self):
        if self.__system_device is None:
            from nicos.system import System
            self.__system_device = self.getDevice('System', System)
        return self.__system_device

    # -- Logging ---------------------------------------------------------------

    def _initLogging(self, prefix=None):
        prefix = prefix or self.appname
        initLoggers()
        self._loggers = {}
        self._log_manager = logging.Manager(None)
        # all interfaces should log to a logfile; more handlers can be
        # added by subclasses
        log_path = path.join(self.config.control_path, 'log')
        self._log_handlers = [
            NicosLogfileHandler(log_path, filenameprefix=prefix),
            ColoredConsoleHandler(),
        ]

    def getLogger(self, name):
        if name in self._loggers:
            return self._loggers[name]
        logger = self._log_manager.getLogger(name)
        # XXX must be configurable
        logger.setLevel(logging.DEBUG)
        for handler in self._log_handlers:
            logger.addHandler(handler)
        self._loggers[name] = logger
        return logger

    def logUnhandledException(self, exc_info=None, cut_frames=0, msg=''):
        """Log an unhandled exception.  Log using the originating device's
        logger, if that information is available.
        """
        if exc_info is None:
            exc_info = sys.exc_info()
        if isinstance(exc_info[1], NicosError):
            if exc_info[1].device and exc_info[1].device._log:
                exc_info[1].device._log.error(exc_info=exc_info)
                return
        if cut_frames:
            type, value, tb = exc_info
            while cut_frames:
                tb = tb.tb_next
                cut_frames -= 1
            exc_info = (type, value, tb)
        self.log.error(msg, exc_info=exc_info)

    # -- Action logging --------------------------------------------------------

    def beginActionScope(self, what):
        self._actionStack.append(what)
        self.log.action(' :: '.join(self._actionStack))

    def endActionScope(self):
        self._actionStack.pop()
        self.log.action(' :: '.join(self._actionStack))

    def action(self, what):
        self.log.action(' :: '.join(self._actionStack + [what]))


class SimpleSession(Session):
    """
    Subclass of Session that configures the logging system for simple
    noninteractive usage.
    """

    autocreate_devices = False
    auto_modules = []

    def _beforeStart(self, maindev):
        pass

    @classmethod
    def run(cls, appname, maindevname=None, setupname=None, pidfile=True,
            daemon=False, start_args=[]):

        if daemon:
            daemonize()

        session.__class__ = cls
        try:
            session.__init__(appname)
            session.loadSetup(setupname or appname, allow_special=True)
            maindev = session.getDevice(maindevname or appname.capitalize())
        except NicosError, err:
            print >>sys.stderr, 'Fatal error while initializing:', err
            return 1

        def signalhandler(signum, frame):
            removePidfile(appname)
            maindev.quit()
        signal.signal(signal.SIGINT, signalhandler)
        signal.signal(signal.SIGTERM, signalhandler)

        if pidfile:
            writePidfile(appname)

        session._beforeStart(maindev)

        maindev.start(*start_args)
        maindev.wait()

        session.shutdown()


class NicosCompleter(rlcompleter.Completer):
    """
    This is a Completer subclass that doesn't show private attributes when
    completing attribute access.
    """

    def attr_matches(self, text):
        matches = rlcompleter.Completer.attr_matches(self, text)
        textlen = len(text)
        return [m for m in matches if not m[textlen:].startswith(('_', 'do'))]


class NicosInteractiveConsole(code.InteractiveConsole):
    """
    This class provides a console similar to the standard Python interactive
    console, with the difference that input and output are logged to the
    NICOS logger and will therefore appear in the logfiles.
    """

    def __init__(self, session, globals, locals):
        self.session = session
        self.log = session.log
        code.InteractiveConsole.__init__(self, globals)
        self.globals = globals
        self.locals = locals
        readline.parse_and_bind('tab: complete')
        readline.set_completer(NicosCompleter(self.globals).complete)
        readline.set_history_length(10000)
        self.histfile = os.path.expanduser('~/.nicoshistory')
        if os.path.isfile(self.histfile):
            readline.read_history_file(self.histfile)

    def interact(self, banner=None):
        code.InteractiveConsole.interact(self, banner)
        readline.write_history_file(self.histfile)

    def runsource(self, source, filename='<input>', symbol='single'):
        """Mostly copied from code.InteractiveInterpreter, but added the
        logging call before runcode().
        """
        try:
            code = self.compile(source, filename, symbol)
        except (OverflowError, SyntaxError, ValueError):
            self.log.exception()
            return False

        if code is None:
            return True

        self.log.log(INPUT, source)
        self.runcode(code)
        return False

    def raw_input(self, prompt):
        sys.stdout.write(colorcode('blue'))
        inp = raw_input(prompt)
        sys.stdout.write(colorcode('reset'))
        return inp

    def runcode(self, codeobj):
        """Mostly copied from code.InteractiveInterpreter, but added the
        logging call for exceptions.
        """
        try:
            exec codeobj in self.globals, self.locals
        except Exception:
            #raise
            self.session.logUnhandledException(sys.exc_info())
        else:
            if code.softspace(sys.stdout, 0):
                print
        #self.locals.clear()


class InteractiveSession(Session):
    """
    Subclass of Session that configures the logging system for interactive
    interpreter usage: it adds a console handler with colored output, and
    an exception hook that reports unhandled exceptions via the logging system.
    """

    def _initLogging(self):
        Session._initLogging(self)
        sys.displayhook = self.__displayhook

    def __displayhook(self, value):
        if value is not None:
            self.log.log(OUTPUT, repr(value))

    def console(self):
        """Run an interactive console, and exit after it is finished."""
        banner = ('NICOS console ready (version %s).\nTry help() for a '
                  'list of commands, or help(command) for help on a command.'
                  % nicos_version)
        console = NicosInteractiveConsole(self, self._Session__namespace,
                                         self._Session__local_namespace)
        console.interact(banner)
        sys.stdout.write(colorcode('reset'))

    @classmethod
    def run(cls, setup='startup'):
        # Assign the correct class to the session singleton.
        session.__class__ = InteractiveSession
        session.__init__('nicos')

        # Create the initial instrument setup.
        session.loadSetup(setup)

        # Try to become master.
        system = session.system
        try:
            system.setMode('master')
        except ModeError:
            system.printinfo('could not enter master mode; remaining slave')
        except:
            system.printwarning('could not enter master mode', exc=True)

        # Fire up an interactive console.
        session.console()

        # After the console is finished, cleanup.
        system.printinfo('shutting down...')
        session.shutdown()


class LoggingStdout(object):
    """
    Standard output stream replacement that tees output to a logger.
    """

    def __init__(self, orig_stdout):
        self.orig_stdout = orig_stdout

    def write(self, text):
        if text.strip():
            session.log.info(text)
        self.orig_stdout.write(text)

    def flush(self):
        self.orig_stdout.flush()


class DaemonSession(SimpleSession):
    """
    Subclass of Session that configures the logging system for running under the
    execution daemon: it adds the special daemon handler and installs a standard
    output stream that logs stray output.
    """

    autocreate_devices = True

    def _initLogging(self):
        SimpleSession._initLogging(self)
        sys.displayhook = self.__displayhook
        sys.stdout = LoggingStdout(sys.stdout)

    def __displayhook(self, value):
        if value is not None:
            self.log.log(OUTPUT, repr(value))

    def _beforeStart(self, daemondev):
        from nicos.daemon.utils import DaemonLogHandler
        daemon_handler = DaemonLogHandler(daemondev)
        # add handler to general NICOS logger
        self.log.handlers.append(daemon_handler)
        # and to all loggers created from now on
        self._log_handlers.append(daemon_handler)

        # Pretend that the daemon setup doesn't exist, so that another
        # setup can be loaded by the user.
        self.devices.clear()
        self.explicit_devices.clear()
        self.configured_devices.clear()
        self.user_modules.clear()
        self.loaded_setups.clear()
        del self.explicit_setups[:]

        self.auto_modules = ['nicos.commands']

        self._Session__system_device = None
        self._Session__exported_names.clear()


class WebSession(Session):
    """
    Subclass of Session that configures the logging system for usage in a web
    application environment.
    """

    def _initLogging(self):
        Session._initLogging(self)
        sys.displayhook = self.__displayhook

    def __displayhook(self, value):
        if value is not None:
            self.log.log(OUTPUT, repr(value))

    @classmethod
    def run(cls, setup='startup'):
        sys.stdin = FakeInput()

        session.__class__ = cls
        session.__init__('web')

        app = NicosApp()
        session._log_handlers.append(WebHandler(app._output_buffer))

        session.loadSetup(setup)

        srv = make_server('', 4000, app)
        session.log.info('web server running on port 4000')
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            session.log.info('web server shutting down')
