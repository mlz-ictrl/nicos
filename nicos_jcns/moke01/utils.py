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
#   Konstantin Kholostov <k.kholostov@fz-juelich.de>
#
# *****************************************************************************

import math

from nicos.utils.functioncurves import Curve2D, Curves
from nicos.utils.functioncurves.calcs import mean


def fit_curve(curve, fittype):
    """MOKE-specific fitting function. Fitting result is a line.
    Returns (k, b), assuming the fit is y(x) = k * x + b"""

    fittypes = ['min', 'max']
    if fittype not in fittypes:
        return
    curve_max = Curve2D([p for p in curve if p.x > 0])
    curve_min = Curve2D([p for p in curve if p.x < 0])
    if curve_max.ymax < curve_min.ymax:
        curve_min, curve_max = curve_max, curve_min
    c = curve_min if fittype == 'min' else curve_max
    e = mean(c.y)
    c = Curve2D([p for p in c if e.n - e.s < p.y.n < e.n + e.s])
    return c.lsm()


def calc_ellipticity(imin, imax, int_mean, ext, angle):
    """Calculates ellipticity values from intensity values."""

    if imin == imax:
        raise ValueError('calc_ellipticity(i, imin, imax) cannot be finished '
                         'when imin == imax. Check input data.')
    return (imax - imin) / (int_mean - ext) * angle / 4 # [µrad]


def scale_intensity(i, imin, imax, kerr):
    """Scales intensity value.
    """

    if imin == imax:
        raise ValueError('calc_ellipticity(i, imin, imax) cannot be finished '
                         'when imin == imax. Check input data.')
    return (i - (imin + imax) / 2) / (imax - imin) * 2 * kerr # [µrad]


def calculate(IntvB, int_mean, angle, ext):
    """MOKE-specific measurement analysis."""

    # separate increasing and decreasing curves, mean them, and fit the means
    curves = Curves.from_series(IntvB) # ([mT, mV])
    IntvB = Curve2D()
    IntvB.append(curves.increasing().mean())
    IntvB.append(curves.decreasing().mean())
    fit_min = fit_curve(IntvB, 'min') # [mV]
    fit_max = fit_curve(IntvB, 'max') # [mV]

    # calculate kerr angle/ellipticity in [µrad]
    kerr = calc_ellipticity(fit_min[1], fit_max[1], int_mean, ext, angle)

    # rescale intensity into ellipticity curves
    EvB = Curve2D() # ([mT, µrad])
    for B, Int in IntvB:
        EvB.append((B, scale_intensity(Int, fit_min[1], fit_max[1], kerr)))

    return fit_min, fit_max, IntvB, EvB, kerr


def generate_output(measurement, angle=None, ext=None):
    """Generates 2 type of output:
    1. measurement settings with full measurement curve of intensity vs.
    magnetic field;
    2. measurement and analysis settings, mean (by number of cycles) intensity
    vs. magnetic field curve, calculated ellipticity vs. magnetic field curve
    and output parameter kerr."""

    keys = ['name', 'time', 'IntvB', 'exp_type', 'mode', 'ramp', 'Bmin', 'Bmax',
            'cycles', 'BvI', 'baseline', 'field_orientation', 'id', 'description']
    if not measurement or not all(key in measurement.keys() for key in keys):
        return ''
    BvI = measurement['BvI']
    IntvB = measurement['IntvB']
    int_mean = IntvB.series_to_curves().amean().yvx(0)
    baseline = measurement['baseline']

    # Measurement settings
    output = f'Measurement name: {measurement["name"]}\n'
    output += f'Sample id: {measurement["id"]}\n'
    output += f'Description: {measurement["description"]}\n'
    output += f'Measurement start time: {measurement["time"]}\n'
    output += f'Measurement type: {measurement["exp_type"]}\n'
    output += f'Measurement mode: {measurement["mode"]}\n'
    output += f'Field orientation: {measurement["field_orientation"]}\n'
    output += f'Power supply ramp: {measurement["ramp"]} [A/min]\n'
    output += f'Bmin: {measurement["Bmin"]} (mT)\n'
    output += f'Bmax: {measurement["Bmax"]} (mT)\n'
    output += f'Step size: {measurement["step"] if measurement["mode"] == "stepwise" else "n/a"} (mT)\n'
    output += f'Step time: {measurement["steptime"] if measurement["mode"] == "stepwise" else "n/a"} (s)\n'
    output += f'Number of cycles planned: {measurement["cycles"]}\n'
    output += f'Number of cycles completed: {int(math.floor(len(Curves.from_series(IntvB)) / 2))}\n\n'

    try:
        IntvB_sub = IntvB - baseline - int_mean.y
    except Exception as e:
        IntvB_sub = IntvB
        output += f'Warning, subtraction of the baseline has failed:\n{str(e)}\n\n'
    if not angle and not ext:
        # raw measurement output
        output += 'Measured curves of intensity vs magnetic field:\n'
        output += 'I (A)\tdI (A)\t' \
                  'B (mT)\tdB (mT)\t' \
                  'Int (mV)\tdInt (mV)\t' \
                  'Int_subtracted (mV)\tdInt_subtracted (mV)\n'
        for (I, _), (B, Int), (_, Int_sub) in zip(BvI, IntvB, IntvB_sub):
            output += f'{I.n}\t{I.s}\t' \
                      f'{B.n}\t{B.s}\t' \
                      f'{Int.n}\t{Int.s}\t' \
                      f'{Int_sub.n}\t{Int_sub.s}\n'
    else:
        # analysis output
        try:
            _, _, IntvB_sub, EvB, kerr = calculate(IntvB_sub, int_mean.y, angle, ext)
            output += f'Canting angle: {angle / (1.5 / 25 / 180 * math.pi * 1e6)} (SKT)' \
                      f' {angle / 1000 :.3f} (mrad)\n'
            output += f'Extinction: {ext} (mV)\n'
            output += f'Kerr angle: {kerr} (µrad)\n\n'
            output += 'Mean intensity and ellipticity curves:\n'
            output += 'I (A)\tdI (A)\t' \
                      'B (mT)\tdB (mT)\t' \
                      'Int (mV)\tdInt (mV)\t' \
                      'Int_subtracted (mV)\tdInt_subtracted (mV)\t' \
                      'E (a.u.)\tdE (a.u.)\n'
            for (I, _), (B, Int), (_, Int_sub), (_, E) in \
                    zip(BvI[:len(IntvB_sub)], IntvB, IntvB_sub, EvB):
                output += f'{I.n}\t{I.s}\t' \
                          f'{B.n}\t{B.s}\t' \
                          f'{Int.n}\t{Int.s}\t' \
                          f'{Int_sub.n}\t{Int_sub.s}\t' \
                          f'{E.n}\t{E.s}\n'
        except Exception as e:
            output += f'Warning, calculation has failed:\n{str(e)}\n\n'
    return output


def fix_filename(filename):
    """Restrict filename string to limited amount of symbols.
    """
    allowed = [ord(' '), ord('_'), ord('-')]
    allowed += range(ord('0'), ord('9'))
    allowed += range(ord('A'), ord('Z'))
    allowed += range(ord('a'), ord('z'))

    res = ''
    for l in filename:
        res += l if ord(l) in allowed else '-'
    return res
