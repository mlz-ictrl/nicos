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

from os import path
from time import time

from nicos import session
from nicos.core import status
from nicos.core.constants import FINAL
from nicos.core.data import DataSinkHandler
from nicos.core.device import Readable, requires
from nicos.core.errors import ConfigurationError, InvalidValueError
from nicos.core.params import Attach, Override, Param, anytype, dictof, \
    dictwith, floatrange, intrange, none_or, oneof
from nicos.core.utils import USER, usermethod
from nicos.devices.datasinks import FileSink
from nicos.devices.generic.detector import Detector as GenericDetector, \
    PassiveChannel
from nicos.devices.tango import PyTangoDevice

# available energy parameters
ENERGY_PARAMETERS = ('xray', 'threshold')

# available crystallographic parameters and their conversion function
MX_PARAMETERS = {
    'wavelength': float,           # angstrom
    'energy_range': eval,          # keV
    'detector_distance': float,    # mm
    'detector_voffset': float,     # mm
    'beam_xy': eval,               # pixels
    'flux': float,                 # cps
    'filter_transmission': float,  # transmission factor
    'start_angle': float,          # deg
    'detector_2theta': float,      # deg
    'polarization': float,         # polarisation factor
    'alpha': float,                # deg
    'kappa': float,                # deg
    'phi': float,                  # deg
    'chi': float,                  # deg
    'omega': float,                # deg
    'oscillation_axis': str,       # name of the axis
    'n_oscillations': int,         # number of oscillations
    'start_position': float,       # mm
    'shutter_time': float,         # s
}


class Configuration(PyTangoDevice, PassiveChannel):
    """Channel that allows to configure various parameters of the DECTRIS
    Pilatus detector.

    Without this channel you cannot access any parameter of the Pilatus
    detector except for the exposure time (TimerChannel) out of NICOS.

    You can attach devices to this channel in order to read out their values
    and store them in the Pilatus image header via the ``mxsettings``
    parameter.
    """

    # TODO: add proper descriptions
    attached_devices = {
        'detector_distance': Attach(
            'Current detector distance to sample.',
            Readable, optional=True,
        ),
        'detector_voffset': Attach(
            'Current vertical detector translation.',
            Readable,  optional=True,
        ),
        'flux': Attach(
            'Current photon flux in cps.',
            Readable, optional=True,
        ),
        'filter_transmission': Attach(
            'Current transmission filter factor.',
            Readable, optional=True,
        ),
        'start_angle': Attach(
            '',
            Readable, optional=True,
        ),
        'detector_2theta': Attach(
            'Current two-theta position.',
            Readable, optional=True,
        ),
        'polarization': Attach(
            '',
            Readable, optional=True,
        ),
        'alpha': Attach(
            'Current alpha position.',
            Readable, optional=True,
        ),
        'kappa': Attach(
            'Current kappa position.',
            Readable, optional=True,
        ),
        'phi': Attach(
            'Current phi position.',
            Readable, optional=True,
        ),
        'chi': Attach(
            'Current chi position.',
            Readable, optional=True,
        ),
        'omega': Attach(
            'Current omega position.',
            Readable, optional=True,
        ),
        'start_position': Attach(
            '',
            Readable, optional=True,
        ),
        'shutter_time': Attach(
            '',
            Readable, optional=True,
        ),
    }

    parameters = {
        'energy': Param(
            'X-ray and threshold energy in kilo electron volt. Set to "None" '
            'if the energy is either not set yet not configurable for this '
            'detector.',
            type=none_or(
                dictwith(**dict((p, float) for p in ENERGY_PARAMETERS))),
            settable=True,
            volatile=True,
            unit='keV',
            prefercache=False,
            chatty=True,
        ),
        'exposures': Param(
            'Number of exposures to accumulate per frame/readout.',
            type=intrange(1, 2**32 - 1),
            settable=True,
            volatile=True,
            userparam=False,
            unit='',
        ),
        'imageheader': Param(
            'String to be included in the image header.',
            type=str,
            settable=True,
            volatile=True,
            unit='',
            chatty=True,
        ),
        'images': Param(
            'Number of images for an automatic sequence.',
            type=intrange(1, 2**16 - 1),
            settable=True,
            volatile=True,
            userparam=False,
            unit='',
        ),
        'mxsettings': Param(
            'Crystallographic parameters reported in the image header.',
            type=dictof(oneof(*MX_PARAMETERS), anytype),
            settable=True,
            volatile=True,
            unit='',
            prefercache=False,
        ),
        'period': Param(
            'Exposure period in seconds (must be longer than exposure time + '
            '2.28 ms readout time).',
            type=floatrange(1.0015, 60 * 24 * 60 * 60),  # maximum: 60 days
            settable=True,
            volatile=True,
            userparam=False,
            unit='s',
        ),
        'sensorvalues': Param(
            'Relative humidity and temperature sensor values on all channels.',
            type=dictof(str, str),
            unit='',
            volatile=True,
        ),
    }

    parameter_overrides = {
        'lowlevel': Override(default=True),
    }

    def _poll_all_channels(self):
        # update the status of all pilatus detector channels
        for detector in session.experiment.detectors:
            if isinstance(detector, Detector):
                detector.poll()

    def doRead(self, maxage=0):
        return []

    def valueInfo(self):
        return ()

    def doStatus(self, maxage=0):
        return PyTangoDevice.doStatus(self, maxage)[0], ''

    def doPrepare(self):
        self.doUpdateMxsettings({})

    def doReadEnergy(self):
        values = self._dev.energy
        return dict(zip(ENERGY_PARAMETERS, values)) if all(values) else None

    def _write_energy(self, value):
        # only send the energy parameters to the hardware if they have changed
        if self.energy:
            for param in ENERGY_PARAMETERS:
                if abs(value[param] - self.energy[param]) > 0.001:
                    self._dev.energy = [value['xray'], value['threshold']]
                    return

    def doWriteEnergy(self, value):
        self._write_energy(value)
        self._poll_all_channels()

    def doUpdateEnergy(self, value):
        # only necessary for transmitting setup values to the hardware
        if self.doStatus()[0] == status.OK:
            self._write_energy(value)

    def doReadExposures(self):
        return self._dev.exposures

    def doReadImages(self):
        return self._dev.images

    def doWriteImages(self, value):
        self._dev.images = value

    def doReadImageheader(self):
        return self._dev.imageHeader

    def doWriteImageHeader(self, value):
        self._dev.imageHeader = value

    def doReadMxsettings(self):
        mx_settings = self._dev.mxSettings
        if not mx_settings:
            return {}
        # create dict {k1: v1, k2: v2, ...} from list [k1, v1, k2, v2, ...]
        mx_settings = {mx_settings[2 * i]: mx_settings[2 * i + 1]
                       for i in range(len(mx_settings) // 2)}
        # convert values to tuple, float or int
        return {k: MX_PARAMETERS[k](v) for k, v in mx_settings.items()}

    def doWriteMxsettings(self, value):
        start_time = time()
        # energy update must be completed after maximum 15 seconds
        while time() < start_time + 15:
            if self.doStatus()[0] == status.OK:
                break
            self.log.info('waiting until the detector is ready')
            session.delay(1.5)
        else:
            self.log.error('mxsettings update could not be performed: '
                           'pilatus detector is still busy')
            return
        # flatten dict {k1: v1, k2: v2, ...} to [k1, v1, k2, v2, ...]
        self._dev.mxSettings = [str(v) for v in list(sum(value.items(), ()))]

    def doUpdateMxsettings(self, value):
        value = dict(value)  # convert to writable dict
        for name, adev in ((k, v) for k, v in self._adevs.items() if v):
            adev_value = adev.read()
            if name == 'filter_transmission':
                adev_value = 1 / adev_value
            value[name] = str(adev_value)
        if value:
            self.doWriteMxsettings(value)

    def doReadPeriod(self):
        return self._dev.period

    def doWritePeriod(self, value):
        self._dev.period = value

    def doReadSensorvalues(self):
        sensor_values = self._dev.sensorValues
        # create dict {k1: v1, k2: v2, ...} from list [k1, v1, k2, v2, ...]
        return {sensor_values[2 * i]: sensor_values[2 * i + 1]
                for i in range(len(sensor_values) // 2)}

    @usermethod
    @requires(level=USER)
    def setEnergy(self, radiation=None, **value):
        """Either load the predefined settings that are suitable for usage with
        silver, chromium, copper, iron oder molybdenum radiation or set
        the x-ray and threshold energy to any other appropriate values.

        :param str radiation: 'Ag', 'Cr', 'Cu', 'Fe' or 'Mo' (case insensitive)
        :param dict[str, float] value: {'xray': x, 'threshold': y}
        """
        if not (radiation or value) or radiation and value:
            raise InvalidValueError('call either dev.SetEnergy("<radiation>") '
                                    'or dev.SetEnergy(xray=x, threshold=y)')
        if radiation:
            self._dev.LoadEnergySettings(radiation)
            self._poll_all_channels()
        else:
            self.energy = value


class Detector(GenericDetector):
    """Generic detector that provides access to the image directory and filename
    as well as the diskspace attributes of a DECTRIS Pilatus detector.

    This detector requires exactly one 'other' channel that must be an instance
    of :class:`Configuration`.
    """

    parameters = {
        'diskspace': Param(
             'Available space on the Pilatus computer in gibibytes.',
            type=float,
            unit='GiB',
            fmtstr='%.3f',
            volatile=True,
        ),
        'filename': Param(
            'Name of currently being created (during exposures) or last '
            'created image file.',
            type=str,
            unit='',
            volatile=True,
        ),
        'imagedir': Param(
            'Current target directory on the Pilatus computer where the next '
            'detector image will be stored at.',
            type=str,
            settable=True,
            unit='',
            volatile=True,
            internal=True,
        ),
        'nextfilename': Param(
            'Name of the next created image file.',
            type=str,
            settable=True,
            unit='',
            internal=True,
        ),
    }

    def doPreinit(self, mode):
        if len(self._attached_others) != 1 or not isinstance(
                self._attached_others[0], Configuration):
            raise ConfigurationError(
                'pilatus detectors require exactly one "other" channel that '
                'is an instance of {}'.format(Configuration)
            )
        self._cfg_channel = self._attached_others[0]._dev
        GenericDetector.doPreinit(self, mode)

    def doPoll(self, _n, _maxage):
        self._pollParam('filename')
        self._pollParam('imagedir')

    def doPrepare(self):
        GenericDetector.doPrepare(self)
        self.readArrays(FINAL)  # update readresult of image channels

    def doReadDiskspace(self):
        return self._cfg_channel.diskSpace

    def doReadFilename(self):
        return path.basename(self._cfg_channel.absImagePath)

    def doReadImagedir(self):
        return self._cfg_channel.imageDir

    def doWriteImagedir(self, value):
        self._cfg_channel.imageDir = value

    def doReadNextfilename(self):
        return self._cfg_channel.nextFilename

    def doWriteNextfilename(self, value):
        self._cfg_channel.nextFilename = value


class TIFFImageSinkHandler(DataSinkHandler):
    """Data sink handler for the DECTRIS Pilatus detector that sends the next
    image filename together with the current nicos subdirectory automatically
    to the hardware before starting an exposure.
    """

    def prepare(self):
        self.manager.assignCounter(self.dataset)
        for det in self.sink.get_pilatus_detectors():
            filename, filepaths = self.manager.getFilenames(
                self.dataset, self.sink.filenametemplate, self.sink.subdir)
            # imagedir = <year>/<proposal>/<subdir>
            det.imagedir = '/'.join(filepaths[0].split(
                path.sep)[-4 - int(bool(self.sink.subdir)):-2])
            det.nextfilename = filename
            det.poll()  # update parameter values


class TIFFImageSink(FileSink):
    """Data sink that uses the TIFF image sink handler for the DECTRIS Pilatus
    detector.

    At least one of the devices in the ``detectors`` attribute must be a
    Pilatus detector.
    """

    handlerclass = TIFFImageSinkHandler

    def doInit(self, _mode):
        self._pilatus_detectors = []
        for det_name in self.detectors:
            if isinstance(session.getDevice(det_name), Detector):
                self._pilatus_detectors.append(session.getDevice(det_name))
            else:
                self.log.warning('non-pilatus detector %r uses pilatus image '
                                 'file sink', det_name)
        if not self._pilatus_detectors:
            raise ConfigurationError(
                'pilatus data sink requires at least one pilatus detector '
                'device that is an instance of {}'.format(Detector)
            )

    def get_pilatus_detectors(self):
        """Return all pilatus detector devices passed through the ``detectors``
        parameter as a list.

        Used by :class:`DataSinkHandler` class in order to send the current
        image filename and image path to the hardware.

        :return: list of all pilatus detector devices
        :rtype: list[Device]
        """
        return self._pilatus_detectors
