#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""Haake/Julabo thermostat Protocol NICOS driver"""

__version__ = "$Revision$"

from time import sleep, time

from IO import StringIO

from nicos.core import status, intrange, oneof, Device, Moveable, \
     Param, NicosError, CommunicationError, ProgrammingError
from nicos.taco.core import TacoDevice

class HaakeRS232Driver(TacoDevice, Device):
    """Basic Haake client class (tested for Haake DC50/K35)
    """

    taco_class = StringIO

    parameters = {
        'maxtries': Param('Maximum tries before raising', type=int, default=5),
    }

    def _w (self,cmd,par=""):
        maxtry = self.maxtry
        while 1==1:
            if par == "":
                apar = par
            else:
                apar = eval(par)
            if apar != "":
                istr = cmd+" "+apar+chr(0x0d)
            else:
                istr = cmd + chr(0x0d)
            try:
                while self.HWDev.read(50) != "":
                    sleep (0.01)
                self.HWDev.write(istr)
                sleep(0.5)
                istr = self._r()
                if len(istr) > 2:
                    istr = istr[:-2]
                if istr == "!":
                    maxtry -= 1
                    if maxtry == 0:
                        raise CommunicationError(self, "write error")
                    continue
                if istr == "$":
                    istr = "ok"
                if cmd=="R I" or cmd=="I" or cmd=="R T1" or cmd=="T1":
                    try:
                        istr = eval(istr[2:-1])
                    except:
                        maxtry -= 1
                        if maxtry == 0:
                            raise CommunicationError(self, "write error")
                        continue
                if cmd=="R T3" or cmd=="T3":
                    try:
                        istr = eval(istr[2:-1])
                    except:
                        maxtry -= 1
                        if maxtry == 0:
                             raise CommunicationError(self, "write error")
                        continue
                break
            except RuntimeError, e:
                raise NicosError(self, e.__str__ ())
        return istr
        
    def _r (self):
        maxtry = self.maxtry
        inp = "a"
        ainput = ""
        atime = time.time()
        while inp != chr(0x0a):
            if time.time() > atime + 10.0:
                return "!"
            inp = self.HWDev.read()
            if inp == "!":
                return "!"
            if inp == "":
                maxtry -= 1
                if maxtry == 0:
                    raise NicmError ("read error")
                continue
            ainput = ainput + inp
        return ainput

    def doInit (self):
        pass

    def write (self, cmd, par=""):
        a = self._w (cmd, par)
        sleep(0.1)
        return a

class Julabo(HasLimits, Moveable):

    attached_devices = {
        'bus': (HaakeRS232Driver, 'Serial communication bus'),
    }

    parameters = {
        'rampType': Param('ramping(0) or stepping(1)', type=intrange(0, 2), default=0),
        'rampRate': Param('ramp speed in K/s', type=float, default=0.002),
        'tolerance' : Param('tolerance in K', type=float, default=0.2),
        'thermostat_type' : Param('Type of thermostat', 
                                  type=oneof('JulaboF32HD', 'HaakeDC50'),
                                  default='JulaboF32HD'),
        'intern_extern' : Param('internal(0) or external(1) temperature sensor',
                                  type=intrange(0, 2), default=1),
    }
    
    def doInit (self):
        # set default values
        self._waiting = FALSE
        self._stime = 0
        self._TRamp = 0
        self._TStep = 0
        self._SKind = 1
        self._htr = 4

    def doStart (self, pos):
        if self.thermostat_type == "JulaboF32HD":
            if self._adevs['bus'].write ("in_mode_05") == 0:
                self._adevs['bus'].write ("out_mode_05",1)
                sleep (5)
            if self._adevs['bus'].write ("in_mode_04") != self.intern_extern:
                self._adevs['bus'].write ("out_mode_04", self.intern_extern)
                sleep (5)
        # start ramp/step
        if self.rampType == 0:	# ramp
            self._TRamp = pos
        else:			# step
            self._TStep = pos

        temp = self.read()
        if pos > temp:
            self._SKind = 0
        else:
            self._SKind = 1
        if self.thermostat_type == "JulaboF32HD":
            self._adevs['bus'].write ("out_sp_00",pos)
        elif self.thermostat_type == "HaakeDC50":
            self._adevs['bus'].write ("W S0 %f" % (pos,))
        self._stime = time()
        sleep (1)

    def doRead (self):
        # return current temperature
        try:
            if self.thermostat_type == "JulaboF32HD":
                if self.intern_extern == 0:
                    temp = self._adevs['bus'].write ("in_pv_00")
                else:
                    temp = self._adevs['bus'].write ("in_pv_02")
            elif self.thermostat_type == "HaakeDC50":
                temp = self._adevs['bus'].write ("R T3")
            ret = temp
        except:
            raise NicosError(self, "could not read from device")
        return ret


    def doStop (self):
        # stop ramp/step immediately
        if self.thermostat_type == "JulaboF32HD":
            self._adevs['bus'].write ("out_mode_05",0)
        else:
            pass

    def doStatus (self):
        # 0: idle
        # 1: ramping
        # 2: stepping
        # 3: error
        try:
            temp = self.read()
        except:
            return 3
        if self.rampType == 0:
            if self._SKind == 0:
                if self._TRamp - self.tolerance >= temp:
                    return 1
                else:
                    return 0
            else:
                if self._TRamp + self.tolerance <= temp:
                    return 1
                else:
                    return 0
        else:
            if self._SKind == 0:
                if self._TStep - self.tolerance >= temp:
                    return 2
                else:
                    return 0
            else:
                if self._TStep + self.tolerance <= temp:
                    return 2
                else:
                    return 0
                
    def doWait (self, stime=0):
        #
        while self._waiting == TRUE:
            sleep(0.03)
        self._waiting = TRUE
        if stime == 0:
            a = self.doStatus()
            return a
        while 1==1:
            a = self.doStatus()
            if a == 0:
                break
            if time.time() >= self._stime + stime:
                self.log.warning("timeout occurred - did not reach selected temperature in time", exc =1)
                break
            sleep(0.1)
        self._waiting = FALSE
        return 0
