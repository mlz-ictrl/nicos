# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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

from os import path
from time import time

from numpy import delete

from nicos import session
from nicos.core.constants import FINAL
from nicos.core.data.sink import DataSinkHandler as BaseDataSinkHandler
from nicos.core.device import Readable, requires
from nicos.core.errors import InvalidValueError
from nicos.core.mixins import DeviceMixinBase
from nicos.core.params import Attach, Override, Param, anytype, dictof, \
    dictwith, listof, oneof
from nicos.core.status import BUSY, OK
from nicos.core.utils import USER, usermethod
from nicos.devices.datasinks.file import FileSink as BaseFileSink
from nicos.devices.datasinks.image import ImageSink, SingleFileSinkHandler
from nicos.devices.generic.detector import Detector as GenericDetector, \
    PassiveChannel
from nicos.devices.tango import PyTangoDevice

ENERGY_PARAMS = ('photon', 'threshold')


class ConfigurationChannel(PyTangoDevice, PassiveChannel):
    """Channel that allows to configure various parameters of a DECTRIS 2D
    detector.

    Without this channel you cannot access any parameter of the detector except
    for the exposure time out of NICOS.
    """

    parameter_overrides = {
        'visibility': Override(default=()),
    }

    def doRead(self, _maxage=0):
        return []

    def valueInfo(self):
        return ()


class HasEnergy(DeviceMixinBase):
    """Mixin for DECTRIS detectors that provide an energy parameter."""

    parameters = {
        'energy': Param(
            'Photon and threshold energy in kilo electron volt.',
            type=dictwith(**dict((p, float) for p in ENERGY_PARAMS)),
            settable=True,
            volatile=True,
            unit='keV',
            prefercache=False,
            chatty=True,
        ),
    }

    def doPoll(self, n, maxage):
        if hasattr(super(), 'doPoll'):
            super().doPoll(n, maxage)
        if self.doStatus()[0] != BUSY:
            self._pollParam('energy')

    def doPreinit(self, mode):
        super().doPreinit(mode)
        # channel presets accessed in doStatus that is called in doUpdateEnergy
        self._channel_presets = {}

    def _read_energy(self):
        return [float(f'{v:.3f}') for v in self._cfg_channel.energy]

    def doReadEnergy(self):
        return dict(zip(ENERGY_PARAMS, self._read_energy()))

    def _write_energy(self, value):
        # only send the energy parameters to the hardware if they have changed
        if any(abs(value[p] - self.energy[p]) > 0.001 for p in ENERGY_PARAMS):
            self._cfg_channel.energy = [value['photon'], value['threshold']]
            self.poll()

    def doWriteEnergy(self, value):
        self._write_energy(value)

    def doUpdateEnergy(self, value):
        if not self._sim_intercept:
            # only necessary for transmitting setup values to the hardware
            if self.doStatus()[0] == OK:
                self._write_energy(value)

    @usermethod
    @requires(level=USER)
    def setEnergy(self, element=None, **value):
        """Either set the energy to the K-alpha fluorescence radiation energy
        of an element or set the photon and threshold energy to any other
        appropriate values.

        :param str element: element name according to the periodic table
        :param dict[str, float or list[float]] value: {'photon': x,
          'threshold': y} or {'photon': x, 'threshold': [y, z]}
        """
        if not (element or value) or element and value:
            raise InvalidValueError('call either dev.SetEnergy("<element>"), '
                                    'dev.SetEnergy(xray=x, threshold=y) or'
                                    'dev.SetEnergy(xray=x, threshold=[y, z])')
        if element:
            self._cfg_channel.LoadEnergySettings(element)
            self.poll()
        else:
            self.energy = value


class Detector(GenericDetector):
    """DECTRIS detector device.

    Sets the configuration channel to allow access to various parameters and
    determines the master detector during preparation for the next measurement.
    """

    has_gate = True

    def doPreinit(self, mode):
        super().doPreinit(mode)
        self._cfg_channel = self._attached_others[0]._dev

    def doPrepare(self):
        # first detector in detector list is controller
        first_det = session.experiment.detectors[0]
        is_controller = not first_det.has_gate or self.name == first_det.name
        for dev in self._attached_timers:
            dev.iscontroller = is_controller
        super().doPrepare()


class Detector2D(Detector):
    """Detector that provides access to the image path and other necessary
    parameters of DECTRIS 2D detectors.
    """

    parameters = {
        'diskspace': Param(
            'Available space on the detector computer in gibibytes.',
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
        'humidity': Param(
            'Relative humidity inside the detector module compartment.',
            type=float,
            unit='%',
            fmtstr='%.3f',
            volatile=True,
        ),
        'imagedir': Param(
            'Current target directory on the detector computer where the next '
            'detector image will be stored at.',
            type=str,
            unit='',
            volatile=True,
        ),
        'nextimagepath': Param(
            'Path of the next created image file.',
            type=str,
            settable=True,
            unit='',
            internal=True,
        ),
        'temperature': Param(
            'Detector temperature in degree Celsius.',
            type=float,
            unit='degC',
            fmtstr='%.3f',
            volatile=True,
        ),
    }

    def doPoll(self, _n, _maxage):
        self._pollParam('filename')
        self._pollParam('imagedir')

    def doPrepare(self):
        super().doPrepare()
        # update read result of image channels
        self.readArrays(FINAL)

    def doReadDiskspace(self):
        return self._cfg_channel.diskSpace

    def doReadHumidity(self):
        return self._cfg_channel.humidity

    def doReadFilename(self):
        return path.basename(self._cfg_channel.latestImagePath)

    def doReadImagedir(self):
        return path.dirname(self._cfg_channel.latestImagePath)

    def doReadNextimagepath(self):
        return self._cfg_channel.nextImagePath

    def doWriteNextimagepath(self, value):
        self._cfg_channel.nextImagePath = value

    def doReadTemperature(self):
        return self._cfg_channel.temperature


class EIGERDetector(HasEnergy, Detector2D):
    """Generic detector that provides access to the image directory and
    filename as well as the disk space attributes of a `DECTRIS EIGER detector
    <https://www.dectris.com/detectors/x-ray-detectors/eiger2/>`_.
    """

    parameter_overrides = {
        'energy': Override(
            type=dictwith(**dict((('photon', float),
                                  ('threshold', listof(float))))),
        ),
    }

    def doReadEnergy(self):
        energy = self._read_energy()
        # return only threshold values if they are enabled
        threshold = list(delete(energy[1:], [i for i, enabled in enumerate(
            self._cfg_channel.thresholdEnabled) if not enabled]))
        return dict(zip(ENERGY_PARAMS, (energy[0], threshold)))

    def _write_energy(self, value):
        # only send the energy parameters to the hardware if they have changed
        energy = [self.energy['photon']] + self.energy['threshold']
        value = [value['photon']] + value['threshold']
        if len(energy) != len(value) or any(abs(e - v) > 0.001
                                            for e, v in zip(energy, value)):
            self._cfg_channel.energy = value

    @usermethod
    @requires(level=USER)
    def setEnergy(self, element=None, **value):
        """Either set the energy to the K-alpha fluorescence radiation energy
        of an element or set the photon and threshold energy to any other
        appropriate values.

        :param str element: element name according to the periodic table
        :param dict[str, float or list[float]] value: {'photon': x,
          'threshold': y} or {'photon': x, 'threshold': [y, z]}
        """
        if 'threshold' in value and not isinstance(value['threshold'], list):
            value['threshold'] = [value['threshold']]
        super().setEnergy(element, **value)


class MYTHENDetector(HasEnergy, Detector):
    """Detector that allows to configure the energy parameters of the DECTRIS
    MYTHEN detector and start measurements with an external gate signal.
    """

    has_gate = False


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


class PILATUS300KDetector(Detector2D):
    """Detector that provides access to all necessary parameters of `DECTRIS
    PILATUS3 R 300K detectors
    <https://www.dectris.com/detectors/x-ray-detectors/pilatus3/>`_.

    You can attach devices to this detector in order to read out their values
    and store them in the PILATUS image header via the ``mxsettings``
    parameter.
    """

    attached_devices = {
        'detector_distance': Attach(
            'Current detector distance to sample.',
            Readable, optional=True,
        ),
        'detector_voffset': Attach(
            'Current vertical detector translation.',
            Readable, optional=True,
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
            'Starting angle of the detector scan.',
            Readable, optional=True,
        ),
        'detector_2theta': Attach(
            'Current detector two-theta position.',
            Readable, optional=True,
        ),
        'polarization': Attach(
            'X-ray polarization.',
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
            'Starting position of the detector scan.',
            Readable, optional=True,
        ),
        'shutter_time': Attach(
            'Time the shutter was open.',
            Readable, optional=True,
        ),
    }

    parameter_overrides = {
        'humidity': Override(
            description='Relative humidity on all channels.',
            type=listof(float),
        ),
        'temperature': Override(
            description='Temperature on all channels in degree Celsius.',
            type=listof(float),
        ),
    }

    parameters = {
        'mxsettings': Param(
            'Crystallographic parameters reported in the image header.',
            type=dictof(oneof(*MX_PARAMETERS), anytype),
            settable=True,
            volatile=True,
            unit='',
            prefercache=False,
        ),
    }

    def doPrepare(self):
        super().doPrepare()
        self.doUpdateMxsettings({})

    def doReadMxsettings(self):
        mx_settings = self._cfg_channel.mxSettings
        if not mx_settings:
            return {}
        # create dict {k1: v1, k2: v2, ...} from list [k1, v1, k2, v2, ...]
        mx_settings = {mx_settings[2 * i]: mx_settings[2 * i + 1]
                       for i in range(len(mx_settings) // 2)}
        # convert values to tuple, float or int
        return {k: MX_PARAMETERS[k](v) for k, v in mx_settings.items()}

    def doWriteMxsettings(self, value):
        start_time = time()
        if not self._sim_intercept:
            # energy update must be completed after maximum 15 seconds
            while time() < start_time + 15:
                if self.doStatus()[0] == OK:
                    break
                self.log.info('waiting until the detector is ready')
                session.delay(1.5)
            else:
                self.log.error('mxsettings update could not be performed: '
                               'pilatus detector is still busy')
                return
        # flatten dict {k1: v1, k2: v2, ...} to [k1, v1, k2, v2, ...]
        self._cfg_channel.mxSettings = [str(v)
                                        for v in list(sum(value.items(), ()))]

    def doUpdateMxsettings(self, value):
        value = dict(value)  # convert to writable dict
        for name, adev in ((k, v) for k, v in self._adevs.items()
                           if v and k not in list(Detector2D.attached_devices)):
            adev_value = adev.read()
            if name == 'filter_transmission':
                adev_value = 1 / adev_value
            value[name] = str(adev_value)
        if value:
            self.doWriteMxsettings(value)

    def _getWaiters(self):
        return self._channels  # ignore devices attached for mx settings


class PILATUS1MDetector(HasEnergy, PILATUS300KDetector):
    """Detector that provides access to all necessary parameters of `DECTRIS
    PILATUS3 R 1M detectors
    <https://www.dectris.com/detectors/x-ray-detectors/pilatus3/>`_, including
    ``energy``.

    You can attach devices to this detector in order to read out their values
    and store them in the PILATUS image header via the ``mxsettings``
    parameter.
    """

    @usermethod
    @requires(level=USER)
    def setEnergy(self, element=None, **value):
        """Either set the energy to the K-alpha fluorescence radiation energy
        of an element or set the photon and threshold energy to any other
        appropriate values.

        :param str element: element name according to the periodic table
        :param dict[str, float or list[float] value: {'photon': x,
            'threshold': y} or {'photon': x, 'threshold': [y, z]}
        """
        if 'threshold' in value and isinstance(value['threshold'], list):
            self.log.info('using first threshold value %f',
                          value['threshold'][0])
            value['threshold'] = value['threshold'][0]

        super().setEnergy(element, **value)


class DataSinkHandler(BaseDataSinkHandler):
    """Data sink handler for DECTRIS 2D detectors that sends the next image
    path automatically to the hardware before starting an exposure.
    """

    def prepare(self):
        self.manager.assignCounter(self.dataset)
        filename, filepaths = self.manager.getFilenames(
            self.dataset, self.sink.filenametemplate, self.sink.subdir)
        for det_name in self.sink.detectors:
            det = session.getDevice(det_name)
            # det.nextimagepath = <year>/<proposal>/<subdir>/<filename>
            det.nextimagepath = path.join(*filepaths[0].split(
                path.sep)[-4 - int(bool(self.sink.subdir)):-2] + [filename])
            det.poll()  # update parameter values


class MYTHENSingleFileSinkHandler(SingleFileSinkHandler):
    """Single file sink handler to use when measuring with the DECTRIS MYTHEN
    detector that writes its count values to a data file.
    """

    def writeData(self, fp, image):
        fp.write('\n'.join(f'{i} {v}' for i, v in enumerate(image)).encode())
        fp.flush()


class FileSink(BaseFileSink):
    """Data sink that uses the image sink handler for DECTRIS 2D detectors."""

    handlerclass = DataSinkHandler


class MYTHENImageSink(ImageSink):
    """Image sink that uses the image sink handler for the DECTRIS MYTHEN
    detector.
    """

    handlerclass = MYTHENSingleFileSinkHandler
