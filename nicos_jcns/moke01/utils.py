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

from nicos.utils.functioncurves import Curve2D, Curves


def fit_curve(curve, fittype):
    """MOKE-specific fitting function. Fitting result is a line.
    Returns (k, b), assuming the fit is y(x) = k * x + b"""

    fittypes = ['min', 'max']
    if fittype not in fittypes:
        return
    err = 0.025
    ymin, ymax = curve.ymin, curve.ymax
    emin = err if ymin >= 0 else -err
    emax = err if ymax >= 0 else -err
    y1 = [p.y for p in curve if ymin * (1 - emin) < p.y < ymin * (1 + emin)]
    y2 = [p.y for p in curve if ymax * (1 - emax) < p.y < ymax * (1 + emax)]
    y = y1 if fittype == 'min' else y2
    x = [p.x for p in curve if p.y in y]
    if x and y:
        return Curve2D.from_x_y(x, y).lsm()
    else:
        return 0, 0


def calc_ellipticity(imin, imax, ext, angle):
    """Calculates ellipticity values from intensity values."""

    if imin == imax:
        raise ValueError('calc_ellipticity(i, imin, imax) cannot be finished '
                         'when imin == imax. Check input data.')
    return (imax - imin) / ((imin + imax) / 2 - ext) * angle / 4


def scale_intensity(i, imin, imax, kerr):
    """Scales intensity value.
    """

    if imin == imax:
        raise ValueError('calc_ellipticity(i, imin, imax) cannot be finished '
                         'when imin == imax. Check input data.')
    return (i - (imin + imax) / 2) / (imax - imin) * 2 * kerr


def calculate(IntvB, angle, ext):
    """MOKE-specific measurement analysis."""

    # separate increasing and decreasing curves, mean them, and fit the means
    series = Curves.from_series(IntvB)
    IntvB = Curve2D()
    IntvB.append(series.increasing().mean())
    IntvB.append(series.decreasing().mean())
    fit_min = fit_curve(IntvB, 'min')
    fit_max = fit_curve(IntvB, 'max')

    # calculate kerr angle/ellipticity
    kerr = calc_ellipticity(fit_min[1], fit_max[1], ext, angle)

    # rescale intensity into ellipticity curves
    EvB = Curve2D()
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
    baseline = measurement['baseline']

    # Measurement settings
    output = f'Measurement name: {measurement["name"]}\n'
    output += f'Id: {measurement["id"]}\n'
    output += f'Description: {measurement["description"]}\n'
    output += f'Measurement time: {measurement["time"]}\n'
    output += f'Measurement type: {measurement["exp_type"]}\n'
    output += f'Measurement mode: {measurement["mode"]}\n'
    output += f'Field orientation: {measurement["field_orientation"]}\n'
    output += f'Power supply ramp: {measurement["ramp"]} [A/min]\n'
    output += f'Lower value of the field range Bmin: {measurement["Bmin"]} (T)\n'
    output += f'Upper value of the field range Bmax: {measurement["Bmax"]} (T)\n'
    output += f'Step size: {measurement["step"] if measurement["mode"] == "stepwise" else "n/a"} (T)\n'
    output += f'Step time: {measurement["steptime"] if measurement["mode"] == "stepwise" else "n/a"} (s)\n'
    output += f'Number of cycles: {measurement["cycles"]}\n\n'

    try:
        IntvB_sub = IntvB - baseline
    except Exception as e:
        IntvB_sub = IntvB
        output += f'Warning, subtraction of the baseline has failed:\n{str(e)}\n\n'
    # raw measurement output
    if not angle and not ext:
        output += 'Measured curves of intensity vs magnetic field:\n'
        output += 'I (A)\tdI (A)\t' \
                  'B (T)\tdB (T)\t' \
                  'Int (V)\tdInt (V)\t' \
                  'Int_subtracted (V)\tdInt_subtracted (V)\n'
        for (I, _), (B, Int), (_, Int_sub) in zip(BvI, IntvB, IntvB_sub):
            output += f'{I.n}\t{I.s}\t' \
                      f'{B.n}\t{B.s}\t' \
                      f'{Int.n}\t{Int.s}\t' \
                      f'{Int_sub.n}\t{Int_sub.s}\n'
    else:
        # analysis output
        try:
            fit_min, fit_max, IntvB_sub, EvB, kerr = calculate(IntvB_sub, angle, ext)
            output += f'Minimum intensity: {fit_min[1]} (V)\n'
            output += f'Maxmimum intensity: {fit_max[1]} (V)\n'
            output += f'Canting angle: {angle} (SKT)\n'
            output += f'Extinction: {ext} (V)\n'
            output += f'Kerr angle: {kerr} (mrad)\n\n'
            output += 'Mean intensity and ellipticity curves:\n'
            output += 'I (A)\tdI (A)\t' \
                      'B (T)\tdB (T)\t' \
                      'Int (V)\tdInt (V)\t' \
                      'Int_subtracted (V)\tdInt_subtracted (V)\t' \
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
