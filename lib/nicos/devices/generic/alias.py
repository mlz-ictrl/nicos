#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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

"""Generic device classes using hardware-specific attached devices."""

import re

from nicos import session
from nicos.core import Device, Param, ConfigurationError, NicosError, none_or, \
     usermethod


class NoDevice(object):

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return '<none>'

    def __getattr__(self, name):
        raise ConfigurationError('alias %r does not point to any device' % self.name)

    def __setattr__(self, name, value):
        if name != 'name':
            raise ConfigurationError('alias %r does not point to any device' % self.name)
        object.__setattr__(self, name, value)


class DeviceAlias(Device):
    """
    Generic "alias" device that can point all access to any other NICOS device.

    The device that should be accessed is set using the "alias" parameter, which
    can be configured and changed at runtime.  For example, with a DeviceAlias
    instance *T*::

        T.alias = Tcryo
        read(T)   # will read Tcryo
        T.alias = Toven
        read(T)   # will read Toven

    This allows to call e.g. the sample temperature by the same name in all
    sample environment setups, but behind the scenes implement it using
    different actual hardware devices.

    If the "alias" parameter is empty, the alias points to a special "NoDevice"
    object that raises a `ConfigurationError` on every access.
    """

    parameters = {
        'alias':    Param('Device to alias', type=none_or(str), settable=True,
                          chatty=True),
        'devclass': Param('Class name that the aliased device must be an '
                          'instance of', type=str, default='nicos.core.Device'),
    }

    _ownattrs = ['_obj', '_mode', '_cache', 'alias']
    _ownparams = set(['alias', 'name', 'devclass'])
    _initialized = False

    def __init__(self, name, **config):
        self._obj = None
        devclass = config.get('devclass', 'nicos.core.Device')
        try:
            modname, clsname = devclass.rsplit('.', 1)
            self._cls = session._nicos_import(modname, clsname)
        except Exception:
            self.log.warning('could not import class %r; using Device as the '
                             'alias devclass', exc=1)
            self._cls = Device
        Device.__init__(self, name, **config)
        self._initialized = True

    def doUpdateAlias(self, devname):
        if not devname:
            self._obj = NoDevice(str(self))
            if self._cache:
                self._cache.unsetRewrite(str(self))
                self._reinitParams()
        else:
            try:
                newdev = session.getDevice(devname, (self._cls, DeviceAlias),
                                           source=self)
            except NicosError:
                if not self._initialized:
                    # should not raise an error, otherwise the device cannot
                    # be created at all
                    self.log.warning('could not find aliased device %s, pointing '
                                     'to nothing for now' % devname)
                    newdev = None
                else:
                    raise
            if newdev is self:
                raise NicosError(self, 'cannot set alias pointing to itself')
            if newdev != self._obj:
                self._obj = newdev
                if self._cache:
                    self._cache.setRewrite(str(self), devname)
                    self._reinitParams()

    def _reinitParams(self):
        if self._mode != 'master':  # only in the copy that changed the alias
            return
        # clear all cached parameters
        self._cache.clear(str(self), exclude=self._ownparams)
        # put the parameters from the original device in the cache under the
        # name of the alias
        if not isinstance(self._obj, Device):
            return
        for pname in self._obj.parameters:
            if pname in self._ownparams:
                continue
            self._cache.put(self, pname, getattr(self._obj, pname))

    # Device methods that would not be alias-aware

    def valueInfo(self):
        # override to replace name of the aliased device with the alias' name
        new_info = []
        rx = r'^%s\b' % re.escape(self._obj.name)
        for v in self._obj.valueInfo():
            new_v = v.copy()
            # replace dev name, if at start of value name, with alias name
            new_v.name = re.sub(rx, self.name, v.name)
            new_info.append(new_v)
        return tuple(new_info)

    @usermethod
    def info(self):
        # override to use the object's "info" but add a note about the alias
        if isinstance(self._obj, Device):
            for v in self._obj.info():
                yield v
        yield ('instrument', 'alias', str(self._obj))

    @usermethod
    def version(self):
        v = []
        if isinstance(self._obj, Device):
            v = self._obj.version()
        v.extend(Device.version(self))
        return v

    # these methods must not be proxied

    def __eq__(self, other):
        return self is other

    def __ne__(self, other):
        return self is not other

    # generic proxying of missing attributes to the object

    def __getattr__(self, name):
        if not self._initialized:
            raise AttributeError(name)
        else:
            return getattr(self._obj, name)

    def __setattr__(self, name, value):
        if name in DeviceAlias._ownattrs or not self._initialized:
            object.__setattr__(self, name, value)
        else:
            setattr(self._obj, name, value)

    def __delattr__(self, name):
        if name in DeviceAlias._ownattrs or not self._initialized:
            object.__delattr__(self, name)
        else:
            delattr(self._obj, name)


# proxying of special methods to the object

def make_method(name):
    def method(self, *args, **kw):
        return getattr(self._obj, name)(*args, **kw)
    return method

for name in [
        '__abs__', '__add__', '__and__', '__call__', '__cmp__', '__coerce__',
        '__contains__', '__delitem__', '__delslice__', '__div__', '__divmod__',
        '__float__', '__floordiv__', '__ge__', '__getitem__',
        '__getslice__', '__gt__', '__hash__', '__hex__', '__iadd__', '__iand__',
        '__idiv__', '__idivmod__', '__ifloordiv__', '__ilshift__', '__imod__',
        '__imul__', '__int__', '__invert__', '__ior__', '__ipow__', '__irshift__',
        '__isub__', '__iter__', '__itruediv__', '__ixor__', '__le__', '__len__',
        '__long__', '__lshift__', '__lt__', '__mod__', '__mul__',
        '__neg__', '__oct__', '__or__', '__pos__', '__pow__', '__radd__',
        '__rand__', '__rdiv__', '__rdivmod__', '__reduce__', '__reduce_ex__',
        '__reversed__', '__rfloorfiv__', '__rlshift__', '__rmod__',
        '__rmul__', '__ror__', '__rpow__', '__rrshift__', '__rshift__', '__rsub__',
        '__rtruediv__', '__rxor__', '__setitem__', '__setslice__', '__sub__',
        '__truediv__', '__xor__', 'next',
    ]:
    if hasattr(Device, name):
        setattr(DeviceAlias, name, make_method(name))
