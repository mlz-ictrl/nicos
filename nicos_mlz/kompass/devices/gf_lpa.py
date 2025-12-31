# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#   Ran Tang <ran.tang@frm2.tum.de>
#
# *****************************************************************************

"""Longitudinal polarisation analysis for Kompass, based on code for Panda."""

import numpy as np

from nicos.core import Attach, LimitError, Override, Param
from nicos.core.params import floatrange, tupleof
from nicos.devices.abstract import MappedMoveable
from nicos.utils import lazy_property

from nicos_mlz.panda.devices.guidefield import AlphaStorage, VectorCoil

###############################################################################
# configuration
# 'orient' gives the field produced by coil i (i=0,1,2,3) by 'current' in XYZ
# coordinates fixed to the spectrometer limits are currently given here too....
# 'driver' is the name of an object controlling that particular coil:
# - x is parallel to the incoming neutrons (x//ki)
# - z is 'up' (pointing to the sky)
# - y is 'to the left', chosen to have right-handed system
###############################################################################


class GuideField(MappedMoveable):
    """Guidefield device, parent class of GF_Kompass and GF_Panda.

    Needs to be called to (re-)calculate the required currents for the coils.
    Calibration is done with a matrix giving the field components created with
    a given current.

    Needs the alpha virtual motor for calculations.

    At KOMPASS, x||Q and y is perpendicular.
    """

    parameter_overrides = {
        'mapping': Override(mandatory=False, type=dict,
                            default={
                                'off': None,
                                'x': (1., 0., 0.),
                                '-x': (-1., 0., 0.),
                                'y': (0., 1., 0.),
                                '-y': (0., -1., 0.),
                                'z': (0., 0., 1.),
                                '-z': (0., 0., -1.),
                                'up': (0., 0., 1.),
                                'down': (0., 0., -1.),
                                '0': (0., 0., 0.),
                                }),
    }
    parameters = {
        'alphaoffset': Param('Offset for the alpha angle',
                             type=float, settable=False, default=0),
        'background': Param('Static magnetic field which is always present '
                            'and should be corrected',
                            type=tupleof(float, float, float), unit='mT',
                            settable=True, default=(0., 0., 0.),
                            category='general'),
        'field': Param('Absolute value of the desired field at the '
                       'sample position',
                       type=floatrange(0.1, 100), unit='mT',
                       settable=True, default=25.,
                       category='general'),
    }

    attached_devices = {
        'alpha': Attach('Device which provides the current \\alpha',
                        AlphaStorage),
        'coils': Attach('List of devices used for the vector field',
                        VectorCoil, multiple=[3, 4]),
    }

    _currentmatrix = None

    def doInit(self, mode):
        MappedMoveable.doInit(self, mode)
        self._currentmatrix = np.zeros(shape=(3, len(self.coils)))
        for i in range(3):
            for j, coil in enumerate(self.coils):
                self._currentmatrix[i, j] = coil.orientation[i] / coil.calibrationcurrent
        self.alpha._callback = self._alphaCallBack

    @lazy_property
    def coils(self):
        return self._attached_coils

    @lazy_property
    def alpha(self):
        return self._attached_alpha

    def doShutdown(self):
        self.alpha._callback = None

    def _alphaCallBack(self):
        if self.target in self.mapping:
            self.doStart(self.target)

    def _startRaw(self, target):
        if target:
            target = np.array(target)
            # set requested field (may try to compensate background)
            self._setfield(self.field * target)
        else:  # switch off completely
            for coil in self.coils:
                coil.move(0.0)

    # no _readRaw, as self.target is the unmapped (Higher level) value
    def doRead(self, maxage=0):
        return self.target

    def _vector2angle(self, vec1, vec2):
        """Calculate the angle between two vectors of the same length.

        @param vec1: vector 1 as an array
        @param vec2: vector 2 as an array
        @return: angle in radian
        """
        cos_theta = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        # Move cos(theta) into the range (-1,1) to avoid an NaN result
        while cos_theta < -1:
            cos_theta += 2
        while cos_theta > 1:
            cos_theta -= 2
        return np.arccos(cos_theta)

    def _setfield(self, b_field=np.array([0, 0, 0])):
        """Set the given field.

        Field components are:

        * Bqperp: component perpendicular to q, but within the scattering plane
        * Bqpar:  component parallel to q (within scattering plane)
        * Bz:     component perpendicular to the scattering plane

        (If TwoTheta==0 & \\hbar\\omega=0 then this coordinate-system is the
        same as the XYZ of the coils.)
        """
        # subtract offset (The field, which is already there, doesn't need to
        # be generated....)
        b_field -= np.array(self.background)
        current = self._b2i(b_field)  # compute currents for requested field

        for coil, curr in zip(self.coils, current):
            ok, why = coil.isAllowed(curr)
            if not ok:
                self.log.error("Can't set %s to %s: %s",
                               coil, coil.format(curr, unit=True), why)
                raise LimitError(why)

        # go there
        for coil, curr in zip(self.coils, current):
            coil.start(curr)

    def _b2i(self, b_field=np.array([0.0, 0.0, 0.0])):
        """Rotate the requested field around z-axis by beta.

        First we get alpha from the spectrometer: alpha is the angle between
        X-axis and \\vec{Q} and is in degrees.
        """
        # read alpha, calculate beta
        if self._currentmatrix.shape != (3, 3):
            raise RuntimeError('Invalid matrix size. It is supposed to be 3 x 3')
        beta = np.radians(self.alphaoffset - self.alpha.read(0))
        r = np.array([
            [np.cos(beta), np.sin(beta), 0.0],
            [-np.sin(beta), np.cos(beta), 0.0],
            [0.0, 0.0, 1.0]])
        return np.dot(np.linalg.inv(self._currentmatrix), np.dot(r, b_field))

    def _i2b(self, currents=np.array([0.0, 0.0, 0.0])):
        """Calculate field from currents and rotate field around z-axis by -beta.

        The field is rotated to the coordinates of the scattering frame
        @param currents: coil currents as a 4-element array
        @return: magnetic field as a 3-element array
        """
        beta = np.radians(self.alphaoffset - self.alpha.read(0))
        r = np.array([
            [np.cos(beta), -np.sin(beta), 0.0],
            [np.sin(beta), np.cos(beta), 0.0],
            [0.0, 0.0, 1.0]])
        return np.dot(r, np.dot(self._currentmatrix, currents))


class GF_Panda(GuideField):
    """Guide field for the PANDA set with 3 coils."""

    parameter_overrides = {
        'mapping': Override(default={
                                'perp':  (1., 0., 0.),
                                '-perp': (-1., 0., 0.),
                                'par':   (0., 1., 0.),
                                '-par':  (0., -1., 0.),
                                'z':     (0., 0., 1.),
                                '-z':    (0., 0., -1.),
                                'up':    (0., 0., 1.),
                                'down':  (0., 0., -1.),
                                '0':     (0., 0., 0.),
                                },),
    }


class GF_Kompass(GuideField):
    """For the KOMPASS coil set with 4 coils."""

    def _b2i(self, b_field=np.array([0.0, 0.0, 0.0])):
        """Calculate currents of 4 coils from the 3D magnetic field.

        The first 3 coils are in the horizontal plane.
        The last 1 coil is the Helmholtz-coil pair for the vertical field.
        @param b_field: magnetic field as a 3-element array
        @return: coil currents as a 4-element array
        """
        if self._currentmatrix.shape != (3, 4):
            raise RuntimeError('Invalid matrix size. It is supposed to be 3 x 4')

        beta = np.radians(self.alphaoffset - self.alpha.read(0))
        r = np.array([
            [np.cos(beta), np.sin(beta), 0.0],
            [-np.sin(beta), np.cos(beta), 0.0],
            [0.0, 0.0, 1.0]])
        b_field = np.dot(r, b_field)
        # temp = np.dot(self._currentmatrix_inv, np.dot(r, b_field))

        # In case the field should be zero within the tolerance range,
        # the currents are set to zero
        if np.linalg.norm(b_field) < 1e-6:
            return np.zeros(4)

        # Calculate the z coil first because it is the only one generating
        # z fields
        # calculates the current of the z coil
        i_ring = b_field[-1] / self._currentmatrix[-1, -1]
        # calculate the remaining 3D field
        b_field_hori = b_field - i_ring * self._currentmatrix[:, -1]

        # If the fields from the 3 horizontal coils have no z-component
        # (ideal case), the Heimholtz-coil pair is considered first for Bz,
        # after which the coil whose field is the closest to the target field
        # direction is considered.
        # The remaining field gives the other 2 coils
        # if the 3 horizontal coils do not generate z fields
        if np.linalg.matrix_rank(self._currentmatrix[:, :-1]) < 3:
            # Check if the remaining field is in the horizontal plane
            if abs(b_field_hori[-1]) < 1e-6:
                b_field_hori = b_field_hori[:-1]
            else:
                raise RuntimeError('The remaining field should not have a '
                                   'z-component but it does')
            # If the field is (mainly) vertical, it does not matter which
            # horizontal coil is considered first.
            # Otherwise, check which coil generates the field closest to the
            # target field direction
            self.log.debug('%s %s', abs(b_field[-1]), np.linalg.norm(b_field[:-1]))
            if abs(b_field[-1]) > np.linalg.norm(b_field[:-1]):
                self.log.debug('Case 1: Target field is more vertical.')
                i_1 = b_field_hori[0] / self._currentmatrix[0, 0]
                b_field_hori_rest = b_field_hori - i_1 * self._currentmatrix[:-1, 0]
                i_rest = np.dot(np.linalg.inv(self._currentmatrix[:-1, 1:-1]),
                                b_field_hori_rest)
                i_hori = np.append(i_1, i_rest)
            else:
                self.log.debug('Case 2: Target field is more horizontal.')
                angles = np.array(list(
                    map(lambda i: self._vector2angle(vec1=b_field_hori,
                                                     vec2=self._currentmatrix[:-1, i]),
                        range(3))))
                index = np.argmin(abs(np.sin(angles)))
                self.log.debug('%s %s', np.rad2deg(angles), index)
                i_ind = 0.5 * np.linalg.norm(b_field_hori) ** 2 / np.dot(
                    b_field_hori, self._currentmatrix[:-1, index])
                b_field_hori_rest = b_field_hori - i_ind * self._currentmatrix[:-1, index]
                i_rest = np.dot(
                    np.linalg.inv(np.delete(self._currentmatrix[:-1, :-1], index, 1)),
                    b_field_hori_rest)
                i_hori = np.insert(i_rest, index, i_ind)

        # If the fields from the 3 horizontal coils have a z-component
        # (non-ideal case), the Heimholtz-coil pair is considered first for Bz,
        # after which the 3 horizontal coils are calculated by solving the
        # 3x3 matrix
        else:
            self.log.debug('Case 3: The 3 horizontal coils have z components')
            i_hori = np.dot(np.linalg.inv(self._currentmatrix[:, :-1]), b_field_hori)
        return np.append(i_hori, i_ring)
