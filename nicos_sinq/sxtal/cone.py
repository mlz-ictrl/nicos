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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************

from math import atan2, cos, radians, sin

import numpy as np

from nicos import session
from nicos.core import Moveable, Param, tupleof, usermethod
from nicos.core.errors import ConfigurationError

from nicos_sinq.sxtal.cell import scatteringVectorLength
from nicos_sinq.sxtal.instrument import SXTalBase
from nicos_sinq.sxtal.sample import SXTalSample
from nicos_sinq.sxtal.singlexlib import angleBetweenReflections, \
    calculateBMatrix, chimat, phimat, z1FromAngles


class Cone(Moveable):
    """
    A class which implements the cone device for a cone scan.
    A cone scan is used when searching for reflections. Consider,
    a reflection has been found and indexed. Let us call this the center
    reflection. Then you know that there are other reflections on a cone
    around this reflection. The opening angle of that cone is the angle
    between the center reflection and the target reflection you wish to search
    for next. With the cone device this cone can be scanned when looking
    for more reflections.
    """

    parameters = {
        'center_reflection': Param('The reflection at the center of the cone',
                                   type=tupleof(tupleof(float, float, float),
                                                tupleof(float, float,
                                                        float, float)),
                                   settable=True, userparam=True),
        'target_reflection': Param('The reflection being searched for',
                                   type=tupleof(float, float, float),
                                   settable=True,
                                   userparam=True),
        'qscale': Param('Scaling factor to apply to Q calculated from'
                        'target_reflection', type=float, default=1.0,
                        userparam=True, settable=True),
    }

    valuetype = float

    def doInit(self, mode):
        self._instrument = session.instrument
        self._sample = session.experiment.sample
        if not isinstance(self._instrument, SXTalBase) or not \
                isinstance(self._sample, SXTalSample):
            raise ConfigurationError('Instrument or sample not single crystal')

    @usermethod
    def use_center(self, idx, reflist='ublist'):
        """Use the reflection with index idx in reflist as center"""
        reflist = session.getDevice(reflist)
        ref = reflist.get_reflection(idx)
        if ref:
            self.center_reflection = (ref[0], ref[1])

    def _calcConeMatrix(self, center):
        z1 = z1FromAngles(self._instrument.wavelength,
                          radians(center['stt']), radians(center['om']),
                          radians(center['chi']), radians(center['phi']))
        alpha = atan2(z1[1], z1[0])
        beta = -atan2(z1[0], z1[2])
        mat_alpha = phimat(alpha)
        mat_beta = chimat(beta)
        return np.transpose(np.matmul(mat_beta, mat_alpha))

    def _calcConeVector(self, openingAngle, coneVal, length, mat_cone):
        # This differs by the sign of 0,1 from phimat
        cone_rot = np.zeros((3, 3), dtype='float64')
        cone_rot[0][0] = cos(coneVal)
        cone_rot[0][1] = -sin(coneVal)
        cone_rot[1][0] = sin(coneVal)
        cone_rot[1][1] = cos(coneVal)
        cone_rot[2][2] = 1.0

        null_vec = np.zeros((3,), dtype='float64')
        null_vec[0] = sin(openingAngle)
        null_vec[2] = cos(openingAngle)
        norm = np.linalg.norm(null_vec)
        null_vec /= norm
        null_vec *= length
        cone_vec = cone_rot.dot(null_vec)
        return mat_cone.dot(cone_vec)

    def doStart(self, target):
        B = calculateBMatrix(self._sample.getCell())
        center = self._instrument._refl_to_dict(self.center_reflection)
        opening_angle = angleBetweenReflections(B, center,
                                                {'h':
                                                 self.target_reflection[0],
                                                 'k':
                                                 self.target_reflection[1],
                                                 'l':
                                                 self.target_reflection[2]})
        cone_mat = self._calcConeMatrix(center)
        length = scatteringVectorLength(B, self.target_reflection)\
            * self.qscale
        scat_vec = self._calcConeVector(opening_angle, np.deg2rad(target),
                                        length, cone_mat)
        poslist = self._instrument._extractPos(scat_vec)
        for (devname, devvalue) in poslist:
            dev = self._instrument._adevs[devname]
            dev.start(devvalue)

    def doStatus(self, maxage=0):
        return self._instrument.status(maxage)

    def doRead(self, maxage=0):
        # No sensible way to read from positions
        return self.target
