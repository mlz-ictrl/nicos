#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2014 by the NICOS contributors (see AUTHORS)
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

"""REFSANS NOK coder class for NICOS."""

from nicos.core import Override, status, oneofdict, oneof, Param
from nicos.devices.abstract import Coder as BaseCoder
from nicos.devices.taco.io import AnalogInput

class CoderReference(AnalogInput) :
    """ NOK coder voltage reference """

    parameters = {
        'refhigh' : Param('High reference',
                          type = float,
                          default = 19.8, # 2 * 9.9
                          settable = False,
                         ),
        'refwarn' : Param('Reference warning',
                          type = float,
                          default = 18.0, # 9.0 * 2
                          settable = False,
                         ),
        'reflow' : Param('Low reference',
                         type = float,
                         default = 17.0, # 8.0 * 2 XXX
                         settable = False,
                        ),
        }

    def doRead(self, maxage=0):
        ref = self._read()
        if abs(ref) >= self.refhigh :
            self.log.error(self,  'Reference voltage to high : %f > %f' %
                           (ref, self.refhigh))
        if   abs(ref) <  self.reflow:
            self.log.error(self, 'Reference voltage to low : %f < %f' %
                           (ref, self.reflow))
        elif abs(ref) <  self.refwarn:
            self.log.warning(self, 'Reference voltage seems to be to low : ' \
                                   '%f < %f' % (ref, self.refwarn))
        return ref

    def doStatus(self, maxage=0):
        ref = self._read()
        if abs(ref) >= self.refhigh :
            return status.ERROR,  'Reference voltage to high : %f > %f' % \
                                    (ref, self.refhigh)
        if   abs(ref) <  self.reflow:
            return status.ERROR, 'Reference voltage to low : %f < %f' % \
                                    (ref, self.reflow)
        elif abs(ref) <  self.refwarn:
            return status.ERROR, 'Reference voltage seems to be to low : '\
                                 '%f < %f' % (ref, self.refwarn)
        else:
            return status.OK, ''

    def _read(self) :
        # Range of RAWValue, if it is outside of expection, the cable may be
        # broken test range of ref lack of resolution 9.5 < ref > 10 clip!
        ref = 2.0 * self._taco_guard(self._dev.read)
        return ref

class Coder(BaseCoder):
    """NOK coder implementation class.
    """

    attached_devices = {
        'port' : (AnalogInput, 'analog input device'),
        'ref'  : (CoderReference, 'referencing analog input device'),
    }

    parameter_overrides = {
        'fmtstr' : Override(default = '%.3f'),
        'unit'   : Override(default = 'mm', mandatory = False),
    }

    parameters = {
        'corr' : Param('Correction type',
                       type = oneof('none', 'mul', 'table'),
                       default = 'mul',
                      ),
        'tabfile' : Param('Correction table file',
                          type = str,
                          mandatory = False,
                         ),
        'mul' : Param('Multiplier',
                      type = float,
                      default = 1.0,
                     ),
        'off' : Param('Offset',
                      type = float,
                      default = 0.0,
                     ),
        'snr' : Param('Serial number',
                      type = int,
                      settable = False,
                      mandatory = True,
                     ),
        'length' : Param('Potionmeter length',
                         type = float,
                         settable = False,
                         default = 250,
                        ),
        'sensitivity' : Param('Sensitivity',
                              type = float,
                              mandatory = True,
                             ),
        'phys' : Param('Physically connected and working?',
                       type = str,
                       mandatory = False,
                       default = 'OK',
                      ),
        'position' : Param('Position',
                           type = oneofdict({'top' : -1, 'bottom' : 1}),
                           mandatory = False,
                           default = 'bottom',
                          ),
    }

#   valuetype = oneofdict({-1: 'top', 1: 'bottom'})

    def doSetPosition(self, target):
        # self._taco_guard(self._dev.setpos, target)
        pass

    def doInit(self, mode):
        pass

    def __formula(self, data, direction):
        """the only positon for calculation
        direction = True:  get the position for raw and ref
        direction = False: get new parameter for mul and off
        """
        self.log.debug(self, '%f %f', (data[0], data[1]))
        E = self.position / self.sensitivity * 1000
        self.log.debug(self, 'E = %f' % (E,))
        tmp = E * data[0] / data[1]
        lkorr = self.corr
        if lkorr == 'table':
            try:
                return self.korrtable[data[0]]
            except Exception:
                lkorr = 'mul'
        if direction:
            if lkorr ==  'mul':
                tmp *= self.mul
            return tmp + self.off
        else:
            if lkorr == 'none':
                tmp = data[0] # /E
            elif lkorr ==  'mul':
                tmp = self.mul * data[0] # / E
            return (tmp, self.off + data[1])

    def doStatus(self, maxage=0):
        if self.phys == 'OK':
            return status.OK, ''
        else:
            # Physically not connected or other problems.
            # Ask instrument responsible
            return status.ERROR, self.phys

    def doRead (self, typ='POS'):
        """
        1. ref must be in a given range (depend on ADC)
        2. RAWvalue must be in a given range (depend on NOK)
        """
        self.log.debug(self, 'poti read')
        ref = 0
        RAWValue = 0
        self.log.debug(self, 'poti read enter while')
        exit_ = False
        while not exit_:
            exit_ = False
            for _ in range(2):
                try:
                    # due to resistors
                    ref = self._adevs['ref'].read()
                    break
                except Exception:
                    self.log.exception(self, 'readerror REF 2. (1/2))')
                    exit_ = False
            for _ in range(2):
                try:
                    # let it so the box must work
                    RAWValue = self._adevs['port'].read()
                    break
                except Exception:
                    self.log.exception(self, 'readerror RAWVALUE 2. (2/2);')
                    exit_ = False
        self.log.debug(self, 'raw value = %f reference value = %f',
                       (RAWValue, ref))
        try:
            Position = self.__formula([RAWValue, ref], True)
            self.log.debug(self, 'okay')
            if 'OFF' == typ.upper():
                return {'off' : -RAWValue / ref}
            elif 'POS'== typ.upper():
                return Position
            elif 'PARAMETER' == typ.upper():
                return {'corr' : self.corr,
                        'off' : self.off,
                        'sensitivity' : self.sensitivity,
                        'mul' : self.mul,
                        'avg' : 'auto'}
            else:
                return {'corr' : self.corr,
                        'RAWValue' : RAWValue,
                        'ref' : ref,
                        'Position' : Position}
        except Exception:
            self.log.exception(self, 'calc.Error')
