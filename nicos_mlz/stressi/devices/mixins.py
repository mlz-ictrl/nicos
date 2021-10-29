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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""Some mixins used at STRESS-SPEC instrument."""

import math

from nicos.core import Attach, Moveable, Override, Param, Readable
from nicos.core.mixins import DeviceMixinBase


class Formula:
    """This object handles a formula and the calculation.

    The variable of the function must be named 'x' and all other parameters
    must be numbers!

    .. note:: This is a very basic implementation which gives the opportunity
       for improvements.
    """

    # take the whole math module function bunch into the namespace
    _globals = {k: v for k, v in vars(math).items() if not k.startswith('__')}
    # This should avoid to take others modules into the namespace (see python
    # doc of eval function
    _globals['__builtins__'] = globals()['__builtins__']

    def __init__(self, formula):
        self._formula = formula

    def eval(self, x):
        return eval(self._formula, self._globals, {'x': x})

    def __str__(self):
        return self._formula


ext_formula_desc = '''
    The formula must be given in the form that all parameters are numbers, but
    the value to be transformed is called 'x'. The 'x' value may occur more
    than once.
'''


class TransformRead(DeviceMixinBase):
    """This mixin converts a single raw read value into a calculated value.

    This mixin could be inherited by classes which want to recalculate their
    read values with a formula.

    It adds automtically the `informula` parameter.
    """

    _informula = None

    parameters = {
        'informula': Param('Input conversion formula',
                           type=str, settable=False, default='x',
                           ext_desc=ext_formula_desc,
                           ),
    }

    parameter_overrides = {
        'unit': Override(volatile=True, mandatory=False),
    }

    attached_devices = {
        'dev': Attach('Base device', Readable),
    }

    def _mapReadValue(self, value):
        return self._informula.eval(value)

    def _readRaw(self, maxage=0):
        raw = self._attached_dev.read(maxage)
        self.log.debug('Raw value: %r', raw)
        return raw

    def doReadUnit(self):
        return self._attached_dev.unit

    def doUpdateInformula(self, formula):
        self.log.debug('Informula: %r' % formula)
        self._informula = Formula(formula)
        return formula


class TransformMove(TransformRead):
    """This mixin converts a single write value into calculated value.

    This mixin could be inherited by classes which want to recalculate their
    write value with a formula and write this one.

    It adds automtically the `outformula` parameter.
    """

    _outformula = None

    attached_devices = {
        'dev': Attach('Base device', Moveable),
    }

    parameters = {
        'outformula': Param('Output conversion formula',
                            type=str, settable=False, default='x',
                            ext_desc=ext_formula_desc,
                            ),
    }

    def _mapTargetValue(self, target):
        return self._outformula.eval(target)

    def _startRaw(self, target):
        self._attached_dev.start(target)

    def doUpdateOutformula(self, formula):
        self.log.debug('Outformula: %r', formula)
        self._outformula = Formula(formula)
        return formula
