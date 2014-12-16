#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""TOFTOF chopper and resolution calculations."""

from math import sqrt

try:
    from scipy import constants
    h = constants.value('Planck constant')
    mn = constants.value('neutron mass')
    e = constants.value('elementary charge')
except ImportError:
    h = 6.62606896e-34                      # Planck constant [Js]
    mn = 1.674927211e-27                    # Neutron mass [kg]
    e = 1.602176487e-19                     # Elementary charge [C]

# in us (1e6) / AA (1e-10) / m
alpha = 1e6 * (mn / h) / 1e10           # Should be 252.7784

def sgn(x):
    return -1 if x < 0 else 1


# *** TOFTOF specific constants ***

# a[0]:   distance chopper1 - sample in m
# a[1-7]: distance chopper1 - chopperX in m
a = (11.4, 0.0, 0.1, 3.397, 7.953, 8.028, 9.925, 10.0)

# offsets of chopper zero position in deg (definition of the sign is unknown
# chopperOffset = (0.00, 0.00, -0.25, 0.45, 0.39, -0.25, 0.13, 0.36)
# chopperOffset = (0.00, 0.00, -0.06, 0.45, 0.39, -0.25, -0.81, 0.36) # 2.12.2009
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
    If the disk slits are switch to non standard values the phase is calculated
    to the trigger signal __not__ to the neutron package at the first chopper
    disc.
    """
    itv = 1.0
    if x == 5:
        if ratio in [2, 3, 4, 5, 6, 7, 8]:
            itv = (ratio - 1.0) / float(ratio)
        elif ratio in [9, 10]:
            itv = 7.0 / float(ratio)
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

def Eres1(li, w, st=0, crc=1, dL=0.0):
    """Return energy resolution at position *x* [m] downstream the sample.

    * li: wavelength [A]
    * dL: uncertainty in distance [m]
    * w: chopper angular speed [rpm]
    * st: slit type (0=gg, 1=kk, 2=gk)
    * crc: counter-rotating P and M disks
    """
    x = 4.0
    if w == 0:
        return (0, 0)
    wc = w / 60.0
    if st == 0:
        ap = 13.82              # aperture P-Chopper
        am = 5.0                # aperture M-Chopper
    else:
        if st == 1:
            ap = 13.82 / 2.0    # aperture P-Chopper
            am = 5.0 / 2.0      # aperture M-Chopper
        else:
            ap = 13.82          # aperture P-Chopper
            am = 5.0 / 2.0      # aperture M-Chopper
    tm = am / (2.0 * 360 * wc)  # opening time M-Chopper
    tp = ap / (2.0 * 360 * wc)  # opening time P-Chopper
    if crc == 0:
        tm *= 2.0
        tp *= 2.0
    Lpm = a[7] - a[1]           # flight distance chopper1-chopper7
    Lms = a[0] - a[7]           # flight distance chopper7-sample
    Lsd = x                     # flight distance sample-detector
    # Lpd = a[0] + x            # flight distance chopper1-detector
    li *= 1.0e-10
    lf = li

    A = tm * (Lpm + Lms + Lsd * (lf / li)**3)
    B = tp * (Lms + Lsd * (lf / li)**3)
    C = Lpm * mn * lf * dL / h
    dt = sqrt(A**2 + B**2 + C**2) / Lpm        # uncertainty in time
    res = h**3 / (mn**2 * e) * dt / (Lsd * lf**3) # uncertainty in energy

    return (res, dt)
