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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#
# *****************************************************************************

from nicos.core.errors import ConfigurationError
from nicos_ess.nexus.placeholder import PlaceholderBase, DeviceValuePlaceholder


class SlitGeometryPlaceholder(PlaceholderBase):
    """ Placeholder that determines the slit geometry from given slit number
    Slit geometry is defined as [top-bottom, left-right]
    """
    def __init__(self, slit_number):
        if 0 < slit_number < 5:
            self.slit = slit_number
        else:
            raise ConfigurationError('Slit %s is out of range.' % slit_number)

    def __repr__(self):
        return "(Slit: %s)" % self.slit

    def fetch_info(self, metainfo):
        """ Returns the slit geometry [top-bottom, left-right]
        """
        num = self.slit
        values = DeviceValuePlaceholder('slit%s' % num).fetch_info(metainfo)[0]
        if values is not None:
            left, right, bottom, top = values
            val = [top - bottom, left - right]
            return val, '%s' % val, 'mm', ''

        return None


class SlitValuePlaceholder(DeviceValuePlaceholder):
    """ Placeholder that determines the value of a specific motor in that
    slit. The slit device is provided using *slitdevice* and the
    *component* provides the name the of the component in the slit
    """

    component_to_ids = {
        'left': 0,
        'right': 1,
        'bottom': 2,
        'top': 3,
        'horizontal': 0,
        'vertical': 1
    }

    def __init__(self, slitdevice, component):
        DeviceValuePlaceholder.__init__(self, slitdevice)
        if component not in self.component_to_ids:
            raise ConfigurationError('Component %s unidentified for '
                                     '%s' % (component, slitdevice))
        self.component = component

    def __repr__(self):
        return "(slit: %s and component: %s)" % (self.device, self.component)

    def fetch_info(self, metainfo):
        """ Returns the info of the component of the slit
        """
        values, _, unit, _ = DeviceValuePlaceholder.fetch_info(self, metainfo)

        valueid = self.component_to_ids[self.component]
        if valueid < len(values):
            return values[valueid], '%s' % values[valueid], unit, ''

        return None
