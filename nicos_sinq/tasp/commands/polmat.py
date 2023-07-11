# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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
#   Markus Zolliker <markus.zolliker@psi.ch>
#
# *****************************************************************************

import math
import time

from nicos import session
from nicos.commands import helparglist, usercommand
from nicos.commands.measure import SetEnvironment, count
from nicos.commands.scan import manualscan

# indices (starting from 1, because we will also have the negative counterparts
X = 1
Y = 2
Z = 3

XYZ = (X, Y, Z)
ALL = (X, Y, Z, -X, -Y, -Z)


def normalize(data):
    """normalize counts and calculate sigma ** 2

    :param data: dict[i, j] of (counts, monitor) wih i in XYZ and j in ALL
    :return: dict[i, j] of (signal, sigma ** 2) with the same keys as data
    """"""
    """
    return {key: (cnts/mon, max(cnts, 1) / mon ** 2)
            for key, (cnts, mon) in data.items()}


def calc_polmat(data, background=None, neg=1):
    """calculate the polarisation matrix from measured data

    :param data: dict[i, j] of (counts, monitor) with i in XYZ and j in ALL
    :param background: background data, if available, structured as
        parameter 'data'
    :param neg: when --/-+ is used instead of ++/+-
    :return: result containing the polarisation matrix and their norm
       result[i, j] is (pij, dpij) with dpij the statistical error of pij
       and
       result[i, 0] is  (|Pi|, d|Pi|) being magnitude and sigma of the
       norm of a row
    """
    data = normalize(data)
    if background is not None:
        background = normalize(background)
        for key, (y, d2) in data.items():
            yb, d2b = background[key]
            data[key] = y - yb, d2 + d2b

    result = {}
    for i in XYZ:
        sum2 = 0
        sumd2 = 0
        for j in XYZ:
            ypos, d2pos = data[i, j]
            yneg, d2neg = data[i, -j]
            ysum = ypos + yneg
            if ysum:
                pij = neg * (ypos - yneg) / ysum
                dpij2 = ((1 - pij) / ysum) ** 2 * d2pos + \
                        ((1 + pij) / ysum) ** 2 * d2neg
            else:
                pij = 0
                dpij2 = 1
            result[i, j] = pij, math.sqrt(dpij2)
            sum2 += pij ** 2
            sumd2 += dpij2 * pij ** 2
        result[i, 0] = math.sqrt(sum2), math.sqrt(sumd2 / (sum2 or 1))
    return result


def print_polmat(result):
    """print the result as in the SICS polmat command"""
    session.log.info("  pix     sigma     piy     sigma     piz    '"
                     " sigma     |Pi|    sigma")
    for i in XYZ:
        session.log.info('  '.join(["%7.3f %7.3f" % result[i, j] for j
                                    in (X, Y, Z, 0)]))


def test_gufi(gufi):
    return abs(gufi._attached_magnet.read(0) - gufi.hold_value) < .1


def check_gufi(gufi):
    """
    The guide field power supply tends to reset itself. Rather then
    fixing the hardware we check here if the guide field is OK and
    fix it if it has gone off.
    """
    gufiok = test_gufi(gufi)
    while not gufiok:
        session.log.info('Trying to fix gufi...')
        gufi.maw(gufi.target)
        gufiok = test_gufi(gufi)
        if not gufiok:
            # The thing tends to overheat: thus wait before trying again
            time.sleep(60)


@usercommand
@helparglist('QE position, optional background QE position, counting preset')
def polmat(qpos, bqpos=None, neg=False,  **preset):
    """
    Measures a polarisation matrix. Drives to qpos and then
    measures all the permutations of the mupad vectors. With this
    data a polarisation matrix is calculated and printed If the parameter
    bqpos is given, another data set is measured for all permutations
    and used for the background correction of the polarisation matrix.
    Setting the optional parameter neg to True measures the negative
    permutations
    Example:

    polmat((1.37, -1.37, 0, 0), bqpos=(1.5, -1.5, 0, 0), t=5)
    """
    tasp = session.getDevice('TASP')
    tasp.maw(qpos)
    musw = session.getDevice('munumsw')
    gufi = session.getDevice('gufi')
    SetEnvironment('i1', 'i2', 'i3', 'i4')
    data = {}
    counter = session.getDevice('ctr1')
    monitor = session.getDevice('mon1')
    if neg:
        sign = -1
    else:
        sign = 1
    with manualscan(musw):
        for x in XYZ:
            for y in ALL:
                check_gufi(gufi)
                musw.maw((sign*x, y))
                count(**preset)
                data[x, y] = (counter.read(0)[0], monitor.read(0)[0])

    if bqpos:
        tasp.maw(bqpos)
        bgk = {}
        with manualscan(musw):
            for x in XYZ:
                for y in ALL:
                    check_gufi(gufi)
                    musw.maw((sign*x, y))
                    count(**preset)
                    bgk[x, y] = (counter.read(0)[0], monitor.read(0)[0])
    else:
        bgk = None

    result = calc_polmat(data, bgk, sign)
    print_polmat(result)
