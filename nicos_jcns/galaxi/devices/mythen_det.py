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
#   Alexander Steffens <a.steffens@fz-juelich.de>
#
# *****************************************************************************

from __future__ import absolute_import, division, print_function

from nicos import session
from nicos.core.device import requires
from nicos.core.errors import ConfigurationError, InvalidValueError
from nicos.core.params import Param, dictwith
from nicos.core.utils import USER, usermethod
from nicos.devices.datasinks.image import ImageSink as BaseImageSink, \
    SingleFileSinkHandler as BaseSingleFileSinkHandler
from nicos.devices.tango import ImageChannel as TangoImageChannel

# available energy parameters
ENERGY_PARAMETERS = ('xray', 'threshold')


class ImageChannel(TangoImageChannel):
    """Image channel that allows to configure various parameters of the DECTRIS
    Mythen detector.
    """

    parameters = {
        'delayafter': Param(
            'Delay between two subsequent frames.',
            type=int,
            settable=True,
            userparam=False,
            unit='ns',
            volatile=True,
        ),
        'delaybefore': Param(
            'Delay between a trigger signal and the start of the measurement.',
            type=int,
            settable=True,
            userparam=False,
            unit='ns',
            volatile=True,
        ),
        'energy': Param(
            'X-ray and threshold energy in kilo electron volt.',
            type=dictwith(**dict((p, float) for p in ENERGY_PARAMETERS)),
            settable=True,
            unit='keV',
            volatile=True,
            chatty=True,
        ),
        'frames': Param(
            'Number of frames within an acquisition.',
            type=int,
            settable=True,
            volatile=True,
            userparam=False,
            unit='',
        ),
    }

    def doPrepare(self):
        pilatus_det = session.getDevice('pilatus')
        self._dev.ignoreGate = pilatus_det not in session.experiment.detectors
        TangoImageChannel.doPrepare(self)

    def doReadDelayafter(self):
        return self._dev.delayAfter

    def doWriteDelayafter(self, value):
        self._dev.delayAfter = value

    def doReadDelaybefore(self):
        return self._dev.delayBefore

    def doWriteDelaybefore(self, value):
        self._dev.delayBefore = value

    def doReadEnergy(self):
        return dict(zip(ENERGY_PARAMETERS, self._dev.energy))

    def doWriteEnergy(self, value):
        self._dev.energy = [value['xray'], value['threshold']]

    def doReadFrames(self):
        return self._dev.frames

    def doWriteFrames(self, value):
        self._dev.frames = value

    def doReadThreshold(self):
        return self._dev.threshold

    def doWriteThreshold(self, value):
        self._dev.threshold = value

    @usermethod
    @requires(level=USER)
    def setEnergy(self, radiation=None, **value):
        """Either load the predefined settings that are suitable for usage with
        silver, chromium, copper or molybdenum radiation or set the x-ray and
        threshold energy to any other appropriate values.

        :param str radiation: 'Ag', 'Cr', 'Cu' or 'Mo' (case insensitive)
        :param dict[str, float] value: {'xray': x, 'threshold': y}
        """
        if not (radiation or value) or radiation and value:
            raise InvalidValueError('call either dev.SetEnergy("<radiation>") '
                                    'or dev.SetEnergy(xray=x, threshold=y)')
        if radiation:
            self._dev.LoadEnergySettings(radiation)
        else:
            self.energy = value


class SingleFileSinkHandler(BaseSingleFileSinkHandler):
    """Single file sink handler to use when measuring with the DECTRIS Mythen
    detector that writes its count values to a data file.
    """

    def writeData(self, fp, image):
        for index, value in enumerate(image):
            fp.write('{:d} {:d}\n'.format(index, value))
        fp.flush()


class ImageSink(BaseImageSink):
    """Image sink that uses the image sink handler for the DECTRIS Mythen
    detector.
    """

    handlerclass = SingleFileSinkHandler

    def doInit(self, _mode):
        for dev_name in self.detectors:
            detector = session.getDevice(dev_name)
            for img in detector._attached_images:
                if not isinstance(session.getDevice(img), ImageChannel):
                    raise ConfigurationError(
                        'mythen image sink can only be used by detector '
                        'devices that come up with image channels that are '
                        'instances of {}'.format(ImageChannel)
                    )
