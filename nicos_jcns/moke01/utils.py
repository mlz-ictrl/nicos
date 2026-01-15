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
from random import randint

import numpy
import scipy

from nicos.utils.functioncurves import Curve2D, Curves, ufloat
from nicos.utils.functioncurves.calcs import mean


def fit_curve(curve, fittype):
    """MOKE-specific fitting function.
    It filters values on a curve of ``_/‾`` shape from min or max horizontal
    saturation areas to fit them into a line with least squares method.
    :param curve: ``_/‾`` shaped curve of class Curve2D
    :param fittype: ``'min'`` or ``'max'``
    :return: python tuple ``(k, b)`` for a fitting line y(x) = k * x + b
    """
    fittypes = ['min', 'max']
    if fittype not in fittypes:
        return
    m = Curves.from_series(curve).mean().yvx(0)
    curve_max = Curve2D([p for p in curve if p.y.n - p.y.s > m.y.n + m.y.s])
    curve_min = Curve2D([p for p in curve if p.y.n + p.y.s < m.y.n - m.y.s])
    c = curve_min if fittype == 'min' else curve_max
    e = mean(c.y)
    _filter = (lambda y: y < e) if fittype == 'min' else (lambda y: y > e)
    c = Curve2D([p for p in c if _filter(p.y)])
    return c.lsm()


def calc_kerr(imin, imax, int_mean, ext, angle):
    """Calculates kerr angle which is the rotation of the polarization plane of
    light that occurs when linearly polarized light reflects from a magnetized
    material.
    :param imin: lower intensity value obtained from ``fit_curve`` at 0 T
        magnetic field strength. The value can be taken from both raw and
        subtracted ``Int(B)`` curves [mV]
    :param imax: higher intensity value obtained from ``fit_curve`` at 0 T
        magnetic field strength. The value can be taken from both raw and
        subtracted ``Int(B)`` curves [mV]
    :param int_mean: mean intensity value at 0 T magnetic field strength, should
        only be taken from raw (non-subtracted) ``Int(B)`` curve [mV]
    :param ext: extinction voltage, a small residual intensity voltage measured
        when the optical system is adjusted to the point where, ideally,
        no light should reach the photodetector [mV]
    :param angle: canting angle is an angle between the magnetization vector and
        the sample plane [µrad]
    :return: Kerr angle [µrad]
    """
    if imin == imax:
        raise ValueError('calc_ellipticity(i, imin, imax) cannot be finished '
                         'when imin == imax. Check input data.')
    return (imax - imin) / (int_mean - ext) * angle / 4 # [µrad]


def scale_intensity(i, imin, imax, kerr):
    """Recalculates given intensity value into ellipticity value.
    :param i: intensity value to recalculate [mV]
    :param imin: lower intensity value obtained from ``fit_curve`` at 0 T
        magnetic field strength. The value can be taken from both raw and
        subtracted ``Int(B)`` curves [mV]
    :param imax: higher intensity value obtained from ``fit_curve`` at 0 T
        magnetic field strength. The value can be taken from both raw and
        subtracted ``Int(B)`` curves [mV]
    :param kerr: Kerr angle [µrad]
    :return: ellipticity value [µrad]
    """
    if imin == imax:
        raise ValueError('calc_ellipticity(i, imin, imax) cannot be finished '
                         'when imin == imax. Check input data.')
    return (i - (imin + imax) / 2) / (imax - imin) * 2 * kerr # [µrad]


def calculate(IntvB, int_mean, angle, ext, fit_min=None, fit_max=None):
    """High-level function to execute MOKE analysis: fit curves if necessary,
    calculate kerr angle and recalculate intensity curves into ellipticity
    curves.
    :param IntvB: ``Int(B)`` curve of class Cyrve2D, can be both raw and
        subtracted curve.
    :param int_mean: mean intensity value at 0 T magnetic field strength, should
        only be taken from raw (non-subtracted) ``Int(B)`` curve [mV]
    :param angle: canting angle is an angle between the magnetization vector and
        the sample plane [µrad]
    :param ext: extinction voltage, a small residual intensity voltage measured
        when the optical system is adjusted to the point where, ideally,
        no light should reach the photodetector [mV]
    :param fit_min: python tuple ``(k, b)`` for a fitting line y(x) = k * x + b
        of min horizontal saturation area
    :param fit_max: python tuple ``(k, b)`` for a fitting line y(x) = k * x + b
        of min horizontal saturation area
    :return: python tuple of ``(fit_min, fit_max, IntvB, EvB, kerr)``
    """
    if fit_min is None:
        fit_min = fit_curve(IntvB, 'min') # [mV]
    if fit_max is None:
        fit_max = fit_curve(IntvB, 'max') # [mV]
    # calculate kerr angle in [µrad]
    kerr = calc_kerr(fit_min[1], fit_max[1], int_mean, ext, angle)

    # separate increasing and decreasing curves and mean them
    curves = Curves.from_series(IntvB) # ([mT, mV])
    IntvB = Curve2D()
    IntvB.append(curves.increasing().mean())
    IntvB.append(curves.decreasing().mean())
    # rescale intensity into ellipticity curves
    EvB = Curve2D() # ([mT, µrad])
    for B, Int in IntvB:
        EvB.append((B, scale_intensity(Int, fit_min[1], fit_max[1], kerr)))

    return fit_min, fit_max, IntvB, EvB, kerr


def generate_output(measurement, angle=None, ext=None, fit_min=None, fit_max=None):
    """Generates two type of output:
    1. only measurement settings with raw and subtracted ``B(I)`` and ``Int(B)``
    curves;
    2. measurement settings and analysis data, such as mean (by number of
    cycles) ``Int(B)`` and ``E(B)`` curves and Kerr angle.
    :param measurement: python dict object that collects necessary measurement
        information
    :param angle: canting angle is an angle between the magnetization vector and
        the sample plane [µrad]
    :param ext: extinction voltage, a small residual intensity voltage measured
        when the optical system is adjusted to the point where, ideally,
        no light should reach the photodetector [mV]
    :param fit_min: python tuple ``(k, b)`` for a fitting line y(x) = k * x + b
        of min horizontal saturation area
    :param fit_max: python tuple ``(k, b)`` for a fitting line y(x) = k * x + b
        of min horizontal saturation area
    :return: ASCII data table
    """
    keys = ['name', 'time', 'IntvB', 'exp_type', 'mode', 'ramp', 'Bmin', 'Bmax',
            'cycles', 'BvI', 'baseline', 'field_orientation', 'id',
            'description', 'calfac']
    if not measurement or not all(key in measurement.keys() for key in keys):
        return ''
    BvI = measurement['BvI']
    IntvB = measurement['IntvB']
    int_mean = IntvB.series_to_curves().mean().yvx(0)
    baseline = measurement['baseline']
    calfac = measurement['calfac']

    # Measurement settings
    output = f'Measurement name: {measurement["name"]}\n'
    output += f'Sample id: {measurement["id"]}\n'
    output += f'Description: {measurement["description"]}\n'
    output += f'Measurement start time: {measurement["time"]}\n'
    output += f'Measurement type: {measurement["exp_type"]}\n'
    output += f'Measurement mode: {measurement["mode"]}\n'
    output += f'Calibration factor: {calfac}\n'
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
        data = [['I (A)', 'B (mT)', 'dB (mT)', 'Int (mV)', 'dInt (mV)',
                 'Int_subtracted (mV)', 'dInt_subtracted (mV)']]
        for (I, _), (B, Int), (_, Int_sub) in zip(BvI, IntvB, IntvB_sub):
            data.append([I.n, B.n, B.s, Int.n, Int.s, Int_sub.n, Int_sub.s])
        output += asciitable(data)
    else:
        # analysis output
        try:
            fit_min, fit_max, IntvB_sub, EvB, kerr = calculate(IntvB_sub, int_mean.y, angle, ext, fit_min, fit_max)
            output += f'Intensity min: {fit_min[1]:.3f} mV\n'
            output += f'Intensity max: {fit_max[1]:.3f} mV\n'
            output += f'Canting angle: {angle / (1.5 / 25 / 180 * math.pi * 1e6)} (SKT)' \
                      f' {angle / 1000 :.3f} (mrad)\n'
            output += f'Extinction: {ext} (mV)\n'
            output += f'Kerr angle: {kerr} (µrad)\n\n'
            output += 'Mean intensity and ellipticity curves:\n'
            data = [['I (A)', 'B (mT)', 'dB (mT)', 'Int (mV)', 'dInt (mV)',
                     'Int_subtracted (mV)', 'dInt_subtracted (mV)',
                     'E (µrad)', 'dE (µrad)']]
            for (I, _), (B, Int), (_, Int_sub), (_, E) in \
                    zip(BvI[:len(IntvB_sub)], IntvB, IntvB_sub, EvB):
                data.append([I.n, B.n, B.s, Int.n, Int.s,
                             Int_sub.n, Int_sub.s, E.n, E.s])
            output += asciitable(data)
        except Exception as e:
            output += f'Warning, calculation has failed:\n{str(e)}\n\n'
    return output


def fix_filename(filename):
    """Restrict filename string to limited amount of symbols.
    :param filename: desired filename
    :return: allowed filename
    """
    allowed = [ord(' '), ord('_'), ord('-')]
    allowed += range(ord('0'), ord('9'))
    allowed += range(ord('A'), ord('Z'))
    allowed += range(ord('a'), ord('z'))

    res = ''
    for l in filename:
        res += l if ord(l) in allowed else '-'
    return res


def asciitable(data):
    """Creates custom ASCII table. Column widths are adjusted to fit entries.
    All columns are aligned by right.
    :param data: 2D python list that contains headers and values of a table
    :return: a python string containing an ASCII formatted table
    """
    res = ''
    if data:
        widths = [0] * len(data[0])
        for row in data:
            for i, col in enumerate(row):
                if isinstance(col, (float, int)):
                    row[i] = f'{col:.3f}'
                widths[i] = max(widths[i], len(str(row[i])))
        for row in data:
            for i, (w, col) in enumerate(zip(widths, row)):
                res += f'{col:>{w}}   '
            res += '\n'
    return res


def generate_intvb(Bmin, Bmax):
    """Generates two ``Int(B)`` curves to account for hysteresis for a given
    magnetic field range, similar to what can be obtained in a real MOKE
    experiment.
    The curves are generated using an error function having some randomized
    input to affect its shape. The values have randomized jitter and instrument
    error. Finally, the error functions are distorted by adding to them random
    small linear component.
    :param Bmin: minimum value of the magnetic field range
    :param Bmax: minimum value of the magnetic field range
    :return: two Curve2D ``Int(B)`` curves wrapped in Curves class
    """
    # width of hysteresis
    width = randint(5, 15) / 10
    # how sharp is the rise
    sharp = randint(10, 20) / 1e3
    # take 100 data points for the range
    x = numpy.linspace(Bmin, Bmax, 100, True)
    # increasing curve with random jitter
    y1 = (scipy.special.erf(x * sharp + width) / 20 + 1.65) * 1e3
    y1 = [ufloat(y * (randint(1, 10) / 1e4 + 1), randint(1, 10) / 1000) for y in y1]
    # decreasing curve with random jitter
    y2 = (scipy.special.erf(x * sharp - width) / 20 + 1.649) * 1e3
    y2 = [ufloat(y * (randint(1, 10) / 1e4 + 1), randint(1, 10) / 1000) for y in y2]
    IntvB = Curves([Curve2D.from_x_y(x, y1), Curve2D.from_x_y(x[::-1], y2[::-1])])
    # random inclination
    k = randint(0, 20) / 1e3
    x = numpy.array([Bmin, Bmax])
    y = k * x
    line = Curve2D.from_x_y(x, y)
    return Curves([IntvB[0] + line, IntvB[1] + line])
