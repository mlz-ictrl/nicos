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
#   Markus Zolliker <markus.zolliker@psi.ch>
#
# *****************************************************************************

"""Support for SECoP

This module contains a SecNode device, which represent connections to a SECoP
server, and the base classes SecopDevice, SecopReadable and SecopMoveable.

A SecNodeDevice is connected to a SecNode by assigning the uri value, this
can be done at any time. With auto_create == True, all devices are created
automatically after connections, and they are altered on reconnection.

For a setup for permanent use, with auto_create == False (the default), the
devices are to be created with the class SecopDevice, SecopReadable or
SecopMoveable, and the following parameters:

- secnode: the secnode device name
- secop_module: the name of the remotely connected SECoP module
- params_cfg (optional): a dict {<parameter name>: <cfg dict>}
  if given, only the parameters mentioned as keys are exported.
  The cfg dict may be empty for using the automatically generated attributes:
  description, datainfo, settable, unit and fmtstr.
  The data type must be given as SECoP datainfo converted from json,
  not as NICOS type!
  Attributes given in the cfg dict may overwrite above attributes.
"""

import re
import time
from collections import defaultdict
from math import floor, log10
from threading import Event, RLock

from frappy.client import SecopClient
from frappy.datatypes import StatusType
from frappy.errors import CommunicationFailedError, ReadFailedError

from nicos import session
from nicos.core import POLLER, SIMULATION, Attach, DeviceAlias, HasLimits, \
    HasOffset, NicosError, Override, Param, status, usermethod
from nicos.core.device import Device, DeviceMeta, DeviceMetaInfo, \
    DeviceParInfo, Moveable, Readable
from nicos.core.errors import CommunicationError, ConfigurationError
from nicos.core.params import anytype, dictof, floatrange, intrange, listof
from nicos.core.utils import formatStatus
from nicos.devices.secop.validators import get_validator
from nicos.protocols.cache import cache_dump
from nicos.utils import createThread, importString, merge_dicts, printTable
try:
    # TODO: remove try/except when frappy is updated on all sites
    from frappy.datatypes import visibility_validator
except ImportError:
    LEGACY_VISIBILITY = {'user': 'www', 1: 'www', 'advanced': 'ww-', 2: 'ww-', 'expert': 'w--', 3: 'w--'}

    def visibility_validator(value):
        value = LEGACY_VISIBILITY.get(value, value)
        if len(value) == 3 and set(value) <= set('wr-'):
            return value
        raise ValueError(f'{value!r} is not a valid visibility')


class NicosSecopClient(SecopClient):
    SPECIAL_NAMES = {'target', 'status', 'stop', 'pollinterval', 'reset'}

    def internalize_name(self, name):
        """name mangling

        - names matching the names of NICOS Moveable attributes
          are mangled, as they would conflict.
        - however, names with a special treatment in SecopDevice.makeDevClass
          are *not* mangled
        """
        if name in self.SPECIAL_NAMES:
            return name
        name = super().internalize_name(name).lower()
        prefix, sep, postfix = name.partition('_')
        if prefix not in dir(SecopMoveable):
            return name
        # mangle names matching NICOS device attributes
        # info -> info_, info_ -> info_1, info_1 -> info_2, ...
        if not sep:
            return name + '_'
        if not postfix:
            return name + '_1'
        try:
            num = int(postfix)
            if str(num) == postfix:
                return '%s_%d' % (prefix, num + 1)
        except ValueError:
            pass
        return name


class DefunctDevice(Exception):
    pass


def clean_identifier(anystring):
    return str(re.sub(r'\W+|^(?=\d)', '_', anystring))


def type_name(typ):
    try:
        return typ.__name__
    except AttributeError:
        return typ.__class__.__name__


def get_aliases(dev):
    """get devices aliased to on dev

    return a list containing for each alias a tuple (device, required class).
    """
    # check that the new class fits the required classes on devices self
    # is attached to
    result = []
    for alias in session.devices.values():
        if isinstance(alias, DeviceAlias) and alias.alias == dev.name:
            result.append((alias, alias._cls))
    return result


def get_attaching_devices(dev):
    """get devices attached to dev

    return a list of tuples (device, required class).
    """
    result = []
    for devname in dev._sdevs:
        sdev = session.devices.get(devname)
        if sdev:
            for aname, att in sdev.attached_devices.items():
                if getattr(sdev, '_attached_' + aname, None) == dev:
                    result.append((sdev, att.devclass))
    return result


def class_from_interface(module_properties):
    for ifclass in (module_properties.get('interface_classes', []) or
                    module_properties.get('interface_class', [])):
        try:
            return IF_CLASSES[ifclass.title()]
        except KeyError:
            continue
    return SecopDevice


def secop_base_class(cls):
    """find the first base class from IF_CLASSES in cls"""
    for b in cls.__mro__:
        if b in ALL_IF_CLASSES:
            return b
    raise TypeError('secop_base_class argument must inherit from SecopDevice')


def get_exc_name(exc):
    # get name of SECoPError, NicosError or other error
    return getattr(exc, 'name', 0) or getattr(exc, 'category', 0) or type(exc).__name__


def make_nicos_error(exc, category=None):
    """convert SECoP error to nicos error

    nicer logging compared to NicosError(str(exc)):
    "<secop-error-class> - <str(exc)>" instead of "Error - <str(exc>)>"
    """
    if isinstance(exc, NicosError):
        return exc
    if category is None:
        category = get_exc_name(exc)
    # do not repeat category when contained already at start
    text = re.sub(f'^{category} ?[-:]? ', '', str(exc))
    # NicosLogger needs category to be a class attribute
    # still inherit from SECoP error class
    return type('NicosSecopError', (type(exc), NicosError), {'category': category})(text)


class SecNodeDevice(Readable):
    """SEC node device.

    want to have a status -> based on Readable
    """

    parameters = {
        'prefix':      Param("Prefix for the generated devices\n\n"
                             "'$' will be replaced by the equipment id."
                             " It should end with a trailing underscore",
                             type=str, default='$_', settable=True),
        'uri':         Param('tcp://<host>:<port>', type=str, settable=True),
        'auto_create': Param('Flag for automatic creation of devices',
                             type=bool, prefercache=False, userparam=False),
        'setup_info':  Param('Setup info', type=anytype, default={},
                             settable=True),
        'visibility_level': Param('level for visibility of created devices',
                                  type=intrange(1, 3), prefercache=False,
                                  default=1, userparam=False),
        'async_only':  Param('True: inhibit SECoP reads on created devices, '
                             'use events only', type=bool, prefercache=False,
                             default=False, userparam=False),
        'allow_list':  Param('list of device names to allow creating',
                             ext_desc='The original names found on the'
                             ' SecNode are looked at. If the allow_list is'
                             ' empty, all modules are allowed',
                             type=listof(str), prefercache=False, default=[],
                             userparam=False),
        'device_mapping': Param('Dict of mappings for Name and Mixins ',
                                type=dictof(str, dictof(str, anytype)),
                                prefercache=False, default={}, userparam=False),
        'general_stop_whitelist': Param('module names to accept general stop',
                                        type=listof(str), prefercache=False,
                                        default=[], userparam=False),
        'general_stop_blacklist': Param('module names to ignore general stop',
                                        type=listof(str), prefercache=False,
                                        default=[], userparam=False)
    }
    parameters['device_mapping'].ext_desc = """
    Dictionary name -> mapping where mapping is a dictionary which can contain
    the following keys:
    name -> remapped name of the device
    mixins -> list of names of mixin classes that should be added to the class
    parameters -> list of parameters for configuration of the mixins

    For example, from a secnode with the modules examplemodule and barcodes,
    among others:

    .. code:

        secnode = device(
            'nicos.devices.secop.SecNodeDevice',
            description='doc demo',
            uri = 'tcp://localhost:10767',
            auto_create = True,
            unit='',
            device_mapping = {
                'examplemodule': {
                    'name': 'ExampleName',
                },
                'barcodes': {
                    'mixins':
                        ['nicos_mlz.devices.barcodes.BarcodeInterpreterMixin'],
                },
                'parameters': {
                    'commandmap': {},
                },
            },
            allow_list = ['barcodes', 'examplemodule'],
        ),

    Barcodes will then be mapped to a NICOS-device called nodname_barcodes and
    examplemodule will become a device named ExampleName.
    """

    parameters['general_stop_whitelist'].ext_desc = """
    If this value is not empty, it is a list of SECoP module names accepting
    general stop, modules not listed will ignore general stop. The parameter
    'general_stop_blacklist' must be empty in this case.
    """

    parameters['general_stop_blacklist'].ext_desc = """
    This value contains a list of SECoP module names ignoring
    general stop, Modules not listed will accept general stop.
    """

    parameter_overrides = {
        'unit': Override(default='', mandatory=False),
        # maxage is not used on the SecNodeDevice itself, but is the base
        # for calculating a slightly hihger value on the SecopReadable instances
        'maxage': Override(default=600, userparam=False),
        # not used:
        'pollinterval': Override(default=None, userparam=False, settable=False),
    }

    valuetype = str
    _secnode = None
    _value = ''
    _status = status.OK, 'unconnected'   # the nicos status
    _devices = {}
    _custom_callbacks = defaultdict(list)
    _polled_devs = ()
    __poll_thread = None

    def doPreinit(self, mode):
        self._devices = {}

    def doInit(self, mode):
        if mode == SIMULATION:
            setup_info = self.get_setup_info()
            if self.auto_create:
                self.makeDynamicDevices(setup_info)
            else:
                self._setROParam('setup_info', setup_info)
        elif session.sessiontype != POLLER:
            if self.uri:
                try:
                    self._connect()
                except Exception:
                    self.log.exception('during initial connect')
            if self.maxage is None:
                self.maxage = 600
            self.__shutdown = Event()
            self._polled_devs = [dev for dev in self._devices.values()
                                 if isinstance(dev, SecopReadable)]
            self.__poll_thread = createThread('poll-thread', self.__poll)

    def get_setup_info(self):
        if self._mode == SIMULATION:
            db = session.getSyncDb()
            return db.get('%s/setup_info' % self.name.lower())
        return self.setup_info

    def __poll(self):
        """simple poll thread

        needed only for making sure value and status do not expire.
        we can not use the regular poller for this, as dynamic devices
        are not registered there
        """
        if not self._polled_devs:  # avoid busy loop
            return
        while True:
            if not self._cache:  # defunct sec node
                return
            for dev in self._polled_devs:
                if self.__shutdown.wait(1):
                    return
                # status()/read() do only call doStatus()/doRead() when the
                # value is older than self.maxage. the maximum age will then be
                # a little higher, as calculated in SecopReadable.doReadMaxage
                try:
                    dev.status(self.maxage)
                except Exception as e:
                    dev.log.debug('error calling status(): %r', e)
                try:
                    dev.read(self.maxage)
                except Exception as e:
                    dev.log.debug('error calling read(): %r', e)

    def doRead(self, maxage=0):
        if self._secnode:
            if self._secnode.online:
                self._value = self._secnode.nodename
        else:
            self._value = ''
        return self._value

    def doStatus(self, maxage=0):
        return self._status

    def _set_status(self, code, text):
        self._status = code, text
        if self._cache:
            self._cache.put(self, 'status', self._status)
            self._cache.put(self, 'value', self.doRead())

    def doWriteUri(self, value):
        """change uri and reconnect"""
        # make sure uri is set before reconnect
        self._setROParam('uri', value)
        if self.uri:
            self._connect()
        else:
            self._disconnect()
        return value

    def _connect(self):
        """try to connect

        called on creation and on uri change,
        but NOT on automatic reconnection
        """
        if not self.uri:
            self._disconnect()
        if self._secnode:
            self._secnode.disconnect()
        self._secnode = NicosSecopClient(self.uri, log=self.log)
        self._secnode.register_callback(None, self.nodeStateChange,
                                        self.descriptiveDataChange)
        try:
            self._secnode.connect(10)
            self._set_status(status.OK, 'connected')
            self.createDevices()
            return
        except Exception as e:
            if not isinstance(e, CommunicationFailedError):
                raise
            self.log.warning('can not connect to %s (%s), retry in background',
                             self.uri, e)
            self._set_status(status.ERROR, 'try connecting')
            start_event = Event()
            self._secnode.spawn_connect(start_event.set)

    def _disconnect(self):
        if not self._secnode:
            return
        self.removeDevices()
        self._secnode.disconnect()
        self._set_status(status.OK, 'unconnected')
        self._secnode = None

    def descriptiveDataChange(self, module, description):
        """called when descriptive data changed

        after an automatic reconnection"""
        self.log.warning('node description changed')
        self.createDevices()

    def get_status(self, online, state):
        if not online:
            return status.ERROR, state
        return status.OK if state == 'connected' else status.WARN, state

    def nodeStateChange(self, online, state):
        """called when the state of the connection changes

        'online' is True when connected or reconnecting, False when
                 disconnected or connecting
        'state' is the connection state as a string
        """
        if online and state == 'connected':
            self._set_status(status.OK, 'connected')
            for device in self._devices.values():
                device.setConnected(True)
        elif not online:
            self._set_status(status.ERROR, 'reconnecting')
            for device in self._devices.values():
                device.setConnected(False)
        else:
            self._set_status(status.WARN, state)

    def doShutdown(self):
        if self.__poll_thread:
            self.__shutdown.set()
            self.__poll_thread.join()
        self._disconnect()
        if self._devices:
            self.log.error('can not remove devices %s', list(self._devices))

    def _get_prefix(self):
        if self._secnode is None:
            # at least when prefix does not contain '$', this works in dry run
            return self.prefix
        equipment_name = clean_identifier(self._secnode.nodename).lower()
        return self.prefix.replace('$', equipment_name)

    def _get_device_name(self, module):
        """get a modules mapped name according to device_mapping or None,
        if unmapped
        """
        if module in self.device_mapping \
           and 'name' in self.device_mapping[module]:
            return self.device_mapping[module]['name']
        return self._get_prefix() + module

    @usermethod
    def showModules(self):
        """show modules of the connected SECoP server

        and intended devices names using the given prefix
        """
        if self._sim_intercept:
            return
        if self._secnode is None:
            self.log.error('secnode is not connected')
            return
        items = [
            (self._get_prefix() + m, m,
             mod_desc.get(
                 'properties', {}).get('description', '').split('\n')[0])
            for m, mod_desc in self._secnode.modules.items()]
        printTable(['foreseen device name', 'SECoP module', 'description'],
                   items, self.log.info)

    def registerDevice(self, device):
        if not self._secnode:
            raise OSError('unconnected')
        self.log.debug('register %s on %s', device, self)
        self._devices[device.name] = device
        module = device.secop_module
        if module not in self._secnode.modules:
            raise ConfigurationError('no module %r found on this SEC node'
                                     % module)
        for parameter in self._secnode.modules[module]['parameters']:
            updatefunc = getattr(device, '_update_' + parameter,
                                 device._update)
            self._secnode.register_callback((module, parameter),
                                            updateItem=updatefunc)
            try:
                data = self._secnode.cache[module, parameter]
                if data:
                    updatefunc(module, parameter, data)
                else:
                    self.log.warning('No data for %s:%s', module, parameter)
            except KeyError:
                self.log.warning('No cache for %s:%s', module, parameter)

    def unregisterDevice(self, device):
        self.log.debug('unregister %s from %s', device, self)
        if self._devices.pop(device.name, None) is None:
            self.log.info('device %s already removed', device.name)
            return
        module = device.secop_module
        try:
            moddesc = self._secnode.modules[module]
        except KeyError:  # do not complain again about missing module
            return
        for parameter in moddesc['parameters']:
            updatefunc = getattr(device, '_update_' + parameter,
                                 device._update)
            self._secnode.unregister_callback((module, parameter),
                                              updateItem=updatefunc)
            for custom_callback in self._custom_callbacks.pop((module, parameter), []):
                self._secnode.unregister_callback((module, parameter),
                                                  updateItem=custom_callback)

    def createDevices(self):
        """create drivers and devices

        for the devices to be created from the connected SECoP server
        """
        if not self._secnode:
            self.log.error('secnode is not connected')
            return
        setup_info = {}
        # keep track of configured devices to warn when one is configured
        # without being found on the SECNode or filtered by allow_list
        configured = set(self.device_mapping.keys())
        if self.general_stop_whitelist:
            if self.general_stop_blacklist:
                self.log.error('only one of general_stop_blacklist/'
                               'general_stop_whitelist may be given')
                self.log.error('-> general_stop_blacklist is ignored')
            general_stop_blacklist = (set(self._secnode.modules) -
                                      set(self.general_stop_whitelist))
        else:
            general_stop_blacklist = set(self.general_stop_blacklist)
        for module, mod_desc in self._secnode.modules.items():
            # If the module should not be created, skip it
            if self.allow_list and module not in self.allow_list:
                self.log.debug('skipping module %s, as it is not in the list'
                               ' of allowed modules', module)
                continue

            if module in configured:
                configured.remove(module)
            module_properties = mod_desc.get('properties', {})
            kwds = {
                'secop_properties': module_properties,
            }
            # Map device name according to config
            dev_name = self._get_device_name(module)
            self.log.debug('using device name %s for SECoP-module %s',
                           dev_name, module)
            # convert parameters and command description to the needed items,
            # especially avoid datatype or a nicos type here,
            # as this would need pickle to put into the cache.
            # datainfo is no problem
            params_cfg = {}
            for pname, props in mod_desc['parameters'].items():
                datainfo = props['datainfo']
                # take only the first line in description, else it would
                # messup ListParams
                # TODO: check whether is not better to do this in ListParams
                pargs = dict(datainfo=datainfo, description=(
                        props['description'].splitlines() or [''])[0])
                if not props.get('readonly', True) and pname != 'target':
                    pargs['settable'] = True
                unit = datainfo.get('unit', '')
                fmtstr = None
                if datainfo['type'] == 'double':
                    fmtstr = datainfo.get('fmtstr', '%g')
                elif datainfo['type'] == 'scaled':
                    fmtstr = datainfo.get(
                        'fmtstr', '%%.%df' %
                                  max(0, -floor(log10(datainfo['scale']))))
                if unit:
                    pargs['unit'] = unit
                if pname == 'target':
                    kwds['target_datainfo'] = datainfo
                    pargs['datainfo'] = None
                elif pname == 'value':
                    kwds['unit'] = unit
                    if fmtstr is not None:
                        kwds['fmtstr'] = fmtstr
                    else:
                        kwds['fmtstr'] = '%r'
                    kwds['value_datainfo'] = datainfo
                if pname not in ('status', 'value'):
                    if fmtstr is not None and fmtstr != '%g':
                        pargs['fmtstr'] = fmtstr
                    params_cfg[pname] = pargs
            commands_cfg = {
                cname: {'description': props.get('description', ''),
                        'datainfo': props['datainfo']}
                for cname, props in mod_desc['commands'].items()}
            mixins = self.device_mapping.get(module, {}).get('mixins', [])
            kwds.update(self.device_mapping.get(
                module, {}).get('parameters', []))
            cls = class_from_interface(module_properties)
            if isinstance(cls, SecopReadable):
                kwds.setdefault('unit', '')  # unit is mandatory on Readables
            # convert legacy to new SECoP visibility
            visibility = visibility_validator(module_properties.get('visibility', 'www'))
            if visibility[3 - self.visibility_level] != 'w':
                # example: for "ww-" above is True for visibility level 2 and 3
                # TODO: handle readonly visibility properly
                kwds['visibility'] = ()
            if 'ignore_general_stop' in cls.parameters:
                kwds['ignore_general_stop'] = module in general_stop_blacklist
            desc = dict(secnode=self.name,
                        description=mod_desc.get('properties', {}).get(
                            'description', ''),
                        secop_module=module,
                        params_cfg=params_cfg,
                        commands_cfg=commands_cfg,
                        mixins=mixins,
                        **kwds)

            # the following test may be removed later, when no bugs appear ...
            if 'cache_unpickle("' in cache_dump(desc):
                self.log.error('module %r skipped - setup info needs pickle',
                               module)
            else:
                setup_info[dev_name] = (
                    'nicos.devices.secop.devices.%s' % cls.__name__, desc)
        if not setup_info:
            self.log.info('creating devices for %s skipped', self.name)
            return
        if self.auto_create:
            if configured:
                self.log.warning('configured modules were not found or were'
                                 ' skipped during creation: %s!',
                                 list(configured))
            self.makeDynamicDevices(setup_info)
        else:
            self._setROParam('setup_info', setup_info)

    def removeDevices(self):
        self.makeDynamicDevices({})

    def makeDynamicDevices(self, setup_info):
        """create and destroy dynamic devices

        create devices from setup_info, and store the name of the setup
        creating the creator device in session.creator_devices for
        session.getSetupInfo()
        Based on the previous setup_info from self.setup_info,
        devices are created, recreated, destroyed or remain unchanged.
        If setup_info is empty, destroy all devices.
        """
        prevdevices = set(self.setup_info.keys())
        self._setROParam('setup_info', setup_info)

        # find setup of this secnode
        result = session.getSetupInfo()
        setupname = None  # only to avoid undefined-loop-variable later
        for setupname in session.loaded_setups:
            info = result.get(setupname, None)
            if info and self.name in info['devices']:
                break
        else:
            raise ConfigurationError('can not find setup')
        # add new or changed devices
        for devname, devcfg in setup_info.items():
            prevdevices.discard(devname)
            dev = session.devices.get(devname, None)
            if dev:
                if not isinstance(dev, SecopDevice) or (
                        dev._attached_secnode and
                        dev._attached_secnode != self):
                    self.log.error('device %s already exists', devname)
                    continue
                base = secop_base_class(dev.__class__)
                prevcfg = (base.__module__ + '.' + base.__name__,
                           dict(secnode=self.name, **dev._config))
            else:
                prevcfg = None
            session.configured_devices[devname] = devcfg
            session.dynamic_devices[devname] = setupname
            if prevcfg == devcfg:
                if dev._defunct:
                    dev.setAlive(self)
            else:
                if dev is None:
                    # add new device
                    session.createDevice(devname, recreate=True, explicit=True)
                    dev = session.devices[devname]
                else:
                    # modify existing device
                    if dev._attached_secnode:
                        dev._attached_secnode.unregisterDevice(dev)
                    try:
                        dev.replaceClass(devcfg[1])
                        dev.setAlive(self)
                    except ConfigurationError:
                        # above failed because an alias or attaching device
                        # requires a specific class.
                        # make old device defunct and replace by a new device
                        session.destroyDevice(dev)
                        session.dynamic_devices.pop(devname, None)
                        session.createDevice(devname, recreate=True,
                                             explicit=True)
                        prevdevices.discard(devname)
                        dev = session.devices[devname]
                if not isinstance(dev, SecopReadable):
                    # we will not get status updates for these
                    dev.updateStatus()

        defunct = set()
        # defunct devices no longer available
        for devname in prevdevices:
            dev = session.devices.get(devname)
            if dev is None or dev._attached_secnode != self:
                continue
            # do not consider temporary devices
            sdevs = [att for att in dev._sdevs if att in session.devices]
            if sdevs:
                self.log.warning('defunct device is attached to %s',
                                 ', '.join(sdevs))
            dev.setDefunct()
            defunct.add(devname)

        # inform client that setups have changed
        session.setupCallback(list(session.loaded_setups),
                              list(session.explicit_setups))

    def register_custom_callback(self, module, parameter, f):
        """Register custom callbacks for parameter updates.

        Use the method found on the SecopDevice class instead of this directly.
        """
        # TODO: or NameError?
        if module not in self._secnode.modules:
            raise ValueError('no module %r found on this SEC node' % module)
        if parameter not in self._secnode.modules[module]['parameters']:
            raise ValueError('no parameter %r found on module %r of this SEC node'
                             % (parameter, module))
        self._custom_callbacks[(module, parameter)].append(f)
        self._secnode.register_callback((module, parameter), updateItem=f)
        self.log.debug('registered callback %r for %s:%s', f.__name__,
                       module, parameter)

    def unregister_custom_callback(self, module, parameter, f):
        """Unregister a custom callback on this Node (prefer function on SecopDevice)."""
        # TODO: or NameError?
        if module not in self._secnode.modules:
            raise ValueError('no module %r found on this SEC node' % module)
        if parameter not in self._secnode.modules[module]['parameters']:
            raise ValueError('no parameter %r found on module %r of this SEC node'
                             % (parameter, module))
        try:
            self._custom_callbacks[(module, parameter)].append(f)
            self._secnode.register_callback((module, parameter), updateItem=f)
        except ValueError as e:
            raise ValueError('function not registered as callback!') from e
        self.log.debug('removed callback %r from %s:%s', f.__name__,
                       module, parameter)


class SecopDevice(Device):
    """Represent a SECoP module.

    Has a status (for the connection and errors on parameters)
    but no value, therefore not based on Readable
    """
    attached_devices = {
        'secnode': Attach('sec node', SecNodeDevice),
    }
    parameters = {
        'secop_module': Param('SECoP module', type=str, settable=False,
                              userparam=False),
        'secop_properties': Param('SECoP module properties',
                                  type=anytype, settable=False,
                                  userparam=False),
        'mixins': Param('Mixins to add to this Device', type=listof(str),
                        settable=False, userparam=False, default=[]),
    }
    _defunct = False
    _cache = None
    _inside_read = False
    # overridden by a dict for the validators of 'value', 'status' and 'target':
    _maintypes = ()

    @classmethod
    def makeDevClass(cls, name, **config):
        """create a class with the needed doRead/doWrite methods

        for accessing the assigned SECoP module
        """
        secnodedev = session.getDevice(config['secnode'])
        # get config from SECNode
        setup_info = secnodedev.get_setup_info()

        # The key in setup_info is the mapped/prefixed name a device gets when
        # dynamically created. With static creation, this might differ from
        # the 'name' argument.
        dynamic_devname = secnodedev._get_device_name(config['secop_module'])
        seccfg = setup_info[dynamic_devname][1]
        # configuration must override SECoP description
        devcfg = merge_dicts(seccfg, config)
        add_mixins = devcfg.pop('mixins', [])

        # create parameters and methods
        parameters = {}
        # validators of special/pseudo parameters
        maintypes = {'value': anytype, 'status': tuple, 'target': anytype}
        attrs = dict(parameters=parameters, __module__=cls.__module__, _maintypes=maintypes)
        if 'value_datainfo' in devcfg:
            maintypes['value'] = get_validator(
                devcfg.pop('value_datainfo'), use_limits=False)
        if 'target_datainfo' in devcfg:
            attrs['valuetype'] = maintypes['target'] = get_validator(
                devcfg.pop('target_datainfo'), use_limits=True)
        for pname, kwargs in devcfg['params_cfg'].items():
            typ = get_validator(kwargs.pop('datainfo'),
                                use_limits=kwargs.get('settable', False))
            if 'fmtstr' not in kwargs and (typ is float or
                                           isinstance(typ, floatrange)):
                # the fmtstr default differs in SECoP and NICOS
                # copy kwargs as it may be read only
                kwargs = dict(kwargs, fmtstr='%g')
            parameters[pname] = Param(volatile=True, type=typ, **kwargs)

            if pname == 'target':
                continue  # special treatment of target in doReadTarget

            def do_read(self, pname=pname):
                return self._read(pname, None)

            attrs['doRead%s' % pname.title()] = do_read

            if kwargs.get('settable', False):
                def do_write(self, value, pname=pname):
                    return self._write(pname, value)

                attrs['doWrite%s' % pname.title()] = do_write

        for cname, cmddict in devcfg['commands_cfg'].items():

            if cname == 'reset':
                continue  # special treatment of reset command in doReset

            def makecmd(cname, datainfo, description):
                argument = datainfo.get('argument')

                validate_result = get_validator(
                    datainfo.get('result'), use_limits=False)

                if argument is None:
                    help_arglist = ''

                    def cmd(self):
                        return validate_result(self._call(cname, None))

                elif argument['type'] == 'tuple':
                    # treat tuple elements as separate arguments
                    help_arglist = ', '.join(
                        '<%s>' % type_name(get_validator(t, use_limits=False))
                        for t in argument['members'])

                    def cmd(self, *args):
                        return validate_result(self._call(cname, args))

                elif argument['type'] == 'struct':
                    # treat SECoP struct as keyworded arguments
                    # positional args will be treated in the given order
                    # which is not guaranteed to be kept in SECoP
                    optional = datainfo.get('optional')
                    keys = list(argument['members'])
                    if optional is None:
                        optional = list(keys)
                    for key in optional:
                        keys.remove(key)
                    help_arglist = ', '.join(keys + ['%s=None' % k
                                                     for k in optional])
                    keys.extend(optional)

                    def cmd(self, *args, **kwds):
                        if len(args) > len(keys):
                            raise ValueError('too many arguments')
                        for arg, key in zip(args, keys):
                            if key in kwds:
                                raise ValueError(
                                    'got multiple values for argument %r'
                                    % key)
                            kwds[key] = arg
                        return validate_result(self._call(cname, kwds))

                else:
                    help_arglist = '<%s>' % type_name(
                        get_validator(argument, use_limits=False))

                    def cmd(self, arg):
                        return validate_result(self._call(cname, arg))

                cmd.help_arglist = help_arglist
                cmd.__doc__ = description
                cmd.__name__ = cname
                return cmd

            old = getattr(cls, cname, None)
            if old is None:
                attrs[cname] = usermethod(makecmd(cname, **cmddict))
            elif cname != 'stop':
                # stop is handled separately, do not complain
                session.log.warning(
                    'skip command %s, as it would overwrite method of %r',
                    cname, cls.__name__)

        # see if secop_properties exists (the case when auto-created from the
        # SecNode) or not, where we need to get it from setup_info.
        if 'secop_properties' not in devcfg:
            devname = secnodedev._get_device_name(devcfg['secop_module'])
            devcfg['secop_properties'] = secnodedev.setup_info[devname][1].get(
                'secop_properties', {}
            )

        classname = cls.__name__ + '_' + name
        # create a new class extending SecopDevice, apply DeviceMeta in order
        # to include the added parameters
        features = devcfg['secop_properties'].get('features', [])
        mixins = [importString(mixin) for mixin in add_mixins]
        mixins.extend([FEATURES[f] for f in features if f in FEATURES])
        if set(devcfg['params_cfg']) & {'target_limits', 'target_min', 'target_max'}:
            mixins.append(SecopHasLimits)
        if mixins:
            # create class to hold access methods
            newclass = DeviceMeta.__new__(
                DeviceMeta, classname + '_base', (cls,), attrs)
            # create class with mixins, with methods overriding access methods
            mixins.append(newclass)
            newclass = DeviceMeta.__new__(
                DeviceMeta, classname, tuple(mixins), {})
        else:
            newclass = DeviceMeta.__new__(
                DeviceMeta, classname, (cls,), attrs)
        newclass._modified_config = devcfg  # store temporarily for __init__
        return newclass

    def __new__(cls, name, **config):
        """called when an instance of the class is created but before __init__

        instead of returning a SecopDevice, we create an object of an extended
        class here
        """
        newclass = cls.makeDevClass(name, **config)
        return Readable.__new__(newclass)

    def __init__(self, name, **config):
        """apply modified config"""
        self._attached_secnode = None
        self._read_lock = RLock()
        self._pending_updates = {}
        self._param_errors = {}
        Device.__init__(self, name, **self._modified_config)
        del self.__class__._modified_config

    def replaceClass(self, config):
        """replace the class on the fly

        happens when the structure for the device has changed
        """
        cls = class_from_interface(config['secop_properties'])
        newclass = cls.makeDevClass(self.name, **config)
        bad_attached = False
        for dev, cls in get_attaching_devices(self):
            if issubclass(newclass, cls):
                self.log.warning('reattach %s to %s', dev.name, self.name)
            else:
                self.log.error('can not attach %s to %s', dev.name, self.name)
                bad_attached = True
        if bad_attached:
            raise ConfigurationError('device class mismatch')
        for dev, cls in get_aliases(self):
            if issubclass(newclass, cls):
                if dev.alias != self.name:
                    self.log.warning('redirect alias %s to %s',
                                     dev.name, self.name)
            else:
                self.log.error('release alias %s from %s', dev.name, self.name)
                dev.alias = ''
        self.__class__ = newclass
        # as we do not go through self.__init__ again,
        # we have to update self._config
        self._config = dict((name.lower(), value)
                            for (name, value) in config.items())
        for aname in self.attached_devices:
            self._config.pop(aname, None)

    def doPreinit(self, mode):
        if mode != SIMULATION:
            self._attached_secnode.registerDevice(self)

    def _cache_update(self, parameter):
        # trigger nicos cache update and trigger doRead<param>/doRead/doStatus
        # respecting methods of mixins
        try:
            if parameter == 'status':
                return self.status(0)
            if parameter == 'value':
                result = self.read(0)
            else:
                result = getattr(self, parameter)  # trigger doRead<param>
            if parameter in self._param_errors:
                self._param_errors.pop(parameter)
                self.status(0)  # modifying _param_errors affects status
            return result
        except Exception as e:
            if self._cache:
                self._cache.invalidate(self, parameter)
            try:
                param_item = self._attached_secnode._secnode.cache[
                        self.secop_module, parameter]
                if not param_item.readerror:  # the error is not handled yet
                    # this may happen when a value of a settable parameter
                    # is updated to a value outside the range
                    param_item.readerror = e
            except Exception:
                pass
            if not isinstance(e, ReadFailedError):
                # The SECoP spec states "ReadFailed" indicates "parameter can
                # not be read _just now_". We assume this error happens not
                # on a hardware failure (which would be HardwareError), but in
                # a foreseeable way, depending on the state of the module
                # -> do not worry the user
                self._param_errors[parameter] = make_nicos_error(e)
            self.status(0)

    def _update(self, module, parameter, item):
        if parameter not in self.parameters and parameter not in self._maintypes:
            return
        if self._inside_read:
            # this thread is inside secnode.getParameter.
            # indicate to the getter that a cache update has to be done:
            self._pending_updates[parameter] = True
        else:
            with self._read_lock:
                try:
                    # do not allow to call getParameter again
                    self._inside_read = True
                    self._cache_update(parameter)
                finally:
                    self._inside_read = False

    def _defunct_error(self):
        if session.devices.get(self.name) == self:
            return DefunctDevice('SECoP device %s no longer available'
                                 % self.name)
        return DefunctDevice('refers to a replaced defunct SECoP device %s'
                             % self.name)

    @usermethod
    def hwread(self, param='value', maxage=0):
        """read from hw or get from secnode cache, depending on maxage

        :param param: a parameter, 'value' (default) or 'status'
        :param maxage: do not read when SECoP timestamp is more recent than
                       indicated by maxage
        :return: the validated value, after doRead<param> machinery
        """
        if self._sim_intercept:
            return self._cache.get(self, param, None)
        try:
            return self._read(param, maxage, True)
        finally:
            self._cache_update(param)

    def _read(self, param, maxage=0, fromhw=True):
        """read from hw or get from secnode cache

        :param param: a parameter name, 'value' or 'status'
        :param maxage: do not read when SECoP timestamp is more recent than
                       indicated by maxage
        :param fromhw: whether to read from HW or not
                       None: called from .status() or .read():
                       depends on secnode.async_only
        :return: the validated value
        """
        try:
            validator = self._maintypes.get(param) or self.parameters[param].type
        except KeyError:
            raise KeyError(f'{param} is no parameter') from None
        try:
            secnode = self._attached_secnode._secnode
        except AttributeError:
            raise self._defunct_error() from None
        if not secnode.online:
            raise CommunicationError('no SECoP connection')
        if maxage is None:
            fromhw = False
        elif fromhw is None and not self._attached_secnode.async_only:
            fromhw = True
        value, timestamp, readerror = secnode.cache[self.secop_module, param]
        if fromhw and time.time() > (timestamp or 0) + maxage:
            with self._read_lock:
                if not self._inside_read:
                    # this thread is not yet inside calling getParameter
                    self._inside_read = True
                    try:
                        self._pending_updates = {}
                        value = secnode.getParameter(self.secop_module, param)[0]
                    finally:
                        todo = self._pending_updates
                        self._pending_updates = {}
                        self._inside_read = False
                    # updating the cache for pending updates
                    # respecting overridden methods from mixins
                    todo.pop(param, None)  # this is handled by the caller
                    for pname in todo:
                        self._cache_update(pname)

        if readerror:
            raise make_nicos_error(readerror) from None
        try:
            return validator(value)
        except Exception:
            self.log.exception('can not set %r to %r', param, value)
            raise

    def _write(self, param, value):
        try:
            self._attached_secnode._secnode.setParameter(self.secop_module,
                                                         param, value)
            return value
        except AttributeError:
            raise self._defunct_error() from None

    def _call(self, cname, argument=None):
        return self._attached_secnode._secnode.execCommand(
            self.secop_module, cname, argument)[0]

    def setDefunct(self):
        if self._defunct:
            self.log.warning('device is already defunct')
            return
        self._defunct = True
        if self._attached_secnode is not None:
            session.configured_devices.pop(self.name, None)
            self._attached_secnode.unregisterDevice(self)
            # make defunct
            secnode = self._adevs.pop('secnode', None)
            if secnode:
                secnode._sdevs.discard(self._name)
            self._attached_secnode = None
            self._cache = None
        self.updateStatus()

    def setAlive(self, secnode):
        self._defunct = False
        self._cache = secnode._cache
        self._attached_secnode = secnode
        self._adevs.update({'secnode': secnode})
        secnode._sdevs.add(self._name)
        secnode.registerDevice(self)
        # clear defunct status
        self.updateStatus()

    def doShutdown(self):
        if not self._defunct:
            self.setDefunct()

    def connectionStatus(self):
        if not self._attached_secnode:
            return status.ERROR, 'defunct'
        if not self._attached_secnode._secnode.online:
            return status.ERROR, 'no SECoP connection'
        return None

    def paramWarning(self):
        n = len(self._param_errors)
        if n == 1:
            param, exc = list(self._param_errors.items())[0]
            return status.WARN, f'param {param}: {exc}'
        return status.WARN, f'errors in {n} parameters: see {self.name}.showerrors()'

    def doStatus(self, maxage=0):
        st = self.connectionStatus()
        if st:
            return st
        if self._param_errors:
            return self.paramWarning()
        return status.OK, ''

    @usermethod
    def status(self, maxage=None):
        """simple replacement for Readable.status

        not inherited from SecopReadable. we have to implement it here,
        as it is called in SecopDevice._cache_update
        """
        if self._sim_intercept:
            return status.OK, 'simulated ok'
        return self._getFromCache('status', self.doStatus, maxage)

    def showerrors(self):
        for param, exc in self._param_errors.items():
            prefix = '' if param in str(exc) else f'{param}: '
            session.log.info('%s.%s%s: %s', self.name, prefix, get_exc_name(exc), exc)

    def updateStatus(self):
        """status update without SECoP read in async_only mode"""
        self._cache_update('status')

    def setConnected(self, connected):
        if connected:
            self._param_errors.clear()  # clear errors from previous connection
        else:
            if self._cache:
                self._cache.clear(self, ['status'])  # clear all except status
        self.updateStatus()

    def register_callback(self, parameter, f):
        """Register a callback for parameter updates.

        The function is executed every time the client receives a new value for
        the given parameter..
        """
        self._attached_secnode.register_custom_callback(self.secop_module,
                                                        parameter, f)

    def unregister_callback(self, parameter, f):
        """Unregister a callback for parameter updates."""
        self._attached_secnode.unregister_custom_callback(self.secop_module,
                                                          parameter, f)


STATUS_MAP = {
    # division by 100: merge SECoP substates
    StatusType.DISABLED // 100: status.DISABLED,
    StatusType.IDLE // 100: status.OK,
    StatusType.WARN // 100: status.WARN,
    StatusType.BUSY // 100: status.BUSY,
    StatusType.ERROR // 100: status.ERROR,
}


class SecopReadable(SecopDevice, Readable):
    """Represent a SECoP "Readable"."""
    parameter_overrides = {
        # do not force to give unit in setup file
        # (take from SECoP description)
        'unit': Override(default='', mandatory=False),
        # pollinterval is unused as polling is done remotely
        # may be overridden by the SECoP pollinterval
        'pollinterval': Override(default=None, userparam=False, settable=False),
        # calculated to be slightly higher than maxage on the attached SecNodeDevice
        'maxage': Override(default=3600, userparam=False, settable=False, volatile=True),
    }

    def status(self, maxage=None):
        # do not use SecopDevice.status here
        return Readable.status(self, maxage)

    def doRead(self, maxage=0):
        try:
            return self._read('value', maxage, None)
        except NicosError:
            st = self.doStatus(0)
            if st[0] == status.DISABLED:
                raise NicosError('disabled') from None
            raise

    def doReset(self):
        try:
            self._call('reset')
        except KeyError:
            try:
                self.clear_errors()
            except AttributeError:
                pass

    def doStatus(self, maxage=0):
        st = self.connectionStatus()
        if st:
            return st
        try:
            code, text = self._read('status', maxage, None)
            # code is a SECoP status code here (StatusType.<name> below)
        except NicosError as e:
            return status.ERROR, str(e)
        if StatusType.FINALIZING <= code < StatusType.ERROR:
            return status.OK, text
        if self._param_errors and code != StatusType.DISABLED:
            exc = self._param_errors.get('value')
            if exc and code < StatusType.BUSY:  # error reading value and status IDLE or WARN
                return status.ERROR, f'can not read value: {get_exc_name(exc)} - {exc}'
            if code < StatusType.WARN:  # error in any other parameter and status IDLE
                return self.paramWarning()
        # treat SECoP code 401 (unknown) as error - should be distinct from
        # NICOS status unknown
        return STATUS_MAP.get(code // 100, status.UNKNOWN), text

    def doReadMaxage(self):
        sn = self._attached_secnode
        # maxage should be a little above the value used in poll thread
        return (sn.maxage or 600) + len(sn._polled_devs) * 2

    def showerrors(self):
        st = self.status()
        if st[0] == status.ERROR:
            session.log.info('%s.status(): %s', self.name, st[1])
        super().showerrors()

    def info(self):
        # override the default NICOS behaviour here:
        # a disabled SECoP module should be ignored silently
        st = self.status(0)
        if st[0] == status.DISABLED:
            # do not display info in data file when disabled
            return []
        exc = self._param_errors.get('value')
        if exc is not None:
            # avoid calling read(), as it would fail
            return [
                DeviceMetaInfo(
                    'value',
                    DeviceParInfo(None, f'Error: {exc}', '', 'general')),
                DeviceMetaInfo(
                    'status',
                    DeviceParInfo(st, formatStatus(st), '', 'status'))]
        return Readable.info(self)


class SecopWritable(SecopReadable, Moveable):
    """Represent the SECoP "Writable"."""

    def doReadTarget(self):
        try:
            return self._read('target', None)
        except NicosError:
            # this might happen when the target is not initialized
            # if we do not catch here, Moveable.start will raise
            # when comparing with the previous value
            return None

    def doStart(self, target):
        try:
            self._attached_secnode._secnode.setParameter(
                self.secop_module, 'target', target)
        except AttributeError:
            raise self._defunct_error() from None

    def _getWaiters(self):
        """do not return attached secnode"""
        return {k: v for k, v in self._adevs.items() if k != 'secnode'}


class SecopMoveable(SecopWritable):
    """Represent the SECoP "Drivable"."""

    def doStop(self):
        if self.doStatus()[0] == status.BUSY:
            try:
                self._attached_secnode._secnode.execCommand(
                    self.secop_module, 'stop')
            except Exception:
                self.log.exception('error while stopping')
                self.updateStatus()


class SecopHasOffset(HasOffset):
    """Modified HasOffset mixin.

    goal: make the class to be accepted by the adjust command
    """
    parameter_overrides = {
        'offset': Override(prefercache=True, volatile=True),
    }

    def doRead(self, maxage=0):
        return super().doRead() - self.offset

    def doReadTarget(self):
        raw = super().doReadTarget()
        return None if raw is None else super().doReadTarget() - self.offset

    def doStart(self, value):
        super().doStart(value + self.offset)

    def doWriteOffset(self, value):
        super().doWriteOffset(value)
        # remark: possible adjustments of limits, targets have to be done
        # in the remote implementation
        self._write('offset', value)


class SecopHasLimits(HasLimits):
    """treat target_max and/or target_min

    accept also target_limits (intermediate draft spec)
    """
    parameter_overrides = {
        'abslimits': Override(prefercache=True, mandatory=False,
                              volatile=True),
        'userlimits': Override(volatile=True),
        # only some of the following parameters are available,
        # but nicos does not complain about superfluous overrides
        'target_limits': Override(userparam=False),
        'target_min': Override(userparam=False),
        'target_max': Override(userparam=False),
    }

    def doReadAbslimits(self):
        dt = self._config.get('target_datainfo', {})
        return dt.get('min', float('-inf')), dt.get('max', float('inf'))

    def doReadUserlimits(self):
        if hasattr(self, 'target_limits'):
            min_, max_ = self.target_limits
        else:
            min_ = getattr(self, 'target_min', float('-inf'))
            max_ = getattr(self, 'target_max', float('inf'))
        offset = self.offset if isinstance(self, SecopHasOffset) else 0
        return min_ - offset, max_ - offset

    def _adjustLimitsToOffset(self, value, diff):
        """not needed, as limits are calculated from SECoP parameters"""

    def doWriteUserlimits(self, value):
        super().doWriteUserlimits(value)
        offset = self.offset if isinstance(self, SecopHasOffset) else 0
        min_ = value[0] + offset
        max_ = value[1] + offset
        if hasattr(self, 'target_limits'):
            self.target_limits = min_, max_
        if hasattr(self, 'target_min'):
            self.target_min = min_
        else:  # silently replace with abslimits
            min_ = self.abslimits[0]
        if hasattr(self, 'target_max'):
            self.target_max = max_
        else:
            max_ = self.abslimits[1]
        return min_ - offset, max_ - offset


IF_CLASSES = {
    'Drivable': SecopMoveable,
    'Writable': SecopWritable,
    'Readable': SecopReadable,
    'Module': SecopDevice,
}

ALL_IF_CLASSES = set(IF_CLASSES.values())

FEATURES = {
    'HasOffset': SecopHasOffset,
}
