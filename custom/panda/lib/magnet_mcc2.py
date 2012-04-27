#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""PANDA Mcc2 Interface for 7T5 Magnet."""

__version__ = "$Revision$"

from time import sleep, time as currenttime

from IO import StringIO

from nicos.taco.core import TacoDevice

import threading

from nicos.core import status, intrange, oneof, anytype, Device, Param, \
     Readable, Moveable, NicosError, ProgrammingError, TimeoutError, \
     formatStatus, tacodev, CommunicationError
from nicos.abstract import Motor as NicosMotor, Coder as NicosCoder
from nicos.generic.axis import Axis

import nicos.status as status


class MCC2Motor(NicosMotor):
    """Class for the control of the Mcc2-Motor"""
    parameters = {
        #~ 'timeout'   : Param('Timeout in seconds for moving the motor or getting'
                            #~ ' a reaction', type=intrange(1, 3601), default=360),
        #~ 'sign'      : Param('Sign of moving direction value',
                            #~ type=oneof(-1.0, 1.0), default=-1.0),
        'precision' : Param('Precision of the device value',
                            type=float, unit='main', settable=False,
                            category='precisions', default=0.001),
        'fmtstr'    : Param('Format string for the device value',
                            type=str, default='%.3f', settable=False),
        'tacodevice' : Param('tacodevice of a rs232 taco server',
                            type=tacodev, mandatory=True),
        'channel'       : Param(' Channel of MCC2 to use (X or Y)',
                            type=oneof('X','Y'), default='Y'),
        'address'       : Param(' address of MCC2 to use (0 to 15)',
                            type=intrange(0,16), default=0),
        'slope'         : Param('stepper units per degree of rotation',
                            type=float, default=1),
        
    }

    _dev=None
    
    def doInit(self):
        #~ NicosMotor.doInit(self)
        self._lock=threading.Lock()
        if self._mode != 'simulation':
            self._dev = StringIO( self.tacodevice )
            try:
                self._dev.deviceOn()
            except Exception:
                self.log.warning('could not switch on taco devices', exc=1)
            self.log.debug('initialized serial taco device')
            if not self._communicate('IVR').startswith('MCC'):
                self.log.error( 'No MCC-2 found !!!' )
                raise NicosError('No MCC-2 found !!!')
            self.doReset()

    def doReset( self ):
        # write correct parameters to mcc-2
        for s in 'YMA YP01S1 YP04S20 YP14S2000 YP17S2 YP27S1 YP34S1 YP40S4 YP41S10 YP42S12 YP45S8'.split():
            t=self._communicate(s)

    def doStart( self, pos ):
        ''' go to a absolute stepperpostition'''
        pos=int(pos*self.slope)
        temp=self._communicate('YE%d'% pos )

    def doStatus( self ):
        ''' find status of motor'''
        temp=self._communicate( 'SH' )
        if temp[0]=='N': return status.BUSY,''       # busy
        return status.OK,''        # idle
        
    def doStop( self ):
        ''' send the stop command '''
        temp=self._communicate('YS')

    def doRead( self ):
        '''read the current stepper position'''
        temp=self._communicate('YP19R')      # read parameter 19
        return float( temp ) / self.slope
        
    def doSetPosition( self, newpos ):
        ''' set current position to given value'''
        temp=self._communicate('YP19S%d'%int(newpos*self.slope))

    def _communicate( self, cmd ):
        with self._lock:
            if cmd[0] in ['X','Y']:
                cmd=self.channel.upper()+cmd[1:] # make sure to use the right channel....
            if self._dev:
                cmd='\002%X%s\003'%(self.address,cmd)
                self.log.debug( "DBG: sending >%r< to MCC-2"%cmd )
                temp = self._dev.communicate( cmd )
                self.log.debug( 'DBG: got >%r<'%temp)
                if len(temp)>=2 and temp[0]=='\002' :   #strip beginning STX (ending ETX is stripped already)
                    temp=temp[1:]
                    if temp[0]!='\006':
                        raise CommunicationError('MCC-2 did not ACK the last command!')
                    return temp[1:]
                raise CommunicationError('Response timed out')
            raise KeyError('Serial Port not initialized!')
        