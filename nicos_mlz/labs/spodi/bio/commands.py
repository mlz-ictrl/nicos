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
#   Dominik Petz <dominik.petz@frm2.tum.de>
#
# *****************************************************************************

from math import degrees, log, pi, sqrt

import numpy as np
from scipy.optimize import curve_fit

from nicos import session
from nicos.commands import helparglist, usercommand
from nicos.commands.device import rmaw
from nicos.commands.measure import count
from nicos.commands.scan import manualscan

__all__ = ['AdjustCapillary']


def imgFit(im, rotation):
    def psdVgt(x, A1, mu1, w1, xc1, A2, mu2, w2, xc2, A3, mu3, w3, xc3, y0):
        return y0 + A1 * (
            mu1 * (2 / pi) * (w1 / (4 * (x - xc1)**2 + w1**2)) +
            (1 - mu1) * (sqrt(4 * log(2)) / (sqrt(pi) * w1)) *
            np.exp(-(4 * log(2) / w1**2) * (x - xc1)**2)) + \
            A2 * (
                mu2 * (2 / pi) * (w2 / (4 * (x - xc2)**2 + w2**2)) +
                (1 - mu2) * (sqrt(4 * log(2)) / (sqrt(pi) * w2)) *
                np.exp(-(4 * log(2) / w2**2) * (x - xc2)**2)) + \
            A3 * (
                mu3 * (2 / pi) * (w3 / (4 * (x - xc3)**2 + w3**2)) +
                (1 - mu3) * (sqrt(4 * log(2)) / (sqrt(pi) * w3)) *
                np.exp(-(4 * log(2) / w3**2) * (x - xc3)**2))

    roi = session.getDevice('roi').roi
    if rotation in [90, 270]:
        roi = [roi[1], roi[0], roi[3], roi[2]]
    session.log.debug('ROI: %s (%s)', roi, session.getDevice('roi').roi)
    lower_limit = roi[0]
    upper_limit = lower_limit + roi[2]
    mid = (lower_limit + upper_limit) / 2
    session.log.debug('%s - %s, %s', lower_limit, upper_limit, mid)
    psdVgt_bounds = ([1500, 0, 0, lower_limit,
                      -100, 0, 0, lower_limit,
                      1500, 0, 0, lower_limit, 0],
                     [2500, 1, 10, upper_limit,
                      2500, 1, 10, upper_limit,
                      2500, 1, 10, upper_limit, 10])

    p0_init = (2500, 1, 5, mid,
               500, 1, 5, mid,
               2500, 1, 5, mid, 0)

    x_fit = []
    y_fit = []
    x_data = np.linspace(lower_limit, upper_limit - 1,
                         (upper_limit - lower_limit))
    stepsize = 10
    for xline in range(roi[1], roi[1] + roi[3], stepsize):
        max_y = im[lower_limit:upper_limit, xline].max()
        y_data = max_y - im[lower_limit:upper_limit, xline]

        try:
            popt, _pcov = curve_fit(
                psdVgt, x_data, y_data, p0=p0_init, bounds=psdVgt_bounds,
                method='trf')

            residuals = y_data - psdVgt(x_data, *popt)
            ss_res = np.sum(residuals**2)
            ss_tot = np.sum((y_data - np.mean(y_data))**2)
            r_squared = 1 - ss_res / ss_tot
            if r_squared >= 0.95:
                x_fit.append(xline)
                y_fit.append((popt[3] + popt[7] + popt[11]) / 3)
                p0_init = popt
            else:
                session.log.debug('xline: %s, len y_data %s, r_squared: %s',
                                  xline, len(y_data), r_squared)
                y_data = np.ndarray.tolist(y_data)
                p0_init = (
                    2500, 1, 5, x_data[int(y_data.index(max(y_data)))],
                    500, 1, 5, x_data[int(y_data.index(max(y_data)))],
                    2500, 1, 5, x_data[int(y_data.index(max(y_data)))],
                    0)
        except Exception as e:
            session.log.warning('Error: %s', e)

    m, t = np.polyfit(x_fit, y_fit, 1)
    x_fit = np.array(x_fit)
    return m, t, x_fit


@helparglist('')
@usercommand
def AdjustCapillary():
    """Adjust a capillary to be centered against the sample table rotation.

    First the rotation will be adjusted. There are 4 pictures (at 0, 90, 180,
    and 270 deg) taken by rotating the sample table rotation device `omgs`.
    From these pictures the corrections of the tilting angle devices `rx` and
    `ry` are calculated and both devices will be moved.

    In a next step again 4 pictures will be taken at the same angles as
    before and from them the correction of the translation devices 'x' and 'y'
    will be calculated and the devices will be moved to these positions.

    In a final step the sample table rotation will be moved to 0 (zero) deg.
    """

    imgrot = session.getDevice('keyence').rotation
    pixsize = session.getDevice('keyence').pixel_size[0]

    def grab_data(roi=None):
        if roi is None:
            roi = session.getDevice('roi').roi
        det = session.getDevice('det')
        if imgrot == 0:
            return det.readArrays('final')[0]
        return np.rot90(det.readArrays('final')[0], (4 - imgrot // 90) % 4)

    def calcAngle(im, angle):
        m, _t, _x_fit = imgFit(im, imgrot)
        alpha = degrees(np.arctan(m))
        session.log.debug('Gradient %.2f°: %.3f', angle, alpha)
        return alpha

    def calcPos(im, angle):
        m, t, x_fit = imgFit(im, imgrot)
        pos = m * (min(x_fit) + max(x_fit)) / 2 + t
        session.log.debug('Position %.2f°: %.3f', angle, pos)
        return pos

    def scan(func, angles):
        number_of_frames = len(angles)
        fitted_values = [0] * number_of_frames
        omgs = session.getDevice('omgs')
        roi = session.getDevice('roi').roi
        with manualscan(omgs):
            omgs.maw(angles[0])  # move to first angle
            for i in range(number_of_frames):
                omgs.wait()  # wait for moving device
                # The detector hardware has a fixed exposure time which can't
                # be changed (for now). There is a 100 us exposure time + 2 s
                # of transfer time
                count(t=0)
                if i < (number_of_frames - 1):
                    omgs.move(angles[i + 1])  # move to next angle to save time
                fitted_values[i] = func(grab_data(roi), angles[i])
        return fitted_values

    number_of_frames = 4

    angles = scan(calcAngle, np.linspace(0, 270, number_of_frames))
    ry_value = (angles[0] - angles[2]) / 2
    rx_value = (angles[3] - angles[1]) / 2
    session.log.info("Adjust 'ry' by %s, 'rx' by %s)",
                     session.getDevice('ry').format(ry_value, True),
                     session.getDevice('rx').format(rx_value, True))
    rmaw('ry', ry_value, 'rx', rx_value)

    positions = scan(calcPos, np.linspace(270, 0, number_of_frames))
    ry_value = -((positions[3] - positions[1]) / 2) * pixsize
    rx_value = -((positions[0] - positions[2]) / 2) * pixsize
    session.log.info("Adjust: 'y' by %s, 'x' by %s)",
                     session.getDevice('y').format(ry_value, True),
                     session.getDevice('x').format(rx_value, True))
    rmaw('y', ry_value, 'x', rx_value)
    session.getDevice('omgs').maw(0)
    count(t=0)
