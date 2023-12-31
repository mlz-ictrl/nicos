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
#   Leonardo J. Ibáñez <leonardoibanez@cnea.gob.ar>
#
# *****************************************************************************

from nicos_lahn.andes.gui.instrument import InstrumentWidget


class ANDES(InstrumentWidget):
    distances = ('Lms', 'LtoD')

    monoradius = 80
    sampleradius = 40
    detectorradius = 20

    # default values (used when no such devices are configured)
    values = {
        'mth': 0,
        'mtt': 40,
        'sth': 0,
        'stt': 15,
        # scale the distances
        'Lms': 1600 / 10,
        'LtoD': 900 / 10,
    }

    def initUi(self):
        InstrumentWidget.initUi(self, False)

    def update(self):
        # incoming beam
        InstrumentWidget.beam(self)

        # monochromator
        InstrumentWidget.monochromator(self)

        # sample
        InstrumentWidget.sample(self, -1)

        # detector
        InstrumentWidget.sampleToDetector(self)

        InstrumentWidget.updateBeams(self)
