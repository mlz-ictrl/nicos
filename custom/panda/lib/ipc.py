#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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

"""IPC class to work around reset bug of triple cards from göttingen"""


from nicos.core import usermethod, status
from nicos.devices.vendor.ipc import Motor as _Motor


# create a workaround class, not resetting
class Motor(_Motor):
    def doReset(self):
        if self._hwtype == 'single':
            _Motor.reset(self)
        else:
            self.log.warning('Resetting triple cards disabled. If you REALLY '
                             'want to reset, use %s.reallyReset() method' %
                             self.name)

    @usermethod
    def reallyReset(self):
        """Reset the device without any additional condition check.

        In comparision to the .`reset` method the motor will be reset without
        any condition.
        """
        _Motor.reset(self)


#
# second possible solution:
#
doc = """
IPC Motor cards made by Göttingen have (at least) two major problems:
a) triple cards reset all three channels upon a reset command.
b) sometimes they drive the stepper motor with wrong stepping frequencies,
   basically not moving it.

a) poses a problem for NICOS, because issuing a reset command to one channel
should not influence other channels. As we don't know which devices (if any)
are connected to the other two channels, we try to store the parameters
(which include the current position) into the internal eeprom before issuing
a reset. This is a real problem, if not all channels are used for encoded axes!

It is still inclear if the reset is needed at all, or what it really does.

b) is difficult, as NICOS assumes that if Hardware (motordriver) says it moved
by a certain number of steps, the corresponding motor actually did just that.
If it doesn't, and the axis has an encoder, NICOS raises an internal Exception
(Schleppfehler) or if the requested movement was small, a PositionError and
then retries the positioning after calling a reset on the motor.
Here a) and b) play together to make instrument scientists very unhappy.

As far as we could figure out, once b) happens, the card appears to be 'locked'
in that state, where it 'forgets' to use the accel-ramp for a movement and
instead just ramps down, starting from twice the normal stepping frequency.
No stepper motor can handle that, so no actual movement happens.
So NICOS again gets an Exception, calls reset and retries until it finally
gives up after maxtries tries.

So far we found one reliably working sequence to go out of this 'locked state'
by issuing a reset and then moving to a slightly different position.
If one of those two steps is missing, it does NOT _reliably_ free the card from
that state. (i.e. sometimes it still works.)

The chance to enter that 'lock'state seems to depend on a combination of
the accel, speed, microstep, position and target value.
We suspect an internal overflow. Unfortunately, once that state is entered,
changing only the target position does not seem to allow it to exit that state.

We try to work around this by following the sequence of:
- change current position a little bit
  (This should avoid entering the 'locked' state again, but still maintain
  (roughly) the same position. THIS IS NOT IDEAL! (anybody have a better idea?)
- save all params to eeprom, so that the other channels of this card are not
  reset to bogus values.
- do a reset (which actually resets all channels!)

    U N T E S T E D !

Firmware-upgrade of the cards is impossible, as the developer is no longer
available and we dont have access to the sourcecode....
"""


# create a workaround class
# if using this, please rename the class!
class MotorUntested(_Motor):
    """UNTESTED!"""
    def doReset(self):
        if self._hwtype == 'triple':
            self.log.warning('Resetting a triple Motor cards, please check '
                             'the result carefully!')
            bus = self._attached_bus
            # make sure we are stopped.
            if self.status(0)[0] != status.OK:  # busy or error
                bus.send(self.addr, 33)  # stop
                try:
                    self.wait()      # this might take a while, ignore errors
                except Exception:
                    pass
            self._store()
            _Motor.reset(self)
            # move by one step (so far this always worked)
            if self.doReadSteps() & 1:
                bus.send(self.addr, 35)  # go in negative direction
            else:
                bus.send(self.addr, 34)  # go in positive direction
            # do ONE step (basically toggling the least-significant bit)
            bus.send(self.addr, 46, 1, 6)
            self.wait()
        else:
            _Motor.reset(self)
