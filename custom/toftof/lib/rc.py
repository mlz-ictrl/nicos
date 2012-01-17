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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Huber Motor Controller Protocol NICOS driver"""

__version__ = "$Revision$"

from time import sleep, time

from IO import StringIO

from nicos.core import status, intrange, listof, Device, Readable, Moveable, \
     Param, Override, NicosError, CommunicationError, InvalidValueError, \
     ConfigurationError, ProgrammingError
from nicos.taco.core import TacoDevice

class ModBusDriverHP (TacoDevice, Device):
    """Basic Huber Protocol client class.
       ---------------------------------

       Parameters:
        
       Command Name                 | Description
       -----------------------------+----------------------------------------------------------
       string* read ()              | read a message from device
       string* write (istr)         | write a message to bus and return the answer
    """

    taco_class = StringIO

    parameters = {
        'maxtries': Param('Maximum tries before raising', type=int, default=50),
    }

    def _CRC (self,str):
        crc = ord(str[0])
        for i in str[1:]:
            crc = crc ^ ord(i)
        return self._str(crc)

    def _str (self, val):
        return "%01x%01x" % (((val&0xf0)>>4),(val&0x0f))
    
    def _w (self, istr):
        istr2 = istr
        iexit = False
        for j in range(4):
            for i in self._huberCmds[j]:
                if istr2.find(i,0,len(i)) != -1:
                    iexit = True
                    hcmd = (j, self._huberCmds[j].index(i))
                    break
            if iexit == True:
                 break
        if iexit == False:
            # positioning command or unknown command
            if len(istr2) > 3:
                if istr2[1] == ":" or istr2[2] == ":":
                    hcmd = (5, "positioning command")
                else:
                    raise ProgrammingError ("unknown command: %s" % (istr2,))
            else:
                    raise ProgrammingError ("unknown command: %s" % (istr2,))
        maxtry = self.maxtries
        while 1 == 1:
            try:
                if hcmd[0] == 3:
                    ret = self._taco_guard(self._dev.communicate, istr)
                    if len(ret) < 4 or "!" + chr(13)+"2C" in ret:
                        maxtry -= 1
                        if maxtry == 0:
                            raise CommunicationError ("could not read from device %s" % self.name)
                        continue
                    else:
                        chsum = self._CRC (ret[:-2]).lower()
#                       print ret, chsum
#                       if chsum != ret [-2:].lower():
#                           maxtry -= 1
#                           if maxtry==0:
#                               raise CommunicationError ("could not read from device %s" % self.name)
#                           continue
#                       return ret[:-4]
                        return ret
                else:
                    self._taco_guard(self._dev.writeLine, istr)
                    sleep(0.01)
                    return "ok"
            except RuntimeError, e:
                maxtry -= 1
                if maxtry == 0:
                    raise CommunicationError (e.__str__ ())
                continue

    def _r (self):
        maxtry = self.maxtries
        stime = time.time() + 120
        while 1==1:
            ret = self._taco_guard(self._dev.readLine, ) # HWDev.read()
            if ret == chr(2):
                break
            if ret == "":
                maxtry -= 1
                if maxtry == 0:
                    return ""
            if time.time() > stime:
                return ""
            sleep(0.001)
        inp1 = ""
        while (1==1):
            inp = self._taco_guard(self._dev.readLine, ) # HWDev.read()
            if inp == "":
                maxtry -= 1
            else:
                inp1 = inp1 + inp
            if inp == chr(3):
                return inp1[:-1]
            if maxtry == 0:
                return ""
            if time.time() > stime:
                return ""
            sleep (0.001)

    def doInit (self):
        self._huberCmds = [["acc","alias","conf","def","dec","ecl","ect","edev","edir","eres","est","esh","ffast","vfast","fref",
                            "vref","frun","vrun","gden","gn","gnum","gz","macc","mdec","mdir","mdl","rofs","nofs","update"],
                           ["stop","quit","q","dfi","*fi","dhs","*hs","beepoff","beepon","ccnt","clr","count","ccount","date",
                            "doff","lcdoff","don","lcdon","dout","io","echooff","echoon","eref","fast","fget","goto","load",
                            "local","loc","lpox","move","movec","org","osc","pos","priority","prio","ref","reboot","restart","remote",
                            "rem","reset","clear","run","save","step","shutdown","time","zero"],
                           ["cnt","cntc","cnts","delay","end","fi","gosub","sub","gsb","hs","in","jump","jmp","lin","nl","out",
                            "res","ret","set","start"],
                           ["?cnt","?conf","?cfg","?e","?ec","?osc","?pgm","?getp","*idn?","?v","?io","?in","?line","?ln",
                            "?lin","?p","?status","?c","?s","?"]]
        self._buffer = []     # buffer for input lines

    def communicate(self, msg):
        pass

    def read (self):
        ret = self._r ()
        return ret

    def write (self, istr):
        ret = self._w (istr)
        return ret

class RadialCollimator(Moveable):
    """Start/Stop movement of radial collimator"""

    attached_devices = {
        'bus': (ModBusDriverHP, 'Serial communication bus'),
    }

    parameters = {
        'address' : Param('address of the motor',
                          type = intrange(1, 17), default = 7),
        'start_angle' : Param('',
			  type = float, default = 1.0),
        'stop_angle' : Param('',
                          type = float, default = 5.4),
        'std_speed' : Param('',
                          type = int, default = 1200),
        'ref_speed' : Param('',
                          type = int, default = 100),
        'timeout' : Param ('',
                          type = float, default = 120),
    }

    def doInit (self):
        self._stime = 0
        if self._mode == 'simulation' :
            return

    def doStart(self, state=1):
	print self.status()
        if self.status()[0] == status.OK :
            self._adevs['bus'].write("clr")
            self._adevs['bus'].write("%d:a%.1f" % (self.address, self.start_angle))
            self._adevs['bus'].write("nl")
            self._adevs['bus'].write("%d:a%.1f" % (self.address, self.stop_angle))
            self._adevs['bus'].write("nl")
            self._adevs['bus'].write("jmp1")
            self._adevs['bus'].write("nl")
            self._adevs['bus'].write("end")
            self._adevs['bus'].write("start")
        #self._stime = time.time()
        #self._adevs['bus'].write("osc%d:0" % (self.address,))
        #sleep(0.1)
        #self._adevs['bus'].write("goto%d:%f" % (self.address, self.start_angle))
        #sleep(0.1)
        #ret = 0
        #while ret & 1 == 0:
        #    ret = self._adevs['bus'].write("?s%d" % (self.address,))
        #    ret = int(ret[ret.find(":")+1:])
        #    if time.time() > self._stime + self.timeout:
        #        self._adevs['bus'].write("q%d" % (self.address,))
        #        raise NicmError("could not reach reset position within timeout")
        #    sleep(0.1)
        #self._adevs['bus'].write("osc%d:%f" % (self.address, self.stop_angle - self.start_angle))
        #sleep(0.1)

    def doStop (self):
        #self._adevs['bus'].write("osc%d:0" % (self.address,))
        #sleep(0.1)
        self._adevs['bus'].write("q")

    def doStatus (self):
        try:
            ret = self._adevs['bus'].write("?s%d" % (self.address,))
            val = int(ret[ret.find(":")+1:-1])
	    print '%d, 0x%04x' % (val, val)
	    if (val & 0x100) == 0x100 :	  # Oscillation active
                return (status.BUSY, 'oscillating')
            elif (val & 0x040) == 0x040 : # Program execution active
                return (status.BUSY, 'oscillating')
            elif (val & 0x001) == 0x001 : # Controller passive
		return (status.OK, '')
            else :
                return (status.UNKNOWN, 'unknown')
        except:
            raise CommunicationError ("could not get the status of the motor axis of the radial collimator")

    def doRead(self) :
        try :
            ret = self._adevs['bus'].write("?p%d" % (self.address,))
            val = float(ret[ret.find(":")+1:-1])
            return val
        except:
            raise CommunicationError ("could not get the status of the motor axis of the radial collimator")

    def doReset(self):
        self._stime = time.time()
        # self._adevs['bus'].write("osc%d:0" % (self.address,))
        self._adevs['bus'].write("ffast%d:%f" % (self.address, 200))
        self._adevs['bus'].write("frun%d:%f" % (self.address, 100))
        self._adevs['bus'].write("move%d:%f" % (self.address, -10))
        sleep(0.4)
        ret = 0
        while ret & 1 == 0:
            ret = self._adevs['bus'].write("?s%d" % (self.address,))
            ret = int(ret[ret.find(":")+1:-1])
            if time.time() > self._stime + self.timeout:
                    self._adevs['bus'].write("q%d" % (self.address,))
                    raise NicosError("could not reach reset position within timeout")
            sleep(0.1)
        self._adevs['bus'].write("move%d:%f" % (self.address, 0.3))
        sleep(0.4)
        ret = 0
        while ret & 1 == 0:
            ret = self._adevs['bus'].write("?s%d" % (self.address,))
            ret = int(ret[ret.find(":")+1:-1])
            if time.time() > self._stime + self.timeout:
                self._adevs['bus'].write("q%d" % (self.address,))
                raise NicosError("could not reach reset position within timeout")
            sleep(0.1)
        self._adevs['bus'].write("ffast%d:%f" % (self.address, self.ref_speed))
        self._adevs['bus'].write("frun%d:%f" % (self.address, 100))
        self._adevs['bus'].write("move%d:%f" % (self.address, -10))
        sleep(0.4)
        ret = 0
        while ret & 1 == 0:
            ret = self._adevs['bus'].write("?s%d" % (self.address,))
            ret = int(ret[ret.find(":")+1:-1])
            if time.time() > self._stime + self.timeout:
                self._adevs['bus'].write("q%d" % (self.address,))
                raise NicosError("could not reach reset position within timeout")
            sleep(0.1)
        self._adevs['bus'].write("zero%d" % (self.address,))
        self._adevs['bus'].write("ffast%d:%f" % (self.address, self.std_speed))
        sspeed = int (round(self.std_speed / 4.0))
        self._adevs['bus'].write("frun%d:%f" % (self.address, sspeed))

