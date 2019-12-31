#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#
# *****************************************************************************
from __future__ import absolute_import, division, print_function


class PlaceholderBase(object):
    """ Base class for a placeholder in NeXus template. Children should
    implement the method *fetch_info* which returns the info of the value
    in the form of a tuple consisting of the following qunatities:
    (value, value_string, units, type)
    """

    def __repr__(self):
        return self.__class__.__name__

    def fetch_info(self, metainfo):
        """ Returns the value for the placeholder.
        :param metainfo: The current information of all devices
        :return: tupleof (value, value_string, units, type)
        """
        raise NotImplementedError('Fetch not implemented for placeholder')


class DeviceValuePlaceholder(PlaceholderBase):
    """ Placeholder for device and one of it's parameter in the NeXus structure
    When required the placeholder can fetch the required value of the
    parameter from the device.
    """

    def __init__(self, device, parameter='value', defaultval=None):
        self.device = device
        self.parameter = parameter
        self.defaultval = defaultval

    def __repr__(self):
        return "(Device: %s and Parameter: %s)" % (self.device, self.parameter)

    def fetch_info(self, metainfo):
        """ Fetch the info of the device and it's parameter from the provided
        metainfo. Returns None if no such device or parameter is found in the
        provided metainfo.
        :param metainfo: dictof device, parameter -> (val, str_val, unit, type)
        :return: info tupleof(val, str_val, unit, type)
        """
        defaultinfo = None
        if self.defaultval is not None:
            defaultinfo = (self.defaultval, '%s' % self.defaultval, '', '')
        return metainfo.get((self.device, self.parameter), defaultinfo)
