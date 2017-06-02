#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#   Björn Pedersen <bjoern.pedersen@frm2.tum.de>
#
# *****************************************************************************

"""
Module for utility user commands.

This module contains utility functions that are of general interest for user
scripts, e.g different list generators and other helper functions.
"""

import math

import numpy

from nicos.core import UsageError
from nicos.commands import usercommand, helparglist, parallel_safe


__all__ = ['floatrange', 'RangeListLog', 'RangeListGeneral']


def RangeListByStep(start, end=None, inc=None):
    """Generate a list of points within [from;to]

    A range function, that does accept float increments...

    usage example:
    l1 = RangeList(1,2,0.5)

    l1 will be:  [1., 1.5, 2.]
    """

    if end is None:
        end = start + 0.0
        start = 0.0
    delta = end - start

    if inc is None:
        inc = math.copysign(1., delta)

    if inc == 0.0:
        raise UsageError('Increment needs to differ from zero')

    if math.copysign(1.0, inc) != math.copysign(1.0, delta):
        raise UsageError('Start/end points and increment are inconsistent')

    res = numpy.arange(start, end + inc, inc)
    if inc > 0 and end - res[-1] < (0.001 * inc):
        res[-1] = end
    elif inc < 0 and end - res[-1] > (0.001 * inc):
        res[-1] = end
    return res.tolist()


def RangeListByCount(start, end=None, num=2):
    """Generate a list of points within [from;to] with num points.

    A range function, that gives evenly spaced points.
    Uses simply the numpy.linspace function.

    usage example:
    l1 = RangeList(1,2,3)

    l1 will be:  [1., 1.5, 2.]
    """
    if end is None:
        end, start = start, 0.0
    return numpy.linspace(start, end, num).tolist()


@usercommand
@helparglist('start, end, [step | num=n]')
@parallel_safe
def floatrange(start, end, step=None, **kw):
    """Generate a linear range of values.

    Generate a linear range of values from *start* to *end*, with either a
    specified step width or number of values.

    *start* and *end* are the start and end values and always included.  *step*
    is the stpewidth and should always be positive; *num* is the number of
    values desired.

    Examples:

    >>> floatrange(1, 2, step=0.1)
    [1.0, 1.1, 1.2 ... 1.9, 2.0]
    >>> floatrange(2, 1, step=0.1)
    [2.0, 1.9, 1.8 ... 1.1, 1.0]
    >>> floatrange(1, 2, num=3)
    [1.0, 1.5, 2.0]
    """
    start = float(start)
    end = float(end)
    # case 1: stepwidth given
    if step is not None:
        if kw.get('num') is not None:
            raise UsageError('Both step and num given, only one is allowed.')
        if step <= 0.0:
            raise UsageError('Increment has to be positive and greater than '
                             'zero.')
        step = math.copysign(float(step), (end - start))
        return RangeListByStep(start, end, step)
    else:
        try:
            num = int(kw.get('num'))
        except TypeError:
            raise UsageError('Please give either step or num.')
        if num < 2:
            raise UsageError('The number of steps should be greater than 1.')
        return RangeListByCount(start, end, num)


@usercommand
@parallel_safe
def RangeListLog(start, end, num=10):
    """Generate a log spaced list with specified number of steps.

    Example:

    >>> RangeListLog(1., 2., 3)
    [1.0, 1.4142135623730949, 2.0]
    """
    if start <= 0 or end <= 0:
        raise UsageError('Log spacing is only defined for positive values')

    return numpy.logspace(math.log10(start), math.log10(end), num).tolist()


def identity(x):
    """Identity function."""
    return x


@usercommand
@parallel_safe
def RangeListGeneral(start, end, num=10, func=identity, funcinv=None):
    """Generate a list spaced evenly in arbitrary functions.

    *func* is a function taking one argument for the values should be spaced
    evenly, can also be a lambda function.  *funcinv* is the inverse function
    to *func*, can be omitted if identical to *func*.

    This function does less error checking and will raise an error on wrong
    input values (e.g. outside the domain of the used function)

    Examples:

    >>> RangeListGeneral(0, math.pi/2, 5, math.sin, math.asin)
    # evenly spaced points on a sine
    [0.0 0.252680255142 0.523598775598 0.848062078981 1.57079632679]
    >>> RangeListGeneral(1, 100, 10, lambda x: 1/x)
    # evenly spaced in 1/x
    [1.0 1.12359550562 1.28205128205 1.49253731343 1.78571428571
     2.22222222222 2.94117647059 4.34782608696 8.33333333333 100.0]
    """
    start = float(start)
    end = float(end)
    try:
        s1 = func(start)
        s2 = func(end)
        res = numpy.linspace(s1, s2, num)
        if funcinv is None:
            funcinv = func
        ufuncinv = numpy.frompyfunc(funcinv, 1, 1)
        return ufuncinv(res).astype(numpy.float64).tolist()
    except Exception as e:
        raise RuntimeError(str(e))
