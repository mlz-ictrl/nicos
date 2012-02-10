#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************
''' A general nicos proxy superclass

'''

class NicosProxy(object):
    """
    general proxy class to add special behaviour to classes

    see: http://code.activestate.com/recipes/252151-generalized-delegates-and-proxies/
    """

    _obj = None
    def __init__(self,obj):
        super(NicosProxy, self).__init__(obj)
        self._obj = obj

    def __getattr__(self,name):
        return getattr(self.pos,name)

    def __setattr__(self,name,value):
        if name == '_obj':
            self.__dict__[name]=value
        elif self._obj:
            return setattr(self._obj,name,value)

    def __repr__(self):
        return self._obj.__repr__()


#Auxiliary getter function.
def getter(attrib):
    return lambda self, *args, **kwargs: getattr(self._obj, attrib)(*args, **kwargs)


def ProxyFactory(obj, names, proxyclass=NicosProxy):
    """Factory function for Proxies that can delegate magic names."""
    #Build class.
    cls = type("%sNicosProxy" % obj.__class__.__name__,
               (proxyclass,),
               {})
    #Add magic names.
    for name in names:
        #Filter magic names.
        if name.startswith("__") and name.endswith("__"):
            if hasattr(obj.__class__, name):
                #Set attribute.
                setattr(cls, name, getter(name))
    #Return instance.
    return cls(obj)

