# -*- coding: utf-8 -*-
"""
    nicm.nicos
    ~~~~~~~~~~

    Contains the NICOS class, which contains all low-level global state
    of the NICOS runtime.

    Only for internal usage by functions and methods.
"""

import imp
import sys
import code
import logging
import traceback
from os import path

from nicm import __version__
from nicm.errors import NicmError, UsageError, ConfigurationError
from nicm.loggers import ColoredConsoleHandler, NicmLogfileHandler, \
     OUTPUT, INPUT, init_logging


class NICOS(object):
    """
    The NICOS class provides all low-level routines needed for NICOS
    operations and keeps the global state: devices, configuration,
    loggers.
    """

    def __init__(self):
        # contains all created device objects
        self.devices = {}
        # contains the name of all explicitly created devices
        self.explicit_devices = set()
        # contains the configuration for all configured devices
        self.configured_devices = {}
        # used during recursive setup
        self.__setup_level = 0
        # namespace to place user-accessible items in
        self.__namespace = {}
        # contains all NICOS-exported names
        self.__exported_names = set()

        self.__init_logging()

    def set_namespace(self, ns):
        """Set the namespace to export commands and devices into."""
        self.__namespace = ns
        self.__exported_names = set()

    def load_setup(self, modname, **variables):
        """Load a setup module and set up devices accordingly.

        The setup module is looked for in the setup/ directory which
        should be a sibling to this package's directory.
        """
        log = self.get_logger('setup')

        modpath = path.join(path.dirname(__file__), '..', 'setup')
        try:
            modfile = imp.find_module(modname, [modpath])
            code = modfile[0].read()
            modfile[0].close()
        except (ImportError, IOError), err:
            raise ConfigurationError('Could not find or read setup '
                                     'module %r: %s' % (modname, err))

        # since the include() function in setup modules calls this method,
        # we need to do different things when it is called recursively
        if self.__setup_level == 0:
            self.__setup_modules = set(['nicm.commands'])
            self.__setup_devices = {}
            self.__setup_startupcode = ''
        self.__setup_level += 1

        # put a few items into the namespace the setup module is executed in,
        # first the variables given by the caller
        ns = variables.copy()
        # then the function to load setup modules recursively
        ns['include'] = self.load_setup
        # and a helper to make the configuration code prettier
        ns['device'] = lambda cls, **params: (cls, params)

        exec code in ns

        log.info('loading %s' % ns.get('name', modname))

        self.__setup_modules.update(ns.get('modules', []))
        self.__setup_devices.update(ns.get('devices', {}))
        self.__setup_startupcode += '\n' + ns.get('startupcode', '')
        self.__setup_level -= 1

        if self.__setup_level > 0:
            # still in recursive setup call
            return

        sys.ps1 = '(%s)>>> ' % modname

        from nicm.commands import user_command
        for modname in self.__setup_modules:
            log.info('importing module %s... ' % modname, nonl=1)
            try:
                __import__(modname)
                mod = sys.modules[modname]
            except Exception, err:
                log.error('Exception importing %s' % modname)
                continue
            if hasattr(mod, '__commands__'):
                for name in mod.__commands__:
                    self.export(name, user_command(getattr(mod, name)))
            log.info('done')

        self.configured_devices.update(self.__setup_devices)

        failed_devs = []
        devlist = sorted(self.__setup_devices.iteritems())
        for devname, (_, devconfig) in devlist:
            if not devconfig.get('autocreate', True):
                continue
            log.info('creating device %r... ' % devname, nonl=1)
            try:
                self.create_device(devname, explicit=True)
                log.info('done')
            except Exception, err:
                log.info('failed')
                failed_devs.append((devname, err))
        if failed_devs:
            log.warning('the following devices could not be created')
            for info in failed_devs:
                log.info('  %-15s: %s' % info)

        exec self.__setup_startupcode in ns
        log.info('done')

    def unload_setup(self):
        """Unload the current setup: destroy all devices and clear the
        NICOS namespace.
        """
        for devname, dev in self.devices.items():
            dev.shutdown()
            self.unexport(devname)
        self.configured_devices.clear()
        for name in list(self.__exported_names):
            self.unexport(name)

    def export(self, name, object):
        self.__namespace[name] = object
        self.__exported_names.add(name)

    def unexport(self, name):
        if name not in self.__namespace:
            self.log.warning('unexport: name %r not in namespace' % name)
            return
        if name not in self.__exported_names:
            self.log.warning('unexport: name %r not exported by NICOS' % name)
        del self.__namespace[name]
        self.__exported_names.remove(name)

    def get_exported_objects(self):
        for name in self.__exported_names:
            if name in self.__namespace:
                yield self.__namespace[name]

    # -- Device control --------------------------------------------------------

    def get_device(self, dev, cls=None):
        """Convenience: get a device by name or instance."""
        if isinstance(dev, str):
            if dev in self.devices:
                dev = self.devices[dev]
            elif dev in self.configured_devices:
                dev = self.create_device(dev)
            else:
                raise UsageError('device %r not found in configuration' % dev)
        from nicm.device import Device
        if not isinstance(dev, cls or Device):
            raise UsageError('dev must be a %s' % cls.__name__)
        return dev

    def create_device(self, devname, recreate=False, explicit=False):
        """Create device given by a device name.

        If device exists and *recreate* is true, destroy and create it again.
        """
        if devname not in self.configured_devices:
            raise ConfigurationError('device %r not found in configuration'
                                     % devname)
        if explicit:
            self.explicit_devices.add(devname)
        if devname in self.devices:
            if not recreate:
                return self.devices[devname]
            self.destroy_device(devname)
        devclsname, devconfig = self.configured_devices[devname]
        modname, clsname = devclsname.rsplit('.', 1)
        devcls = getattr(__import__(modname, None, None, [clsname]),
                         clsname, None)
        if devcls is None:
            raise ConfigurationError('type of device %r does not exist'
                                     % devclsname)
        dev = devcls(devname, devconfig)
        self.devices[devname] = dev
        self.export(devname, dev)
        return dev

    def destroy_device(self, devname):
        """Shutdown and destroy a device."""
        if devname not in self.devices:
            raise UsageError('device %r not created' % devname)
        self.devices[devname].shutdown()
        del self.devices[devname]
        self.explicit_devices.discard(devname)
        if devname in self.__namespace:
            self.unexport(devname)

    # -- Logging ---------------------------------------------------------------

    def __init_logging(self):
        init_logging()
        self.__loggers = {}
        self.__handlers = [ColoredConsoleHandler(), NicmLogfileHandler()]
        self.log = self.get_logger('nicos')
        # XXX make this conditional
        sys.excepthook = self.__excepthook
        sys.displayhook = self.__displayhook

    def __displayhook(self, value):
        if value is not None:
            self.log.log(OUTPUT, repr(value))

    def __excepthook(self, etype, evalue, etb):
        self.log.error('unhandled exception occurred',
                       exc_info=(etype, evalue, etb))

    def get_logger(self, name):
        if name in self.__loggers:
            return self.__loggers[name]
        logger = logging.getLogger(name)
        # XXX must be configurable
        logger.setLevel(logging.DEBUG)
        for handler in self.__handlers:
            logger.addHandler(handler)
        self.__loggers[name] = logger
        return logger

    # -- interactive (logging) console -----------------------------------------

    def console(self):
        """Run an interactive console, and exit after it is finished."""
        banner = ('NICOS console ready (version %s).\nTry help() for a '
                  'list of commands, or help(command) for help.' % __version__)
        console = NicmInteractiveConsole(self, self.__namespace)
        console.interact(banner)
        sys.exit()


class NicmInteractiveConsole(code.InteractiveConsole):
    def __init__(self, nicos, locals):
        self.log = nicos.log
        code.InteractiveConsole.__init__(self, locals)

    def runsource(self, source, filename='<input>', symbol='single'):
        """Mostly copied from code.InteractiveInterpreter, but added the
        logging call before runcode().
        """
        try:
            code = self.compile(source, filename, symbol)
        except (OverflowError, SyntaxError, ValueError):
            self.log.exception('invalid syntax')
            return False

        if code is None:
            return True

        self.log.log(INPUT, source)
        self.runcode(code)
        return False

    def runcode(self, codeobj):
        try:
            exec codeobj in self.locals
        except Exception:
            self.log.exception('unhandled exception occurred')
        else:
            if code.softspace(sys.stdout, 0):
                print
