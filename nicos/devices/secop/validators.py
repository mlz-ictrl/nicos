#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2022 by the NICOS contributors (see AUTHORS)
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

"""SECoP specific validators/valuetypes."""

from collections import OrderedDict

from nicos.core.params import anytype, dictwith, floatrange, intrange, \
    listof, none_or, nonemptystring, oneofdict, string, tupleof
from nicos.utils import readonlydict


# map SECoP types to NICOS types:
# all types must either be vanilla NICOS types or inherit from them

# pylint: disable=redefined-builtin
def Secop_double(min=None, max=None, **kwds):
    if min is None and max is None:
        return float
    return floatrange("float('-inf')" if min is None else min, max)


# pylint: disable=redefined-builtin
def Secop_int(min=None, max=None, **kwds):
    # by the spec, min and max are mandatory in SECoP
    # an integer without limits is therefore indicated by big limits
    # 9999 is apparently big value, but not bigger than 2 ** 15
    # which might be a natural limit if the server side uses 16bit ints.
    # be tolerant with missing min / max here (future spec change?)
    if min <= -9999 and max >= 9999:
        return int
    return intrange(min, max)


def Secop_bool(**kwds):
    return bool


def Secop_string(minchars=0, **kwds):
    # unfortunately, 'string' is not a class, so we can not inherit from it
    # therefore ignore maxchars and minchars > 1
    return nonemptystring if minchars else string


def Secop_blob(minbytes=0, **kwds):
    # ignore maxbytes and minbytes > 1
    return nonemptystring if minbytes else string


class Secop_enum(oneofdict):
    def __init__(self, members, **kwds):
        # Do not use oneof here, as in general numbers are relevant for the
        # specs. Unfortunately, ComboBox will sort items by name, and not by
        # values, which IMO would be preferrable.
        # Eventually nicos.guisupport.typedvalue.ComboWidget should be changed
        # to keep the given order instead or sorting by name, at least when
        # vals is an OrderedDict ...
        oneofdict.__init__(
            self, OrderedDict(sorted(((v, k) for k, v in members.items()))))
        self.__doc__ = 'one of ' + ', '.join('%s, %d' % kv
                                             for kv in members.items())

    def __call__(self, val=None):
        if val is None:
            return next(iter(self.vals))
        return oneofdict.__call__(self, val)


class Secop_array(listof):
    def __init__(self, members, minlen=0, maxlen=None, **kwds):
        self.minlen = minlen
        self.maxlen = maxlen
        listof.__init__(self, get_validator(members))

    def __call__(self, val=None):
        if val is None:
            val = [self.conv()] * self.minlen
        result = listof.__call__(self, val)
        if len(result) < self.minlen:
            raise ValueError('value needs a length >= %d' % self.minlen)
        if self.maxlen is not None and len(result) > self.maxlen:
            raise ValueError('value needs a length <= %d' % self.maxlen)
        return result


def Secop_tuple(members, **kwds):
    return tupleof(*tuple(get_validator(m) for m in members))


class Secop_struct(dictwith):
    def __init__(self, members, optional=(), **kwds):
        convs = {k: get_validator(m) for k, m in members.items()}
        for key in optional:
            # missing optional items are indicated with a None value
            convs[key] = none_or(convs[key])
        self.optional = optional
        self.mandatorykeys = set(convs) - set(optional)
        dictwith.__init__(self, **convs)

    def __call__(self, val=None):
        if val is None:
            return {k: conv() for k, conv in self.convs.items()
                    if k in self.mandatorykeys}
        if not isinstance(val, dict):
            raise ValueError('value needs to be a dict')
        vkeys = set(val)
        msgs = []
        if vkeys - self.keys:
            msgs.append('unknown keys: %s' % ', '.join((vkeys - self.keys)))
        if self.mandatorykeys - vkeys:
            msgs.append('missing keys: %s' % ', '.join(self.mandatorykeys - vkeys))
        if msgs:
            raise ValueError('Key mismatch in dictionary: ' + ', '.join(msgs))
        ret = {}
        for k, conv in self.convs.items():
            ret[k] = conv(val.get(k))
        return readonlydict(ret)

    def write_validator(self, val=None):
        """special validator for writing"""
        val = self(val)
        if self.optional:
            # remove optional values which are None
            val = {k: v for k, v in val.items() if v is not None}
        return val


def get_validator(datainfo):
    if datainfo is None:
        return anytype
    return globals()['Secop_%s' % datainfo['type']](**datainfo)
