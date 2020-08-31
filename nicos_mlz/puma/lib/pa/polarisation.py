# -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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
#   Goetz Eckold <geckold@gwdg.de>
#
# *****************************************************************************

from __future__ import absolute_import, division, print_function

from math import degrees, pi, radians, tan

from numpy import arange, arcsin

from .analyzer import anaeff
from .deflector import ddefl, rdefl
from .gauss import gaussian
from .xa import xA


class PA:

    kf = 2.662  # wavevector of scattered neutrons / A-1
    da = 3.354  # netplane distance of analyser / A
    alpha0 = 0.5  # divergency of incident collimator / deg
    eta = 0.4  # mosaicity of anaylser crystals / deg
    lsa = 100.  # distance sample-analyzer axes / cm
    lsd1 = 20.  # sample-deflector 1 / cm
    lsd2 = 25.  # distance sample-deflector 2 / cm
    lpsd = 150.  # distance sample - PSD / cm
    gamma1 = -0.8  # deflector angle 1 / deg
    gamma2 = 0.7  # deflector angle 2 / deg
    theta05 = -19.2  # analyzer angle / deg
    theta06 = -20.6  # analyzer angle / deg
    theta07 = -22.2  # analyzer angle / deg
    y05 = -7.  # longitudinal displacement of analyzer 5 / cm
    y06 = 0.  # longitudinal displacement of analyzer 6 / cm
    y07 = 8.4  # longitudinal displacement of analyzer 7 / cm
    x05 = 2.  # transverse displacement of analyzer 5 / cm
    x06 = 0.  # transverse displacement of analyzer 6 / cm
    x07 = -2.  # transverse displacement of analyzer 7 / cm
    bS = 0.2  # width of sample slit / cm
    bA = 2.5  # width of analyzer blade / cm
    L = 4.  # length of deflector / cmalpha
    d = 0.055  # thickness of wafers / cm
    R = 0.9  # peak reflectivity of analysers
    psdwidth = 0.07  # PSD channel width in cm

    def __init__(self, **kwds):
        self.update(**kwds)

    def update(self, **kwds):
        if 'kf' in kwds:
            self.kf = kwds['kf']
        if 'dA' in kwds:
            self.da = kwds['dA']
        if 'alpha0' in kwds:
            self.alpha0 = kwds['alpha0']
        if 'eta' in kwds:
            self.eta = kwds['eta']
        if 'LSA' in kwds:
            self.lsa = kwds['LSA']
        if 'LSD1' in kwds:
            self.lsd1 = kwds['LSD1']
        if 'LSD2' in kwds:
            self.lsd2 = kwds['LSD2']
        if 'LPSD' in kwds:
            self.lpsd = kwds['LPSD']
        if 'gamma1' in kwds:
            self.gamma1 = kwds['gamma1']
        if 'gamma2' in kwds:
            self.gamma2 = kwds['gamma2']
        if 'theta06' in kwds:
            self.theta06 = kwds['theta06']
        if 'theta05' in kwds:
            self.theta05 = kwds['theta05']
        if 'theta07' in kwds:
            self.theta07 = kwds['theta07']
        if 'y05' in kwds:
            self.y05 = kwds['y05']
        if 'y06' in kwds:
            self.y06 = kwds['y06']
        if 'y07' in kwds:
            self.y07 = kwds['y07']
        if 'x05' in kwds:
            self.x05 = kwds['x05']
        if 'x06' in kwds:
            self.x06 = kwds['x06']
        if 'x07' in kwds:
            self.x07 = kwds['x07']
        if 'bS' in kwds:
            self.bS = kwds['bS']
        if 'bA' in kwds:
            self.bA = kwds['bA']
        if 'L' in kwds:
            self.L = kwds['L']
        if 'd' in kwds:
            self.d = kwds['d']
        if 'R' in kwds:
            self.R = kwds['R']
        if 'psdwidth' in kwds:
            self.psdwidth = kwds['psdwidth']

    def run(self):
        """Calculate profiles/intensities of polarisation analysis setup."""

        self.psdup = [0] * 202
        self.psddown = [0] * 202
        self.psdupa = [0] * 202
        self.psddowna = [0] * 202

        amp = 1.
        xc = 0.
        self.theta0 = theta0 = -degrees(arcsin(pi / (self.kf * self.da)))
        nxp = int(self.bS / self.psdwidth) + 1
        nalpha = 201
        _range = 4. * self.alpha0

        i5up = 0.
        i6up = 0.
        i7up = 0.
        i5down = 0.
        i6down = 0.
        i7down = 0.
        w_c = [gaussian(amp, xc, self.alpha0,
               -_range / 2. + j * _range / (nalpha - 1))
               for j in range(nalpha)]

        for i in range(nxp):
            xp = -self.bS / 2 + self.bS * i / (nxp - 1)
            for j in range(nalpha):
                alpha = -_range / 2. + j * _range / (nalpha - 1)
                # transmission of the collimator
                wc = w_c[j]

                # considering effect of first deflector

                # reflectivity for neutrons with divergence angle alpha
                r1up = rdefl(self.gamma1 - alpha, 1) - \
                    ddefl(self.gamma1, alpha, self.L, self.d, 1)
                r1down = rdefl(self.gamma1 - alpha, 2) - \
                    ddefl(self.gamma1, alpha, self.L, self.d, 2)

                # transmission for neutrons with divergence angle alpha
                t1up = 1 - r1up
                t1down = 1 - r1down

                # position of reflected beam on PSD
                xpsd1 = xA(alpha, self.gamma1, self.lpsd, self.lsd1, 0., xp, 1)
                xx = xpsd1 / self.psdwidth
                npsd1 = int(xx)
                if xpsd1 < 0:
                    npsd1 -= 1
                f1 = xx - float(npsd1) + 0.5
                npsd1 += 101

                # considering effect of second deflector
                # reflectivity for neutrons with divergence angle alpha
                r2up = rdefl(self.gamma2 - alpha, 1) - \
                    ddefl(self.gamma2, alpha, self.L, self.d, 1)
                r2down = rdefl(self.gamma2 - alpha, 2) - \
                    ddefl(self.gamma2, alpha, self.L, self.d, 2)

                # transmission for neutrons with divergence angle alpha
                t2up = 1 - r2up
                t2down = 1 - r2down

                # reflectivity for neutrons reflected by first deflector
                # having and divergence angle of 2*gamma1-alpha
                alpha1 = 2. * self.gamma1 - alpha
                r2upr1 = rdefl(self.gamma2 - alpha1, 1)
                r2downr1 = rdefl(self.gamma2 - alpha1, 2)

                # transmission for neutrons with divergence angle
                # 2*gamma1-alpha
                t2upr1 = 1 - r2upr1
                t2downr1 = 1 - r2downr1

                # position of reflected beam on PSD
                xpsd2 = xA(alpha, self.gamma2, self.lpsd, self.lsd2, 0., xp, 2)
                xx = xpsd2 / self.psdwidth
                npsd2 = int(xx)
                if xpsd2 < 0:
                    npsd2 -= 1
                f2 = xx - float(npsd2) + 0.5
                npsd2 += 101

                # probabilities of reflected beams
                w1up = wc * r1up * t2upr1
                w1down = wc * r1down * t2downr1
                w2up = wc * r2up * t1up
                w2down = wc * r2down * t1down

                # considering direct, transmitted or doubly reflected beam
                w0up = wc * t1up * t2up
                w0down = wc * t1down * t2down
                xpsd0 = xp + self.lpsd * tan(radians(alpha))
                xx = xpsd0 / self.psdwidth
                npsd0 = int(xx)
                if xpsd0 < 0:
                    npsd0 -= 1
                f0 = xx - float(npsd0) + 0.5
                npsd0 += 101

                # Determination of the PSD pattern without analyzers
                self.psdup[npsd1] += w1up * f1
                self.psdup[npsd1 - 1] += w1up * (1. - f1)
                self.psddown[npsd1] += w1down * f1
                self.psddown[npsd1 - 1] += w1down * (1. - f1)
                self.psdup[npsd2] += w2up * f2
                self.psdup[npsd2 - 1] += w2up * (1. - f2)
                self.psddown[npsd2] += w2down * f2
                self.psddown[npsd2 - 1] += w2down * (1. - f2)
                self.psdup[npsd0] += w0up * f0
                self.psdup[npsd0 - 1] += w0up * (1. - f0)
                self.psddown[npsd0] += w0down * f0
                self.psddown[npsd0 - 1] += w0down * (1. - f0)

                w51 = anaeff(theta0, self.theta05, self.gamma1, alpha,
                             self.lsa, self.lsd1, self.x05, self.y05, xp,
                             self.eta, self.bA, self.R, 1)
                w52 = anaeff(theta0, self.theta05, self.gamma2, alpha,
                             self.lsa, self.lsd2, self.x05, self.y05, xp,
                             self.eta, self.bA, self.R, 2)
                w50 = anaeff(theta0, self.theta05, 0., alpha, self.lsa,
                             self.lsd1, self.x05, self.y05, xp, self.eta,
                             self.bA, self.R, 0)

                w71 = anaeff(theta0, self.theta07, self.gamma1, alpha,
                             self.lsa, self.lsd1, self.x07, self.y07, xp,
                             self.eta, self.bA, self.R, 1)
                w72 = anaeff(theta0, self.theta07, self.gamma2, alpha,
                             self.lsa, self.lsd2, self.x07, self.y07, xp,
                             self.eta, self.bA, self.R, 2)
                w70 = anaeff(theta0, self.theta07, 0., alpha, self.lsa,
                             self.lsd1, self.x07, self.y07, xp, self.eta,
                             self.bA, self.R, 0)

                w61 = anaeff(theta0, self.theta06, self.gamma1, alpha,
                             self.lsa, self.lsd1, self.x06, self.y06, xp,
                             self.eta, self.bA, self.R, 1)
                w62 = anaeff(theta0, self.theta06, self.gamma2, alpha,
                             self.lsa, self.lsd2, self.x06, self.y06, xp,
                             self.eta, self.bA, self.R, 2)
                w60 = anaeff(theta0, self.theta06, 0., alpha, self.lsa,
                             self.lsd1, self.x06, self.y06, xp, self.eta,
                             self.bA, self.R, 0)

                # Determination of the PSD pattern with analyzers
                self.psdupa[npsd1] += w1up * (1 - w51) * (1. - w61) * \
                    (1. - w71)
                self.psddowna[npsd1] += w1down * (1 - w51) * (1. - w61) * \
                    (1. - w71)
                self.psdupa[npsd2] += w2up * (1 - w52) * (1. - w62) * \
                    (1. - w72)
                self.psddowna[npsd2] += w2down * (1 - w52) * (1. - w62) * \
                    (1. - w72)
                self.psdupa[npsd0] += w0up * (1 - w50) * (1. - w60) * \
                    (1. - w70)
                self.psddowna[npsd0] += w0down * (1 - w50) * (1. - w60) * \
                    (1. - w70)

                i5up += w1up * w51 + w2up * w52 + w0up * w50
                i6up += w1up * w61 + w2up * w62 + w0up * w60
                i7up += w1up * w71 + w2up * w72 + w0up * w70
                i5down += w1down * w51 + w2down * w52 + w0down * w50
                i6down += w1down * w61 + w2down * w62 + w0down * w60
                i7down += w1down * w71 + w2down * w72 + w0down * w70

        # calculate integrated PSD-intensities
        self.psdintup = sum(self.psdup)
        self.psdintupa = sum(self.psdupa)
        self.psdintdown = sum(self.psddown)
        self.psdintdowna = sum(self.psddowna)

        self.fractionup = 1. - self.psdintupa / self.psdintup
        self.fractiondown = 1. - self.psdintdowna / self.psdintdown
        self.igesup = i5up + i6up + i7up
        self.ratioup = (i5up + i7up) / self.igesup
        self.igesdown = i5down + i6down + i7down
        self.ratiodown = (i5down + i7down) / self.igesdown

        self.i5up = i5up
        self.i6up = i6up
        self.i7up = i7up
        self.i5down = i5down
        self.i6down = i6down
        self.i7down = i7down
        self.reflup = []
        self.refldown = []
        for x in arange(-2, 2.01, 0.1):
            self.reflup.append(rdefl(x, 1))
            self.refldown.append(rdefl(x, 2))


if __name__ == '__main__':
    def read():
        ret = {}
        with open('PolData_In.txt') as f:
            for line in f.readlines():
                key, value = line.split('=')
                ret[key.strip()] = float(value.strip())
        return ret

    def write(pa):
        with open('PolData_Out.txt', 'w') as f:
            f.write('Parameter-List:\n')
            f.write('wavevector of scattered neutrons     : %6.3f 1/A\n' % pa.kf)
            f.write('netplane-distance of analyzer        : %6.3f A\n' % pa.da)
            f.write('Bragg-angle of analyzer              : %6.2f deg\n' %
                    pa.theta0)
            f.write('collimator-divergency                : %5.2f deg\n' %
                pa.alpha0)
            f.write('analyzer-mosaicity                   : %5.2f deg\n' % pa.eta)
            f.write('distance sample-analyzer             : %6.1f cm\n' % pa.lsa)
            f.write('distance sample-deflector 1          : %6.2f cm\n' % pa.lsd1)
            f.write('distance sample-deflector 2          : %6.2f cm\n' % pa.lsd2)
            f.write('tilt-angle deflector 1               : %5.2f, deg\n' %
                    pa.gamma1)
            f.write('tilt-angle deflector 2               : %5.2f, deg\n' %
                    pa.gamma2)
            f.write('tilt-angles analyzers 5,6,7          : %8.2f deg%8.2f deg'
                    '%8.2f deg\n' % (pa.theta05, pa.theta06, pa.theta07))
            f.write('lateral analyzer- displacements      : %5.1f cm%5.1f cm'
                    '%5.1f cm\n' % (pa.x05, pa.x06, pa.x07))
            f.write('longitudinal analyzer- displacements : %5.1f cm%5.1f cm'
                    '%5.1f cm\n' % (pa.y05, pa.y06, pa.y07))
            f.write('width of sample-slit                 : %4.1f cm\n' % pa.bS)
            f.write('width of analyzer blade              : %4.1f cm\n\n' % pa.bA)

            f.write('\nSpin-up neutrons\n')
            f.write('total PSD intensity : %7.2f\n' % pa.psdintup)
            f.write('fraction detected : %5.2f\n' % pa.fractionup)
            f.write('intensities channels 5,6,7, total : %10.2f%10.2f%10.2f'
                    '%10.2f\n' % (pa.i5up, pa.i6up, pa.i7up,
                              pa.igesup))
            f.write('intensity ratio: %5.2f\n' % pa.ratioup)

            f.write('\nSpin-down neutrons\n')
            f.write('total PSD intensity : %7.2f\n' % pa.psdintdown)
            f.write('fraction detected : %5.2f\n' % pa.fractiondown)
            f.write('intensities channels 5,6,7, total : %10.2f%10.2f%10.2f'
                    '%10.2f\n' % (pa.i5down, pa.i6down, pa.i7down,
                                  pa.igesdown))
            f.write('intensity ratio: %5.2f\n' % pa.ratiodown)

            f.write('\nPSD-profiles:\n')
            f.write('PSD-Pos.     Spin-up             Spin-down\n')
            f.write('          with   without       with   without\n')
            f.write('            analyzer             analyzer\n')
            for i in range(1, 201 + 1):
                f.write('%6.2f  %8.3f%8.3f     %8.3f%8.3f\n' % (
                        (-101 + i) * pa.psdwidth, pa.psdup[i],
                        pa.psdupa[i], pa.psddown[i], pa.psddowna[i]))
            f.write('Reflectivity\n')
            f.write('angle   spin-up  spin-down\n')
            for i in range(1, 41 + 1):
                x = -2.1 + i * 0.1
                f.write('%5.1f   %7.2f  %7.2f\n' % (x, rdefl(x, 1), rdefl(x, 2)))


    pa = PA(**read())

    if False:  # pylint: disable=using-constant-test
        import cProfile
        cProfile.run('pa.run()')
    else:
        pa.run()

    write(pa)
