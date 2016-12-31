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
#   Aleks Wischolit <aleks.wischolit@frm2.tum.de>
#
# *****************************************************************************

from nicos.core import Readable, Override, status
from nicos.devices.taco.core import TacoDevice
from IO import AnalogInput


class TemperatureA(TacoDevice, Readable):

    taco_class = AnalogInput

    parameter_overrides = {
        'unit':  Override(mandatory=False, default='K'),
    }

    def doRead(self, maxage=0):
        tmp = self._taco_guard(self._dev.read())

##      FileName=time.strftime ("%d.%m.%Y") + "_RESEDA_TemperatureLog.txt"
##      Clock=time.strftime("%H:%M:%S")


##      File=open(FileName, "a")
##      File.write(Clock)
##      File.write("\tTemperature A: %.3f K\n" % tmp)

##      File.close()


        return tmp

    def doStatus(self, maxage=0):
        return status.OK, ''



class TemperatureB(TacoDevice, Readable):

    taco_class = AnalogInput

    parameter_overrides = {
        'unit':  Override(mandatory=False, default='K'),
    }

    def doRead(self, maxage=0):
        tmp = self._taco_guard(self._dev.read())

##      FileName=time.strftime ("%d.%m.%Y") + "_RESEDA_TemperatureLog.txt"
##      Clock=time.strftime("%H:%M:%S")


##      File=open(FileName, "a")
##      File.write(Clock)
##      File.write("\tTemperature B: %.3f K\n" % tmp)

##      File.close()


        return tmp

    def doStatus(self, maxage=0):
        return status.OK, ''



class TemperatureC(TacoDevice, Readable):

    taco_class = AnalogInput

    parameter_overrides = {
        'unit':  Override(mandatory=False, default='K'),
    }

    def doRead(self, maxage=0):
        tmp = self._taco_guard(self._dev.read())

##      FileName=time.strftime ("%d.%m.%Y") + "_RESEDA_TemperatureLog.txt"
##      Clock=time.strftime("%H:%M:%S")


##      File=open(FileName, "a")
##      File.write(Clock)
##      File.write("\tTemperature C: %.3f K\n" % tmp)

##      File.close()


        return tmp

    def doStatus(self, maxage=0):
        return status.OK, ''


class TemperatureD(TacoDevice, Readable):

    taco_class = AnalogInput

    parameter_overrides = {
        'unit':  Override(mandatory=False, default='K'),
    }

    def doRead(self, maxage=0):
        tmp = self._taco_guard(self._dev.read())

##      FileName=time.strftime ("%d.%m.%Y") + "_RESEDA_TemperatureLog.txt"
##      Clock=time.strftime("%H:%M:%S")


##      File=open(FileName, "a")
##      File.write(Clock)
##      File.write("\tTemperature D: %.3f K\n\n" % tmp)

##      File.close()


        return tmp

    def doStatus(self, maxage=0):
        return status.OK, ''
