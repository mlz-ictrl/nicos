#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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

import math


def find_max(profile):
    maxval = 0
    pos = 0
    idx = 0
    for p in profile:
        if p > maxval:
            pos = idx
            maxval = p
        idx += 1
    return pos


def find_half(profile, start, incr):
    """Find the half height point. This speeds limit
    finding and protects against very broad peaks which
    might be misinterpreted as background at their tops"""
    half = profile[start]/2.
    idx = start
    while True:
        idx += incr
        if idx < 0:
            return -1
        if idx >= len(profile):
            return len(profile) + 1
        if profile[idx] < half:
            return idx


def count_window_hits(profile, pos, window, incr):
    test = pos + incr * window
    # Can I do this?
    if test < 0 or test > len(profile):
        return -1

    if profile[pos] > 0:
        var = math.sqrt(profile[pos])
        winmin = profile[pos] - 0.67 * var
        winmax = profile[pos] + 0.67 * var
    else:
        winmin = 0
        winmax = 1

    count = 0
    for i in range(0, window):
        idx = pos + i * incr
        if winmin < profile[idx] < winmax:
            count += 1
    return count


def find_limit(profile, start, incr, window, prob):
    count = count_window_hits(profile, start, window, incr)
    if count < 0:
        return count
    probability = float(window - count)/float(window)
    idx = start

    while probability > prob:
        idx += incr
        count = count_window_hits(profile, idx, window, incr)
        if count < 0:
            return count
        probability *= float(count - window)/float(window)
    return idx


def do_integrate(profile, left, right):
    leftBck = 0
    for idx in range(0, left):
        leftBck += profile[idx]
    rightBck = 0
    for idx in range(right, len(profile)):
        rightBck += profile[idx]
    peakSum = 0
    for idx in range(left, right+1):
        peakSum += profile[idx]
    nPeak = right - left + 1
    nBck = left + (len(profile) - right)
    intensity = peakSum - (float(nPeak)/float(nBck)) *\
        (float(leftBck + rightBck))
    stddev = math.sqrt(peakSum + (float(nPeak)/float(nBck))**2 *
                       float(leftBck+rightBck))
    return intensity, stddev


def window_integrate(profile):
    """Scan profile integration using the window method
    as described by Grant & Gabe in J. Appl. Cryst (1978),
    11, 114-120"""
    peak = find_max(profile)
    left = find_half(profile, peak,  -1)
    window = 6
    prob = .01
    if left < 0:
        return False, 'No left side', 0., 0.
    left = find_limit(profile, left, -1, window, prob)
    if left < 0:
        return False, 'No left side', 0., 0.

    right = find_half(profile, peak, 1)
    if right > len(profile):
        return False, 'No right side', .0, .0
    right = find_limit(profile, right, 1, window, prob)
    if right < 0:
        return False, 'No right side', .0, .0

    intensity, stddev = do_integrate(profile, left, right)
    return True, '', intensity, stddev
