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
#   Tobias Unruh <tobias.unruh@frm2.tum.de>
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""TOFTOF chopper and resolution calculations."""

from math import cos, pi, radians, sqrt

import numpy as np

try:
    from scipy import constants
    h = constants.Planck
    mn = constants.neutron_mass
    e = constants.elementary_charge
    hbar = constants.hbar
except ImportError:
    h = 6.62606896e-34                  # Planck constant [Js]
    mn = 1.674927211e-27                # Neutron mass [kg]
    e = 1.602176487e-19                 # Elementary charge [C]
    hbar = h / (2 * pi)                 # h-bar

# in us (1e6) / AA (1e-10) / m
alpha = 1e6 * (mn / h) / 1e10           # Should be 252.7784


def sgn(x):
    return -1 if x < 0 else 1


# *** TOFTOF specific constants ***

# time resolution of the TOF electronics is 50 ns
ttr = 5.0e-8

# a[0]:   distance chopper1 - sample in m
# a[1-7]: distance chopper1 - chopperX in m
a = (11.4, 0.0, 0.1, 3.397, 7.953, 8.028, 9.925, 10.0)

Lsd = 4                                 # flight distance sample-detector
Lpm = a[7] - a[1]                       # flight distance chopper1-chopper7
Lms = a[0] - a[7]                       # flight distance chopper7-sample
Lpre_sample = a[0] - a[5]

# offsets of chopper zero position in deg (definition of the sign is unknown
# chopperOffset = (0.00, 0.00, -0.25, 0.45, 0.39, -0.25, 0.13, 0.36)
# 02.12.2009
# chopperOffset = (0.00, 0.00, -0.06, 0.45, 0.39, -0.25, -0.81, 0.36)
chopperOffset = (0.00, 0.00, 0.00, 0.0, 0.0, 0.0, 0.70, 0.70)

# signs for counter-rotating ch1/2 and ch6/7 (all others run like chopper1)
# sigmaxcrc = (0.0, 1.0, -1.0, -1.0, -1.0, 1.0, -1.0, -1.0)
sigmaxcrc = (0.0, 1.0, -1.0, -1.0, -1.0, 1.0, -1.0, -1.0)

# signs for normally rotating ch1/2 and ch6/7 (all others run like chopper1)
sigmax = (0.0, 1.0, 1.0, -1.0, -1.0, 1.0, -1.0, 1.0)    # pronounce: sigma x

# phases for different slit types
# for the large(g)/large(g) there are no offsets and slit type is 0
# for slit type 1 small(k)/small(k)
st0 = (0.0, 0.0, 0.0, -90.0, -90.0, 90.0, 0.0, 0.0)
# for slit type 2 small(g)/small(k)
st1 = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 90.0, -90.0)

# instrument parameters and constants

low_angle = 7.5915 / 2
high_angle = 139.186 / 2
Ls = 0.02


def speedRatio(ratio=1):
    if ratio in [2, 3, 4, 5, 6, 7, 8]:
        return (ratio - 1.0) / float(ratio)
    elif ratio in [9, 10]:
        return 7.0 / float(ratio)
    return 1.0


def calculateChopperDelay(wl, speed, ratio, st, ch5_90deg_offset):
    # note: unknown time unit, suspect microseconds
    chdelay = 0
    ratio2 = speedRatio(ratio)
    # calculate the speed in Hz instead of given speed in rpms
    speed /= 60.0
    if ch5_90deg_offset:  # chopper 5 90 deg rotated
        chdelay = -1.e6 / (ratio2 * (4 * speed))
    if st == 1:
        chdelay = 1.e6 / (4 * speed)
    # a[5] is the distance between chopper disc 1 and 5
    # alpha see description
    chdelay += (alpha * wl * a[5] - 1.e6 * (1.0 / ratio2 - 1.0) / (4 * speed))
    chdelay %= 1.e6 / (2 * speed)
    chdelay -= 100.0
    if chdelay < 0:
        chdelay += 1.e6 / (2 * speed)
    return int(round(chdelay))


def calculateCounterDelay(wl, speed, ratio, delay, ch5_90deg_offset):
    # calculate the speed in Hz instead of given speed in rpms
    # returns the delay in s (should be smaller than the calculated frametime)
    speed /= 60.0
    ratio2 = speedRatio(ratio)
    # 4 * speed, since we have 4 slits in chopper disc 1
    TOFoffset = 1.0 / (ratio2 * (4 * speed))  # normal mode
    if ch5_90deg_offset:  # chopper 5 90 deg rotated
        TOFoffset *= 2.0
    tel = 1e-6 * alpha * wl * (a[0] - a[5]) + TOFoffset + delay
    n = int(tel / (ratio / (2 * speed)))
    tel -= n * (ratio / (2 * speed))
    # round to multiple of 100ns, (property of electronics)
    return int(round(tel / (2*ttr))) * 2 * ttr


def calculateFrameTime(speed, ratio):
    """
    Calculates the frame time interval from chopper parameters.

    Chopper speed in rpm given, but calculations are in Hz.
    The interval is the time between pulses of chopper 5 because chopper 5
    has only 2 slits

    returns the frame time in s
    """
    speed /= 60.0
    if speed == 0:
        return 0.052
    # 2 * speed since we have 2 identical slits in chopper 5
    return ratio / (2 * speed)


# calculation of flight times

def t1(x, y, ilambda=4.5, offset=0.0):
    """Return the flight time [s] of a neutron of wavelength *ilambda* [A] from
    chopper *x* to chopper *y*, plus the distance *offset*.
    """
    return 1e-6 * alpha * ilambda * (abs(a[x] - a[y]) + offset)


def t2(x, ilambda=4.5, offset=0.0):
    """Return the flight time [s] of a neutron of wavelength *ilambda* [A] from
    chopper *x* to the sample, plus the distance *offset*.
    """
    return t1(0, x, ilambda, offset)


# calculation of chopper phases

def phi1(x, w, ilambda=4.5):
    """Return the angle [deg] that chopper *x* turns until neutrons of
    wavelength *ilambda* [A] arrive at it from chopper 1.
    """
    return 360.0 * w / 60.0 * t1(1, x, ilambda, 0.0)


def phi(x, w, ilambda=4.5, crc=1, slittype=0, ratio=1, ch5_90deg_offset=0):
    """Return the phase angle that has to be set for wavelength *ilambda* [A]
    at chopper *x*.

    **Remark**:
    If the disk slits are switch to non-standard values the phase is calculated
    to the trigger signal __not__ to the neutron package at the first chopper
    disc.
    """
    itv = 1.0
    if x == 5:
        itv = speedRatio(ratio)
    if crc:
        phi_1 = itv * (sigmaxcrc[x] * phi1(x, w, ilambda) + chopperOffset[x])
    else:
        phi_1 = itv * (sigmax[x] * phi1(x, w, ilambda) + chopperOffset[x])
    if slittype == 1:
        phi_1 += st0[x] * itv
    elif slittype == 2:
        phi_1 += st1[x] * itv
    if ch5_90deg_offset and x == 5:
        phi_1 += 90.0
    phi_2 = phi_1 - sgn(phi_1) * int(abs(phi_1) / 360.0) * 360.0
    phi_3 = phi_2 - sgn(phi_2) * int(abs(phi_2) / 180.0) * 360.0
    phi_4 = round(phi_3 * 100.0) / 100.0
    # print x, phi_4
    return phi_4


# Energy resolution calculation

def Eres1(li, w, st=0, crc=1, dL=0.0, lf=None):
    """Return energy resolution at position *x* [m] downstream the sample.

    * li: wavelength [A]
    * dL: uncertainty in distance [m]
    * w: chopper angular speed [rpm]
    * st: slit type (0=gg, 1=kk, 2=gk)
    * crc: counter-rotating P and M disks
    """
    if w == 0:
        return (0, 0)
    wc = w / 60.0
    if st == 0:
        ap = 13.82              # aperture P-Chopper
        am = 5.0                # aperture M-Chopper
    elif st == 1:
        ap = 13.82 / 2.         # aperture P-Chopper
        am = 5.0 / 2.           # aperture M-Chopper
    else:
        ap = 13.82              # aperture P-Chopper
        am = 5.0 / 2.          # aperture M-Chopper
    tm = am / (2. * 360 * wc)   # opening time M-Chopper
    tp = ap / (2. * 360 * wc)   # opening time P-Chopper
    if crc == 0:
        tm *= 2.
        tp *= 2.
    # Lpd = a[0] + x            # flight distance chopper1-detector
    li *= 1.0e-10
    if lf is None:
        lf = li
    lfi = lf / li

    A = tm * (Lpm + Lms + Lsd * lfi ** 3)
    B = tp * (Lms + Lsd * lfi ** 3)
    C = Lpm * mn * lf * dL / h
    dt = sqrt(A * A + B * B + C * C) / Lpm             # uncertainty in time
    res = h ** 3 * dt / (mn * mn * e * Lsd * lf ** 3)  # uncertainty in energy

    return (res, dt)


def Energy(wavelength):
    """Convert neutron wavelength to neutron energy."""

    k0 = 2 * pi / (wavelength * 1e-10)
    return 1000. * (hbar * k0) ** 2 / (2 * mn * e)


class ResolutionAnalysis:

    def __init__(self, chSpeed, chWL, chRatio, chST):
        self.speed = chSpeed
        self.wl = chWL
        self.ratio = chRatio
        self.st = chST

        # calculate E0
        self.k0 = 2 * pi / (chWL * 1e-10)
        self.E0 = Energy(chWL)

        self.run()

    def run(self):
        # Calculate Dynamic Range

        tobs = 1. / (2. * self.speed / 60.) * self.ratio
        lambda_max = tobs * 1e6 / (alpha * Lsd) * 1e-10
        kf_min = 2 * pi / lambda_max

        self.dE_all = np.arange(-self.E0, 50 + 0.1, 0.1)

        kf_all = np.abs(np.sqrt(
            1e-3 * 2 * mn * e * self.dE_all / (hbar * hbar) + self.k0 * self.k0))
        index = np.argwhere(kf_all >= kf_min).flatten()
        self.dE = self.dE_all[index]
        self.dE_min = min(self.dE)
        kf = kf_all[index]

        self.q_low = 1e-10 * np.sqrt(
            self.k0 * self.k0 + kf * kf - 2 * abs(self.k0) * np.abs(kf) *
            cos(2 * radians(low_angle)))
        self.q_high = 1e-10 * np.sqrt(
            self.k0 * self.k0 + kf * kf - 2 * abs(self.k0) * np.abs(kf) *
            cos(2 * radians(high_angle)))

        self.q_low_0 = 1e-10 * self.k0 * sqrt(
            2 * (1 - cos(radians(2 * low_angle))))
        self.q_high_0 = 1e-10 * self.k0 * sqrt(
            2 * (1 - cos(radians(2 * high_angle))))

        # Calculate elastic resolution
        self.lambdas = np.arange(1, 20.1, 0.1)
        i2 = np.argwhere(((self.lambdas - self.wl) * (self.lambdas - self.wl))
                         < 1e-15).flatten().astype(int).tolist()
        self.dE_res = np.array([1000 * Eres1(l, self.speed, self.st, dL=Ls)[0]
                                for l in self.lambdas])
        self.dE_el = (1e3 * self.dE_res[i2])[0]

        # Calculate inelastic resolution
        self.lambdaf = 2 * pi / kf
        self.dE_in = np.array(
            [1e3 * Eres1(self.wl, self.speed, self.st, dL=Ls, lf=l)[0]
             for l in self.lambdaf])
