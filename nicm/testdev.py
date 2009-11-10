# -*- coding: utf-8 -*-
"""
    nicm.testdev
    ~~~~~~~~~~~~

    Virtual devices for testing.
"""

from nicm import nicos
from nicm.device import Device, Moveable
from nicm.motor import Motor
from nicm.coder import Coder
from nicm.commands import printdebug


class VirtualMotor(Motor):
    parameters = {
        'initval': (0, True, 'Initial value for the virtual device.'),
    }

    def doInit(self):
        self._val = self.getPar('initval')

    def doStart(self, pos):
        self.printdebug('moving to %s' % pos)
        self._val = pos

    def doRead(self):
        return self._val


class VirtualCoder(Coder):

    def doRead(self):
        return 0
