#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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

A SecNodeDevice is connected to a SecNode by assigning the uri value, this can
be done at any time. With auto_create == True, all devices are created automatically
after connections, and they are altered on reconnection.

For a setup for permanent use, with auto_create == False (the default), the devices
are to be created with the class SecopDevice, SecopReadable or SecopMoveable, and the
following parameters:
secnode: the secnode device name
secop_module: the name of the remotely connected SECoP module
params_cfg (optional): a dict {<parameter name>: <cfg dict>}
   if given, only the parameters mentioned as keys are exported.
   The cfg dict may be empty for using the automatically generated attributes:
   description, type, settable, unit and fmtstr.
   Attributes given in the cfg dict may overwrite above attributes.
"""

from __future__ import absolute_import, division, print_function

import re
import time
from collections import OrderedDict
from math import floor, log10
from threading import Event

from nicos import session
from nicos.core import MASTER, SIMULATION, Attach, DeviceAlias, Override, Param, \
    status, usermethod
from nicos.core.device import DeviceMeta, Moveable, Readable
from nicos.core.errors import ConfigurationError
from nicos.core.params import anytype, dictwith, floatrange, intrange, \
    listof, nonemptylistof, nonemptystring, oneofdict, string, tupleof
from nicos.utils import printTable

# TODO: Secop supports only py3 !!! Pylint is running with py2 on Jenkins
import secop.modules  # pylint: disable=import-error
from secop.client import SecopClient  # pylint: disable=import-error
# pylint: disable=import-error
from secop.datatypes import FloatRange, ScaledInteger
# pylint: disable=import-error
from secop.errors import CommunicationFailedError

SecopStatus = secop.modules.Drivable.Status

IFCLASSES = {
   'Drivable': 'SecopMoveable',
   'Writable': 'SecopMoveable',  # Writable does not exist in NICOS
   'Readable': 'SecopReadable',
   'Module': 'SecopDevice',
}


class DefunctDevice(Exception):
    pass


def clean_identifier(anystring):
    return str(re.sub(r'\W+|^(?=\d)','_', anystring))


def get_validator_dict():
    """convert SECoP datatype into NICOS validator

    returns the python code of an equivalent NICOS validator for the SECoP datatype
    """
    # use leading underscore to avoid conflicts with built-ins

    def _double(min=None, max=None, **kwds):  # pylint: disable=redefined-builtin
        if max is None:
            if min is None:
                return float
            return floatrange(min)
        return floatrange("float('-inf')" if min is None else min, max)

    def _int(min=None, max=None, **kwds):  # pylint: disable=redefined-builtin
        # be tolerant with missing min / max here
        if max is None:
            if min is None:
                return int
            return intrange(min, 1<<64)
        return intrange(-1<<64 if min is None else min, max)

    def _bool(**kwds):
        return bool

    def _blob(minbytes=0, **kwds):
        # ignore maxbytes and minbytes > 1
        return nonemptystring if minbytes else string

    def _string(minchars=0, **kwds):
        # ignore maxchars and minchars > 1
        return nonemptystring if minchars else string

    def _enum(members, **kwds):
        # do not use oneof here, as in general numbers are relevant for the specs
        # use ordered dict here: indicates that the given order would be preferred for a GUI
        # TODO: nicos.guisupport.typedvalue should be modified to keep the order for combo box
        return oneofdict(OrderedDict(sorted(((v, k) for k, v in members.items()))))

    def _array(members, minlen=0, **kwds):
        # ignore maxlen and minlen > 1
        members = get_validator(**members)
        return nonemptylistof(members) if minlen else listof(members)

    def _tuple(members, **kwds):
        return tupleof(*(get_validator(**m) for m in members))

    def _struct(members, **kwds):
        # ignore 'optional' property
        return dictwith(**{n: get_validator(**m) for n, m in members})

    def _command(argument=None, result=None, **kwds):
        # not yet implemented
        return None

    # return dict of functions with stripped keys
    return {key[1:]: func for key, func in locals().items()}


DATATYPE_TO_VALIDATOR = get_validator_dict()


def get_validator(type, **kwds):  # pylint: disable=redefined-builtin
    return DATATYPE_TO_VALIDATOR[type](**kwds)


def get_aliases(dev):
    """get devices aliased to on dev

    return a list containing for each alias a tuple (device, required class).
    """
    # check that the new class fits the required classes on devices self is attached to
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


class SecNodeDevice(Readable):
    """SEC node device

    want to have a status -> based on Readable
    """

    parameters = {
        'prefix': Param("Prefix for the generated devices\n\n'$' will be replaced by the equipment id",
                        type=str, default='$_', settable=True),
        'uri': Param('tcp://<host>:<port>', type=str, settable=True),
        'auto_create': Param('flag for automatic creation of devices', type=bool,
                             settable=False, prefercache=False, default=False, userparam=False),
        'setup_info': Param('setup info', type=anytype, default={}, settable=True),
    }
    parameter_overrides = {
        'unit': Override(default='', mandatory=False),
    }

    valuetype = str
    _secnode = None
    _value = ''
    _status = status.OK, 'unconnected'
    _devices = {}

    def doPreinit(self, mode):
        self._devices = {}

    def doInit(self, mode):
        if mode == MASTER:
            if self.uri:
                try:
                    self._connect()
                except Exception:
                    pass
        elif mode == SIMULATION:
            setup_info = self.get_setup_info()
            if self.auto_create:
                self.makeDynamicDevices(setup_info)
            else:
                self._setROParam('setup_info', setup_info)

    def get_setup_info(self):
        if self._mode == SIMULATION:
            db = session.getSyncDb()
            return db.get('%s/setup_info' % self.name.lower())
        return self.setup_info

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
        self._setROParam('uri', value)  # make sure uri is set before reconnect
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
        self._secnode = SecopClient(self.uri, log=self.log)
        self._secnode.register_callback(None, self.nodeStateChange, self.descriptiveDataChange)
        try:
            self._secnode.connect()
            self._set_status(status.OK, 'connected')
            self.createDevices()
            return
        except Exception as e:
            if not isinstance(e, CommunicationFailedError):
                raise
            self.log.warning('can not connect to %s (%s), retry in background' % (self.uri, e))
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
        """called when descriptive data changed after an automatic reconnection"""
        self.log.warning('node description changed')
        self.createDevices()

    def get_status(self, online, state):
        if not online:
            return status.ERROR, state
        return status.OK if state == 'connected' else status.WARN, state

    def nodeStateChange(self, online, state):
        """called when the state of the connection changes

        'online' is True when connected or reconnecting, False when disconnected or connecting
        'state' is the connection state as a string
        """
        if online and state == 'connected':
            self._set_status(status.OK, 'connected')
        elif not online:
            self._set_status(status.ERROR, 'reconnecting')
            for device in self._devices.values():
                device.updateSecopStatus((400, 'disconnected'))
        else:
            self._set_status(status.WARN, state)

    def doShutdown(self):
        self._disconnect()
        if self._devices:
            self.log.error('can not remove devices %r' % list(self._devices))

    def _get_prefix(self):
        if not self._secnode:
            return None
        equipment_name = clean_identifier(self._secnode.nodename).lower()
        return self.prefix.replace('$', equipment_name)

    @usermethod
    def showModules(self):
        """show modules of the connected SECoP server

        and intended devices names using the given prefix
        """
        prefix = self._get_prefix()
        if prefix is None:
            self.log.error('secnode is not connected')
            return
        items = [(prefix + m, m, mod_desc.get('properties', {}).get('description', '').split('\n')[0])
                 for m, mod_desc in self._secnode.modules.items()]
        printTable(['foreseen device name', 'SECoP module', 'description'], items, self.log.info)

    def registerDevice(self, device):
        if not self._secnode:
            raise IOError('unconnected')
        self.log.debug('register %s on %s' % (device, self))
        self._devices[device.name] = device
        module = device.secop_module
        if module not in self._secnode.modules:
            raise ConfigurationError('no module %r found on this SEC node' % module)
        for parameter in self._secnode.modules[module]['parameters']:
            updatefunc = getattr(device, '_update_' + parameter, device._update)
            self._secnode.register_callback((module, parameter), updateEvent=updatefunc)
            try:
                data = self._secnode.cache[module, parameter]
                if data:
                    updatefunc(module, parameter, *data)
                else:
                    self.log.warning('No data for %s:%s' % (module, parameter))
            except KeyError:
                self.log.warning('No cache for %s:%s' % (module, parameter))

    def unregisterDevice(self, device):
        self.log.debug('unregister %s from %s' % (device, self))
        session.configured_devices.pop(device.name, None)
        if self._devices.pop(device.name, None) is None:
            self.log.info('device %s already removed' % device.name)
            return
        module = device.secop_module
        try:
            moddesc = self._secnode.modules[module]
        except KeyError:  # do not complain again about missing module
            return
        for parameter in moddesc['parameters']:
            updatefunc = getattr(device, '_update_' + parameter, device._update)
            self._secnode.unregister_callback((module, parameter), updateEvent=updatefunc)

    def createDevices(self):
        """create drivers and devices

        for the devices to be created from the connected SECoP server
        """
        if not self._secnode:
            self.log.error('secnode is not connected')
            return
        modules = self._secnode.modules
        prefix = self._get_prefix()
        setup_info = {}
        for module, mod_desc in modules.items():
            params_cfg = {}
            module_properties = mod_desc.get('properties', None)
            for ifclass in (module_properties.get('interface_classes', []) or
                            module_properties.get('interface_class', [])):
                try:
                    clsname = IFCLASSES[ifclass.title()]
                    break
                except KeyError:
                    continue
            else:
                clsname = 'SecopDevice'
            kwds = {}
            for pname, props in mod_desc['parameters'].items():
                datatype = props['datatype']
                typ = get_validator(**datatype.export_datatype())
                pargs = dict(type=typ, description=props['description'])
                if not props.get('readonly', True) and pname != 'target':
                    pargs['settable'] = True
                unit = ''
                fmtstr = None
                if isinstance(datatype, FloatRange):
                    fmtstr = getattr(datatype, 'fmtstr', '%g')
                    unit = getattr(datatype, 'unit', '')
                elif isinstance(datatype, ScaledInteger):
                    fmtstr = getattr(datatype, 'fmtstr',
                                     '%%%df' % max(0, -floor(log10(props['scale']))))
                    unit = getattr(datatype, 'unit', '')
                if unit:
                    pargs['unit'] = unit
                if pname == 'status':
                    continue
                if pname == 'value':
                    try:
                        kwds['unit'] = datatype.unit
                    except AttributeError:
                        pass
                    if fmtstr is not None:
                        kwds['fmtstr'] = fmtstr
                    else:
                        kwds['fmtstr'] = '%r'
                    kwds['maintype'] = typ
                    continue
                if pname == 'target':
                    kwds['valuetype'] = typ
                if fmtstr is not None and fmtstr != '%g':
                    pargs['fmtstr'] = fmtstr
                params_cfg[pname] = pargs
            if clsname != 'SecopDevice':
                kwds.setdefault('unit', '')  # unit is mandatory on Readables
            desc = dict(secnode=self.name,
                        description=mod_desc.get('properties', {}).get('description', ''),
                        secop_module=module,
                        params_cfg=params_cfg,
                        **kwds)
            setup_info[prefix + module] = ('nicos.devices.secop.%s' % clsname, desc)
        if not setup_info:
            self.log.info('creating devices for %s skipped' % self.name)
            return
        if self.auto_create:
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
                if not isinstance(dev, SecopDevice) or (dev._attached_secnode and
                                                        dev._attached_secnode != self):
                    self.log.error('device %s already exists' % devname)
                    continue
                base = dev.__class__.__bases__[0]
                prevcfg = base.__module__ + '.' + base.__name__, dict(secnode=self.name, **dev._config)
            else:
                prevcfg = None
            if prevcfg != devcfg:
                session.configured_devices[devname] = devcfg
                session.dynamic_devices[devname] = setupname  # pylint: disable=undefined-loop-variable
                if dev is None:
                    # add new device
                    session.createDevice(devname, recreate=True, explicit=True)
                    dev = session.devices[devname]
                else:
                    # modify existing device
                    if dev._attached_secnode:
                        dev._attached_secnode.unregisterDevice(dev)
                    session.configured_devices[devname] = devcfg
                    session.dynamic_devices[devname] = setupname  # pylint: disable=undefined-loop-variable
                    try:
                        dev.replaceClass(devcfg[1])
                        dev.setAlive(self)
                    except ConfigurationError:
                        # above failed because an alias or attaching device requires a specific class
                        # make old device defunct and replace by a new device
                        session.destroyDevice(dev)
                        session.dynamic_devices.pop(devname, None)
                        session.createDevice(devname, recreate=True, explicit=True)
                        prevdevices.discard(devname)
                        dev = session.devices[devname]
                if not isinstance(dev, SecopReadable):
                    # we will not get status updates for these
                    dev.updateSecopStatus((SecopStatus.IDLE, ''))

        defunct = set()
        # defunct devices no longer available
        for devname in prevdevices:
            dev = session.devices.get(devname)
            if dev is None or dev._attached_secnode != self:
                continue
            if dev._sdevs:
                self.log.warning('defunct device is attached to %s' % ', '.join(dev._sdevs))
            dev.setDefunct()
            defunct.add(devname)

        # inform client that setups have changed
        session.setupCallback(list(session.loaded_setups), list(session.explicit_setups))


class SecopDevice(Readable):
    # based on Readable instead of Device, as we want to have a status
    attached_devices = {
        'secnode': Attach('sec node', SecNodeDevice),
    }
    parameters = {
        'secop_module': Param('SECoP module', type=str, settable=False, userparam=False),
    }
    parameter_overrides = {
        # do not force to give unit in setup file (take from SECoP description)
        'unit': Override(default='', mandatory=False),
    }
    _status = (SecopStatus.ERROR, 'disconnected')
    STATUS_MAP = {
        0: status.DISABLED,
        1: status.OK,
        2: status.WARN,
        3: status.BUSY,
        4: status.ERROR,
    }
    _maintype = staticmethod(anytype)
    _defunct = False

    @classmethod
    def makeDevClass(cls, name, **config):
        """create a class with the needed doRead/doWrite methods

        for accessing the assigned SECoP module
        """
        secnodedev = session.getDevice(config['secnode'])
        # make a copy, as we will modify later
        params_override = config.pop('params_cfg', None)
        setup_info = secnodedev.get_setup_info()
        if name in setup_info:
            devcfg = dict(setup_info[name][1])
            params_cfg = devcfg.pop('params_cfg')
        else:
            devcfg, params_cfg = {}, {}
        if params_override is not None:
            params_cfg = dict(params_cfg)
            for pname, pold in list(params_cfg.items()):
                pnew = params_override.get(pname)
                if pnew is not None:
                    params_cfg[pname] = dict(pold, **pnew)
                elif pname not in cls.parameters:
                    params_cfg.pop(pname)  # remove parameters not mentioned
        devcfg.update(config)

        parameters = {}
        # create parameters and methods
        attrs = dict(parameters=parameters, __module__=cls.__module__)
        if 'valuetype' in config:
            # this is in fact the target value type
            attrs['valuetype'] = config.pop('valuetype')
        if 'maintype' in config:
            attrs['_maintype'] = staticmethod(config.pop('maintype'))
        for pname, kwargs in params_cfg.items():
            typ = kwargs['type']
            if 'fmtstr' not in kwargs and (typ is float or isinstance(typ, floatrange)):
                # the fmtstr default differs in SECoP and NICOS
                kwargs = dict(kwargs, fmtstr='%g')  # copy kwargs as it may be read only
            parameters[pname] = Param(volatile=True, **kwargs)

            def do_read(self, maxage=None, pname=pname, validator=typ):
                return self._read(pname, maxage, validator)

            attrs['doRead%s' % pname.title()] = do_read

            if kwargs.get('settable', False):
                def do_write(self, value, pname=pname, validator=typ):
                    return self._write(pname, value, validator)

                attrs['doWrite%s' % pname.title()] = do_write

        classname = cls.__name__ + '_' + name
        # create a new class extending SecopDevice, apply DeviceMeta in order to
        # include the added parameters
        newclass = DeviceMeta.__new__(DeviceMeta, classname, (cls,), attrs)  # pylint: disable=too-many-function-args
        newclass._modified_config = devcfg  # store temporarily for __init__
        return newclass

    def __new__(cls, name, **config):
        """called when an instance of the class is created but before __init__

        instead of returning a SecopDevice, we create an object of an extended class here
        """
        newclass = cls.makeDevClass(name, **config)
        return Readable.__new__(newclass)

    def __init__(self, name, **config):
        """apply modified config"""
        Readable.__init__(self, name, **self._modified_config)
        del self.__class__._modified_config

    def replaceClass(self, config):
        """replace the class on the fly

        happens when the structure fo the device has changed
        """
        cls = self.__class__.__bases__[0]
        newclass = cls.makeDevClass(self.name, **config)
        bad_attached = False
        for dev, cls in get_attaching_devices(self):
            if issubclass(newclass, cls):
                self.log.warning('reattach %s to %s' % (dev.name, self.name))
            else:
                self.log.error('can not attach %s to %s' % (dev.name, self.name))
                bad_attached = True
        if bad_attached:
            raise ConfigurationError('device class mismatch')
        for dev, cls in get_aliases(self):
            if issubclass(newclass, cls):
                self.log.warning('redirect alias %s to %s' % (dev.name, self.name))
            else:
                self.log.error('release alias %s from %s' % (dev.name, self.name))
                dev.alias = ''
        self.__class__ = newclass
        # as we do not go through self.__init__ again, we have to update self._config
        self._config = dict((name.lower(), value) for (name, value) in config.items())
        for aname in self.attached_devices:
            self._config.pop(aname, None)

    def doPreinit(self, mode):
        if mode != SIMULATION:
            self._attached_secnode.registerDevice(self)

    def _update(self, module, parameter, value, timestamp, readerror):
        if parameter not in self.parameters:
            return
        if readerror:
            return  # do not know how to indicate an error on a parameter
        try:
            # ignore timestamp for now
            self._setROParam(parameter, value)
        except Exception as err:
            self.log.error(repr(err))
            self.log.error('can not set %s:%s to %r' % (module, parameter, value))

    def _raise_defunct(self):
        if session.devices.get(self.name) == self:
            raise DefunctDevice('SECoP device %s no longer available' % self.name)
        raise DefunctDevice('refers to a replaced defunct SECoP device %s' % self.name)

    def _read(self, param, maxage, validator):
        try:
            secnode = self._attached_secnode._secnode
        except AttributeError:
            self._raise_defunct()
        value, timestamp, _ = secnode.cache[self.secop_module, param]
        if maxage is not None and time.time() > (timestamp or 0) + maxage:
            value = secnode.getParameter(self.secop_module, param)[0]
        if value is not None:
            value = validator(value)
        return value

    def _write(self, param, value, validator):
        try:
            value = validator(value)
            self._attached_secnode._secnode.setParameter(self.secop_module, param, value)
            return value
        except AttributeError:
            self._raise_defunct()

    def setDefunct(self):
        if self._defunct:
            self.log.error('device is already defunct')
            return
        self.updateSecopStatus((SecopStatus.ERROR, 'defunct'))
        self._defunct = True
        if self._attached_secnode is not None:
            self._attached_secnode.unregisterDevice(self)
            # make defunct
            self._attached_secnode = None
            self._cache = None

    def setAlive(self, secnode):
        self._defunct = False
        self._cache = secnode._cache
        self._attached_secnode = secnode
        secnode.registerDevice(self)
        # clear defunct status
        self.updateSecopStatus((SecopStatus.IDLE, ''))

    def doShutdown(self):
        if not self._defunct:
            self.setDefunct()

    def doRead(self, maxage=0):
        """dummy, as there is no value"""
        return ''

    def updateSecopStatus(self, value):
        """update status from SECoP status value"""
        self._status = value
        if self._cache:
            self._cache.put(self, 'status', self.doStatus())

    def _update_status(self, module, parameter, value, timestamp, readerror):
        if value is not None:
            self.updateSecopStatus(tuple(value))

    def doStatus(self, maxage=0):
        code, text = self._status
        if 390 <= code < 400:  # SECoP status finalizing
            return status.OK, text
        # treat SECoP code 401 (unknown) as error - should be distinct from NICOS status unknown
        return self.STATUS_MAP.get(code // 100, status.UNKNOWN), text


class SecopReadable(SecopDevice):

    def doRead(self, maxage=0):
        return self._read('value', maxage, self._maintype)

    def _update_value(self, module, parameter, value, timestamp, readerror):
        if value is None:
            return
        if self._cache:
            try:
                # convert enum code to name
                value = self._maintype(value)
            except Exception:
                pass
            self._cache.put(self, 'value', value)


class SecopMoveable(SecopReadable, Moveable):

    def doStart(self, value):
        try:
            self._attached_secnode._secnode.setParameter(self.secop_module,
                                                         'target', value)
        except AttributeError:
            self._raise_defunct()

    def doStop(self):
        if self.status(0)[0] == status.BUSY:
            try:
                self._attached_secnode._secnode.execCommand(self.secop_module, 'stop')
            except Exception as e:
                self.log.error('error while stopping: ' + str(e))
                self.updateSecopStatus((200, 'error while stopping'))
