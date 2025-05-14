# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Daniel Matulka <daniel.matulka@tuwien.ac.at>
#
# *****************************************************************************

from nicos.core import  Override, Param, floatrange, oneof

from .generic import GenericLimaCCD


class EigerLimaCCD(GenericLimaCCD):
    """
    Extension to the GenericLimaCCD for the Dectris Eiger detectors.
    """

    # Values for the K-Alpha 1 lines of the element according to
    # the X-Ray Data Booklet
    # (https://xdb.lbl.gov/Section1/Table_1-3.pdf)
    anodes = {
        'Cr':5414.7,
        'Co':6930.3,
        'Cu':8047.8,
        'Ga':9251.7,
        'Mo':17479.3,
        'Rh':20216.1,
        'Ag':22162.9,
        'In':24209.7,
        'W':59318.2,
    }

    parameters = {
        'anode': Param('Anode material of the X-Ray source (sets the energy to the K-Alpha line)',
                         type=oneof(*(list(anodes.keys())+['special'])), settable=True,
                         unit='', volatile=True, category='general'),
        'photon_energy': Param('Energy of the X-rays of intrest',
                         type=floatrange(fr=0,to=10e6), settable=True,
                         unit='eV', volatile=True, category='general'),
        'threshold_energy': Param('Camera detection threshold.\
                                  This should be set between 50 to 60 % of the \
                                  incoming beam energy.',
                         type=floatrange(fr=0,to=10e6), settable=True,
                         unit='eV', volatile=True, category='general'),
        'temperature': Param('Temperature of the detector',
                         type=float, settable=False,
                         unit='°C', volatile=True, category='general'),
        'humidity': Param('Humidity of the detector',
                         type=float, settable=False,
                         unit='%', volatile=True, category='general'),
    }

    parameter_overrides = {
        'hwdevice': Override(mandatory=True),
    }

    def doReadTemperature(self):
        return float(self._hwDev._dev.temperature)

    def doReadHumidity(self):
        return float(self._hwDev._dev.humidity)

    def doReadPhoton_Energy(self):
        return float(self._hwDev._dev.photon_energy)

    def doWritePhoton_Energy(self, value):
        self._hwDev._dev.photon_energy = value

    def doReadThreshold_Energy(self):
        return float(self._hwDev._dev.threshold_energy)

    def doWriteThreshold_Energy(self, value):
        self._hwDev._dev.threshold_energy = value

    def doWriteAnode(self, value):
        if value != 'special':
            self._hwDev._dev.photon_energy = self.anodes[value]

    def doReadAnode(self):
        set_energy = self.photon_energy
        material = [name for name, val in self.anodes.items()
                    if (abs(val - set_energy)) < 1]

        if not material:
            return 'special'
        return material[0]
