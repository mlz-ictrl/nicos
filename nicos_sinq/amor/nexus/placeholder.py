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
            raise ConfigurationError('Slit number not in range.')

    def fetch_info(self, metainfo):
        """ Returns the slit geometry [top-bottom, left-right]
        """
        num = self.slit
        top = DeviceValuePlaceholder('d%st' % num).fetch_info(metainfo)[0]
        bottom = DeviceValuePlaceholder('d%sb' % num).fetch_info(metainfo)[0]
        left = DeviceValuePlaceholder('d1l').fetch_info(metainfo)[0]
        right = DeviceValuePlaceholder('d1r').fetch_info(metainfo)[0]
        if None in [top, bottom, left, right]:
            return None
        val = [top-bottom, left-right]
        return val, '%s' % val, 'mm', ''
