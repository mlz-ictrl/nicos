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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""Huber Motor Controller Protocol NICOS driver."""

from time import sleep, time as currenttime

from IO import StringIO

from nicos.core import status, intrange, oneofdict, Device, Moveable, Override, \
     Param, NicosError, CommunicationError, ProgrammingError, HasTimeout, \
     TimeoutError
from nicos.devices.taco.core import TacoDevice


class ModBusDriverHP(TacoDevice, Device):
    """Basic Huber Protocol client class."""

    taco_class = StringIO

    parameters = {
        'maxtries': Param('Maximum tries before raising',
                          type=int, default=50),
    }

    def write(self, istr):
        istr2 = istr
        iexit = False
        for j in range(4):
            for i in self._huberCmds[j]:
                if istr2.find(i, 0, len(i)) != -1:
                    iexit = True
                    hcmd = (j, self._huberCmds[j].index(i))
                    break
            if iexit:
                break
        if not iexit:
            # positioning command or unknown command
            if len(istr2) > 3:
                if istr2[1] == ":" or istr2[2] == ":":
                    hcmd = (5, "positioning command")
                else:
                    raise ProgrammingError(self, 'unknown command: %s' %
                                           (istr2,))
            else:
                raise ProgrammingError(self, 'unknown command: %s' % (istr2,))
        maxtry = self.maxtries
        self.log.debug('bus write : %s' % (istr,))
        while 1:
            if hcmd[0] == 3:
                ret = self._taco_guard(self._dev.communicate, istr)
                if len(ret) < 4 or "!" + chr(13)+"2C" in ret:
                    maxtry -= 1
                    if maxtry == 0:
                        raise CommunicationError(self, 'could not read from'
                                                 'device')
                    continue
                return ret
            else:
                self._taco_guard(self._dev.writeLine, istr)
                sleep(0.1)
                return "ok"

    def doInit(self, mode):
        self._huberCmds = [
            ["acc", "alias", "conf", "def", "dec", "ecl", "ect", "edev",
             "edir", "eres", "est", "esh", "ffast", "vfast", "fref", "vref",
             "frun", "vrun", "gden", "gn", "gnum", "gz", "macc", "mdec",
             "mdir", "mdl", "rofs", "nofs", "update"],
            ["stop", "quit", "q", "dfi", "*fi", "dhs", "*hs", "beepoff",
             "beepon", "ccnt", "clr", "count", "ccount", "date", "doff",
             "lcdoff", "don", "lcdon", "dout", "io", "echooff", "echoon",
             "eref", "fast", "fget", "goto", "load", "local", "loc", "lpox",
             "move", "movec", "org", "osc", "pos", "priority", "prio", "ref",
             "reboot", "restart", "remote", "rem", "reset", "clear", "run",
             "save", "step", "shutdown", "time", "zero"],
            ["cnt", "cntc", "cnts", "delay", "end", "fi", "gosub", "sub",
             "gsb", "hs", "in", "jump", "jmp", "lin", "nl", "out", "res",
             "ret", "set", "start"],
            ["?cnt", "?conf", "?cfg", "?e", "?ec", "?osc", "?pgm", "?getp",
             "*idn?", "?v", "?io", "?in", "?line", "?ln", "?lin", "?p",
             "?status", "?c", "?s", "?"]]
        self._buffer = []     # buffer for input lines


class RadialCollimator(HasTimeout, Moveable):
    """Start/Stop movement of radial collimator"""

    attached_devices = {
        'bus': (ModBusDriverHP, 'Serial communication bus'),
    }

    parameters = {
        'address':     Param('Address of the motor',
                             type=intrange(1, 16), default=7),
        'start_angle': Param('Start angle of oscillation',
                             type=float, default=1.0),
        'stop_angle':  Param('Stop angle of oscillation',
                             type=float, default=5.4),
        'std_speed':   Param('Default speed',
                             type=int, default=1200),
        'ref_speed':   Param('Speed when referencing',
                             type=int, default=100),
    }
    parameter_overrides = {
        'timeout': Override(default=120),
    }

    valuetype = oneofdict({1: 'on', 0: 'off'})

    def doInit(self, mode):
        self._stime = 0

    def doStart(self, target):
        bus = self._adevs['bus']
        if target == 'on':
            # self._stime = currenttime()
            # bus.write("osc%d:0" % (self.address,))
            # sleep(0.1)
            # bus.write("goto%d:%f" % (self.address, self.start_angle))
            # sleep(0.1)
            # ret = 0
            # while ret & 1 == 0:
            #     ret = bus.write("?s%d" % (self.address,))
            #     ret = int(ret[ret.find(":")+1:])
            #     if currenttime() > self._stime + self.timeout:
            #         bus.write("q%d" % (self.address,))
            #         raise NicosError(self, 'could not reach reset position'
            #                          'within timeout')
            #     sleep(0.1)
            # bus.write("osc%d:%f" % (self.address, self.stop_angle -
            #                         self.start_angle))
            # sleep(0.1)
            if self.status()[0] == status.OK:
                bus.write("clr")
                bus.write("%d:a%.1f" % (self.address, self.start_angle))
                bus.write("nl")
                bus.write("%d:a%.1f" % (self.address, self.stop_angle))
                bus.write("nl")
                bus.write("jmp1")
                bus.write("nl")
                bus.write("end")
                bus.write("start")
        else:
            # self._adevs['bus'].write("osc%d:0" % (self.address,))
            # sleep(0.1)
            # bus.write("q%d" % (self.address,))
            bus.write("q" % ())

    def doStop(self):
        self.log.info('note: radial collimator does not use stop() anymore, '
                      'use move(%s, "off")' % self)

    def _rc_status(self):
        try:
            ret = self._adevs['bus'].write("?s%d" % (self.address,))
        except NicosError:
            raise CommunicationError(self, 'could not get the status of the '
                                     'motor axis of the radial collimator')
        val = int(ret[ret.find(":")+1:-1])
        self.log.debug('_rc_status is %d, 0x%04x' % (val, val))
        return val

    def doStatus(self, maxage=0):
        val = self._rc_status()
        if (val & 0x001) == 0x001:  # Controller passive
            return (status.OK, 'stopped')
        elif (val & 0x040) == 0x040:  # Program execution active
            return (status.BUSY, 'oscillating')
        elif (val & 0x100) == 0x100:   # Oscillation active
            return (status.BUSY, 'oscillating')
        else:
            return (status.UNKNOWN, 'unknown')

    def doRead(self, maxage=0):
        try:
            ret = self._adevs['bus'].write("?p%d" % (self.address,))
            return float(ret[ret.find(":")+1:-1])
        except (NicosError, ValueError):
            raise CommunicationError(self, 'could not get the status of the '
                                     'motor axis of the radial collimator')

    def doReset(self):
        # doReset is blocking, may take a while!
        timeouterr = 'could not reach reset position within timeout'
        self._stime = currenttime()
        bus = self._adevs['bus']
        # bus.write("osc%d:0" % (self.address,))
        bus.write("ffast%d:%f" % (self.address, 200))
        bus.write("frun%d:%f" % (self.address, 100))
        bus.write("move%d:%f" % (self.address, -10))
        sleep(0.4)
        try:
            self.wait()
        except NicosError:
            raise TimeoutError(self, timeouterr)
        bus.write("move%d:%f" % (self.address, 0.3))
        sleep(0.4)
        try:
            self.wait()
        except NicosError:
            raise TimeoutError(self, timeouterr)
        bus.write("ffast%d:%f" % (self.address, self.ref_speed))
        bus.write("frun%d:%f" % (self.address, 100))
        bus.write("move%d:%f" % (self.address, -10))
        sleep(0.4)
        try:
            self.wait()
        except NicosError:
            raise TimeoutError(self, timeouterr)
        bus.write("zero%d" % (self.address,))
        bus.write("ffast%d:%f" % (self.address, self.std_speed))
        sspeed = int(round(self.std_speed / 4.0))
        bus.write("frun%d:%f" % (self.address, sspeed))
