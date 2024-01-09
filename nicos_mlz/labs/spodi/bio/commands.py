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

__all__ = ['AdjustCapillary']


def imgFit(im):
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

    lower_limit = 750
    upper_limit = 1250
    psdVgt_bounds = ([1500, 0, 0, lower_limit,
                      -100, 0, 0, lower_limit,
                      1500, 0, 0, lower_limit, 0],
                     [2500, 1, 10, upper_limit,
                      2500, 1, 10, upper_limit,
                      2500, 1, 10, upper_limit, 10])

    mid = (lower_limit + upper_limit) / 2
    p0_init = (2500, 1, 5, mid,
               500, 1, 5, mid,
               2500, 1, 5, mid, 0)

    x_fit = []
    y_fit = []
    for xline in range(500, 1500, 10):
        x_data = np.linspace(lower_limit, upper_limit,
                             (upper_limit - lower_limit))
        max_y = max(im[lower_limit:upper_limit, xline])
        y_data = max_y - im[lower_limit:upper_limit, xline]

        try:
            popt, _pcov = curve_fit(
                psdVgt, x_data, y_data, p0=p0_init, bounds=psdVgt_bounds,
                method='trf')

            residuals = y_data - psdVgt(x_data, *popt)
            ss_res = np.sum(residuals**2)
            ss_tot = np.sum((y_data - np.mean(y_data))**2)
            r_squared = 1 - ss_res / ss_tot

            if r_squared >= 0.98:
                x_fit.append(xline)
                y_fit.append((popt[3] + popt[7] + popt[11]) / 3)
                p0_init = popt
            else:
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


def grab_data():
    return session.getDevice('det').readArrays('final')[0]


@helparglist('')
@usercommand
def AdjustCapillary():
    """Adjust a capillary to be centered against the sample table rotation.

    First the rotation will be adjusted. There are 4 pictures (at 0, 90, 180,
    and 270 deg) taken by rotating the sample table rotation device `omgs`.
    From these pictures the corrections of the tilting angle device `rx` and
    `ry` are calculated and both devices will be moved.

    In the next step again 4 pictures will be take at the same angles as
    before and from them the correction of the translation devices 'x' and 'y'
    will be calculated and the devices moved to these positions.

    In a final step the sample table rotation will be moved to 0 (zero) deg.
    """

    def calcAngle(im, angle):
        m, _t, _x_fit = imgFit(im)
        alpha = degrees(np.arctan(m))
        session.log.info('Gradient %.2f°: %.3f', angle, alpha)
        return alpha

    def calcPos(im, angle):
        m, t, x_fit = imgFit(im)
        pos = m * (min(x_fit) + max(x_fit)) / 2 + t
        session.log.info('Position %.2f°: %.3f', angle, pos)
        return pos

    def scan(func, angles):
        number_of_frames = len(angles)
        fitted_values = [0] * number_of_frames
        omgs = session.getDevice('omgs')
        omgs.maw(angles[0])  # move to first angle
        for i in range(number_of_frames):
            omgs.wait()  # wait for moving device
            session.log.info('%d/%d %.2f', i, number_of_frames, omgs.read())
            # The detector hardware has a fixed exposure time which can't be
            # changed (for now). There is a 100 us exposure time + 2 s of
            # transfer time
            count(t=0)
            if i < (number_of_frames - 1):
                omgs.move(angles[i + 1])  # move to next angle to save time
            fitted_values[i] = func(grab_data(), angles[i])
        return fitted_values

    number_of_frames = 4

    angles = scan(calcAngle, np.linspace(0, 270, number_of_frames))
    ry_value = (angles[0] - angles[2]) / 2
    rx_value = (angles[3] - angles[1]) / 2
    session.log.info('result: rmaw(ry, %f, rx, %f)', ry_value, rx_value)
    rmaw(session.getDevice('ry'), ry_value, session.getDevice('rx'), rx_value)

    positions = scan(calcPos, np.linspace(270, 0, number_of_frames))
    ry_value = ((positions[3] - positions[1]) / 2) * 75 / 2048
    rx_value = ((positions[0] - positions[2]) / 2) * 75 / 2048
    session.log.info('result: rmaw(y, %f, x, %f)', -ry_value, -rx_value)
    rmaw(session.getDevice('y'), -ry_value, session.getDevice('x'), -rx_value)
