# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************

import time

from nicos import session
from nicos.core import SIMULATION, Attach, Moveable, Param, oneof, pvname
from nicos.core.errors import MoveError, NicosTimeoutError
from nicos.core.mixins import HasPrecision
from nicos.core.utils import multiWait
from nicos.devices.epics.pyepics import EpicsDevice
from nicos.devices.generic.sequence import SeqMethod, SeqSleep, SequenceItem, \
    SequencerMixin

from nicos_sinq.devices.epics.extensions import EpicsCommandReply


class SetSPS(SequenceItem):

    def __init__(self, controller, target):
        SequenceItem.__init__(self)
        self._target = target
        self._controller = controller
        self._start_time = time.time()

    def check(self):
        return True

    def run(self):
        session.log.info('Switching to slit stage %d', self._target)
        command = 'S000%1.1d' % (self._target-1)
        self._controller._put_pv('writepv', command)

    def isCompleted(self):
        if self._controller.read(0) == self._target:
            return True
        if time.time() > self._start_time + 10:
            raise NicosTimeoutError('Timeout setting SPS')
        return False


class AldiController(SequencerMixin, EpicsDevice, Moveable):
    """
    This is the controller responsible for switching between slit
    stages. See AldiMotor below.
    """
    attached_devices = {
        'motors': Attach('Motors to manage while switching',
                         Moveable, multiple=True),
        'motor_controller': Attach('Direct connection to motor controller',
                                   EpicsCommandReply),
    }
    parameters = {
        'readpv': Param('PV to read the digital input waveform', type=pvname,
                        mandatory=True, settable=False, userparam=False),
        'writepv': Param('PV to send the command to toggle state',
                         type=pvname, mandatory=True, settable=False,
                         userparam=False),
    }

    valuetype = oneof(1, 2, 3)

    _aldimotors = [('d1b', 'd1t'), ('d2b', 'd2t'), ('d3b', 'd3t')]

    def _get_pv_parameters(self):
        return {'readpv', 'writepv'}

    _savedpos = []

    def doStart(self, target):
        """Generate and start a sequence if non is running.

        Just calls ``self._startSequence(self._generateSequence(target))``
        """
        if self._seq_is_running():
            if self._mode == SIMULATION:
                self._seq_thread.join()
                self._seq_thread = None
            else:
                raise MoveError(self, 'Cannot start device, sequence is still '
                                      'running (at %s)!' % self._seq_status[1])
        self._startSequence(self._generateSequence(target))

    def doRead(self, maxage=0):
        data = self._pvs['readpv'].get(16)
        testbyte = data[8]
        for ii in range(0, 3):
            if (testbyte & 1 << ii) > 0:
                return ii+1

    def _setMotorPar(self, target):
        vals = [(61400, 63800), (63200, 64600), (62700, 61000)]
        v = vals[target-1]

        com = 'V 7 %d' % v[0]
        self._attached_motor_controller.execute(com)
        com = 'V 8 %d' % v[1]
        self._attached_motor_controller.execute(com)

    def _refrun(self):
        self.log.info('Starting reference runs...')
        for mot in self._attached_motors:
            mot.reference()
            self.log.info('Reference run for %s finished\n', mot.name)

    def _runToSaved(self):
        self.log.info('Driving back to start positions...')
        for mot in self._aldimotors[self.target-1]:
            aldimot = session.getDevice(mot)
            aldimot.startBack()
        multiWait(self._attached_motors)

    def _generateSequence(self, target):
        seq = []

        seq.append(SetSPS(self, target))

        seq.append(SeqMethod(self, '_setMotorPar', target))

        seq.append(SeqSleep(10.))

        # seq.append(SeqMethod(self, '_refrun'))

        # seq.append(SeqSleep(2.))

        seq.append(SeqMethod(self, '_runToSaved'))

        return seq


class AldiMotor(HasPrecision, Moveable):
    """
    Morpheus has the bottom and top slit motors shared between three
    slits with an SPS being responsible for switching between the slit
    stages. Whenever a slit stage needs to be changed, some parameters have
    to be sent to the motor controller and a reference run has to be made.
    This is the responsability of the AldiController defined below.
    """

    parameters = {
        'stage_number': Param('Number of the stage this motor is on',
                              type=oneof(1, 2, 3)),
    }

    attached_devices = {
        'real_motor': Attach('Real motor to drive', Moveable),
        'controller': Attach('Controller for switching stages',
                             AldiController),
    }

    _switching = False

    def startBack(self):
        # Run back to the last known target
        self._switching = False
        if self.target:
            self.start(self.target)
        else:
            self.start(20.)

    def doStart(self, target):
        if self.stage_number == self._attached_controller.read(0):
            self._attached_real_motor.start(target)
        else:
            if self._attached_controller.isCompleted():
                self._attached_controller.start(self.stage_number)
            self._switching = True

    def doStatus(self, maxage=0):
        # Status is the controller status when switching, else the
        # motor status
        if self._switching:
            status, reason = self._attached_controller.status(maxage)
            if status in self.busystates:
                return status, reason
            self._attached_real_motor.start(self.target)
            self._switching = False
        else:
            return self._attached_real_motor.status(maxage)

    def doRead(self, maxage=0):
        if self.stage_number == self._attached_controller.read(0):
            return self._attached_real_motor.read(maxage)
        if self.target:
            return self.target
        # This can happen when this has never run or the cache
        # value is lost.
        return 20.

    def doIsAllowed(self, target):
        return self._attached_real_motor.isAllowed(target)

    def doIsAtTarget(self, pos, target):
        return self._attached_real_motor.isAtTarget(pos, target)
