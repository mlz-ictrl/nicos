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

from nicos.core.errors import ConfigurationError

from nicos_ess.nexus.placeholder import DeviceValuePlaceholder, PlaceholderBase


class DistancesPlaceholder(PlaceholderBase):
    """Placeholder for distance of a component from sample
    """

    def __init__(self, component, defaultval):
        self.component = component
        self.defaultval = defaultval

    def fetch_info(self, metainfo):
        value = DeviceValuePlaceholder('Distances',
                                       self.component).fetch_info(metainfo)
        sample = DeviceValuePlaceholder('Distances',
                                        'sample').fetch_info(metainfo)
        if sample and isinstance(sample[0], float) and \
                value and isinstance(value[0], float):
            dist = sample[0] - value[0]
            return (dist, '%s' % dist, value[2], value[3])
        else:
            return (self.defaultval, '%s' % self.defaultval, 'mm', 'general')


class SlitGeometryPlaceholder(PlaceholderBase):
    """ Placeholder that determines the slit geometry from given slit number
    Slit geometry is defined as [top-bottom, left-right]
    """

    def __init__(self, slit_number, defaultval):
        if 0 < slit_number < 5:
            self.slit = slit_number
        else:
            raise ConfigurationError('Slit %s is out of range.' % slit_number)
        self.defaultval = defaultval

    def __repr__(self):
        return "(Slit: %s)" % self.slit

    def fetch_info(self, metainfo):
        """ Returns the slit geometry [top-bottom, left-right]
        """
        num = self.slit
        top = DeviceValuePlaceholder('d%st' % num).fetch_info(metainfo)
        bottom = DeviceValuePlaceholder('d%sb' % num).fetch_info(metainfo)
        left = DeviceValuePlaceholder('d1l').fetch_info(metainfo)
        right = DeviceValuePlaceholder('d1r').fetch_info(metainfo)

        h = self.defaultval if None in [top, bottom] else top[0] - bottom[0]
        w = self.defaultval if None in [left, right] else left[0] - right[0]

        if None in [h, w]:
            return None

        val = [h, w]
        return val, '%s' % val, 'mm', ''


class UserEmailPlaceholder(DeviceValuePlaceholder):

    def __init__(self, dev, parameter, getemail=False):
        DeviceValuePlaceholder.__init__(self, dev, parameter)
        self.getemail = getemail

    def fetch_info(self, metainfo):
        useremail, _, _, _ = DeviceValuePlaceholder.fetch_info(self, metainfo)
        usersplit = useremail.split('<')
        ret = ''
        if not self.getemail:
            ret = usersplit[0].strip()
        elif len(usersplit) > 1:
            ret = usersplit[1][:-1]
        return ret, ret, '', ''


class ComponentDistancePlaceholder(PlaceholderBase):

    def __init__(self, component1, component2):
        self.component1 = component1
        self.component2 = component2

    def fetch_info(self, metainfo):
        d1 = metainfo.get(('Distances', self.component1), 0.0)
        d2 = metainfo.get(('Distances', self.component2), 0.0)
        val = abs(d1[0]-d2[0])
        return val, '%s' % val, 'mm', ''


class TimeBinningPlaceholder(PlaceholderBase):

    def __init__(self, detector, channel, ax_no):
        self.detector = detector
        self.channel = channel
        self.ax_no = ax_no

    def fetch_info(self, metainfo):
        desc = metainfo.get((self.detector, 'desc_' + self.channel))
        chspeed = metainfo.get(('ch1', 'speed'))
        chindexphase = metainfo.get(('chopper', 'indexphase'))

        if not desc:
            return None

        desc = desc[0]
        chspeed = 1000 if not chspeed else chspeed[0]
        chindexphase = -6.7 if not chindexphase else chindexphase[0]

        toffset = chindexphase * 1e7 / (6 * chspeed)

        bins = [e-toffset for e in desc['dimbins'][self.ax_no]]

        return (bins, '', 'ms', 'general')
