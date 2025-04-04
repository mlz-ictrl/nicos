# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************
import os
from datetime import datetime

from nicos import session
from nicos.commands.output import printinfo
from nicos.core import Attach, CanDisable, HasPrecision, IsController, \
    Moveable, Override, Param, Readable, listof, oneof, status, tupleof
from nicos.core.params import limits as unpack_limits
from nicos.core.utils import multiStatus
from nicos.devices.abstract import Motor
from nicos.devices.epics.pyepics import EpicsDevice, EpicsDigitalMoveable, \
    EpicsReadable
from nicos.devices.epics.pyepics.motor import EpicsMotor

from nicos_sinq.devices.epics.extensions import EpicsCommandReply

# pitch
UNSELECTED = -3000
NARROW = 1
WIDE = 0

SELECTED = 1

ACTIVE = 1
INACTIVE = 0


class EpicsDigitalReadable(EpicsReadable):
    """
    Handles EPICS devices which can set and read an integer value.
    """
    valuetype = int


class DigitalInput(CanDisable, EpicsDigitalReadable):
    # Device that interact with the PLC to enable/disable/select one of the
    # pitches
    # Warning: there is an inconsistency between the EPICS and PLC logic.
    # The SPS toggles the motor on/off every time a "1" is received. After
    # activation (deactivation) of the motor the PV has to be put back to "0".

    parameters = {
        'pitch': Param('ID of the corresponding pitch', type=int,
                       mandatory=True),
        'pvprefix': Param('PV prefix', type=str, mandatory=True),
        'selectable': Param('Whether the pitch can be selected or not',
                            settable=False, volatile=True, mandatory=False),
        'parkposition': Param('Whether the motor is at park position or not',
                              settable=False, volatile=True, mandatory=False)
    }

    parameter_overrides = {
        'unit': Override(default='', mandatory=False),
        'readpv': Override(mandatory=False, userparam=False, settable=False),
    }

    record_fields = {}
    pv_cache_relations = {'readpv': 'value'}

    def doPreinit(self, mode):
        self.record_fields.update({
            'select': f'P{self.pitch}:Select',
            'selectable': f'P{self.pitch}:Selectable',
            'park_position': f'P{self.pitch}:ParkPosition',
            'alarm': f'P{self.pitch}:Alarm',
        })
        EpicsDigitalReadable.doPreinit(self, mode)
        self._selection_state = UNSELECTED

    def _get_pv_parameters(self):
        """
        Return the list of the aliases for the pvs.

        :return: List of PV aliases.
        """

        pvs = EpicsDigitalReadable._get_pv_parameters(self) | set(
            self.record_fields.keys())
        return pvs

    def _get_pv_name(self, pvparam):
        """
        Translates between PV alias and full PV name.

        :param pvparam: PV alias.
        :return: Actual PV name.
        """
        record_prefix = getattr(self, 'pvprefix')
        field = self.record_fields.get(pvparam)

        if field:
            return ':'.join((record_prefix, field))

        return getattr(self, pvparam)

    def doRead(self, maxage=0):
        return self._get_pv('readpv')

    def doStatus(self, maxage=0):
        general_epics_status, _ = self._get_mapped_epics_status()

        if general_epics_status == status.ERROR:
            return status.ERROR, 'Unknown problem in record'

        if self._get_pv('alarm'):
            return status.ERROR, 'Alarm raised from SPS'

        if (self.doRead() != self._selection_state and
                self._selection_state != UNSELECTED):
            return status.BUSY, 'Switching status'

        return status.OK, '' if self.selectable else 'Not selectable'

    def doEnable(self, on):
        self._selection_state = on
        enabled = self.doRead()
        if on:
            if self.selectable and not enabled:
                self._put_pv_blocking('select', 1)
                self._put_pv_blocking('select', 0)
        else:
            if enabled:
                self._put_pv_blocking('select', 1)
                self._put_pv_blocking('select', 0)

    def doReadSelectable(self):
        return self._get_pv('selectable')

    def doReadParkposition(self):
        return self._get_pv('park_position')


class RangeSelector(EpicsDigitalMoveable):
    """
    Device that accounts for the representation of the MCU in the PLC
    """

    parameters = {
        'id': Param('ID of the corresponding MCU', type=int, mandatory=True),
        'pvprefix': Param('PV prefix', type=str, mandatory=True),
    }

    parameter_overrides = {
        'unit': Override(default='', mandatory=False),
        'readpv': Override(mandatory=False, userparam=False, settable=False),
        'writepv': Override(mandatory=False, userparam=False, settable=False),
    }

    record_fields = {}
    pv_cache_relations = {'readpv': 'value', 'writepv': 'target'}

    valuetype = int  # oneof(NARROW, WIDE)

    def doPreinit(self, mode):
        self.record_fields.update({
            'move': f'MCU{self.id}:Move',
        })
        EpicsDigitalMoveable.doPreinit(self, mode)
        self._range = UNSELECTED

    def _get_pv_parameters(self):
        pvs = set(self.record_fields.keys()) | \
              EpicsDigitalMoveable._get_pv_parameters(self)
        return pvs

    def _get_pv_name(self, pvparam):
        """
        Translates between PV alias and full PV name. Has to account for asyn
        fields that contain '.'

        :param pvparam: PV alias.
        :return: Actual PV name.
        """
        record_prefix = getattr(self, 'pvprefix')
        field = self.record_fields.get(pvparam)

        if field:
            return ':'.join((record_prefix, field)).replace(':.', '.')

        return getattr(self, pvparam)

    def doIsAtTarget(self, pos, target):
        if pos != self._range:
            return False
        return True

    def doRead(self, maxage=0):
        return self._get_pv('readpv')

    def doStart(self, target):
        self._range = target
        if self.doRead() != target:
            self._put_pv_blocking('writepv', 1)
            self._put_pv_blocking('writepv', 0)

    def doStatus(self, maxage=0):
        stat, message = EpicsDevice.doStatus(self, maxage)
        if stat == status.ERROR:
            return stat, message or 'Unknown problem in record'
        elif stat == status.WARN:
            return stat, message

        if self._get_pv('readpv') != self._range and\
                self._range != UNSELECTED:
            return status.BUSY, 'Switching range'
        return status.OK, ''


class SeleneEpicsMotor(EpicsMotor):

    parameter_overrides = {
        'abslimits': Override(volatile=True, settable=True),
    }

    pv_cache_relations = {'readpv': 'value', 'writepv': 'target'}

    def _get_record_fields(self):
        record_fields = EpicsMotor._record_fields
        record_fields.update({
                'highlimit': 'DHLM',
                'lowlimit': 'DLLM',
                'set_position': '-SetPosition',
            })
        return record_fields

    def _get_pv_parameters(self):
        """
        Implementation of inherited method to automatically account for fields
        present in motor record.
        :return: List of PV aliases.
        """
        if self.errormsgpv:
            self.pv_cache_relations['errormsgpv'] = 'errormsg'
        if self.errorbitpv:
            self.pv_cache_relations['errorbitpv'] = 'errorbit'
        if self.reseterrorpv:
            self.pv_cache_relations['reseterrorpv'] = 'reseterror'
        return EpicsMotor._get_pv_parameters(self)

    def _get_pv_name(self, pvparam):
        """
        Special implementation to account for the presence of'-SetPosition'

        :param pvparam: PV alias.
        :return: Actual PV name.
        """
        pv_name = EpicsMotor._get_pv_name(self, pvparam)
        if '.-' in pv_name:
            return pv_name.replace('.-', '-')
        return pv_name

#   def _get_pv(self, pvparam, as_string=False):
#        return self._get_pv(pvparam)

    def doWriteAbslimits(self, limits):
        """
        Set the limits for the motor. In this case there is no difference among
        user- and abslimits, BOTH must be set to the same value. One must be
        careful on the order, though: when we shrink the limits, first set the
        userlimits, then the abs-. When we enlarge the range we first have to
        set the abslimits, then the user-.
        :param limits: a pair (lowlimit, highlimit)
        :return: None
        """

        low, high = unpack_limits(limits)

        self._put_pv_blocking('lowlimit', -10)
        self._put_pv_blocking('highlimit', 10)
        self.userlimits = limits
        self._put_pv_blocking('lowlimit', low)
        self._put_pv_blocking('highlimit', high)

    def isAtEndswitch(self):
        return self._get_pv('lowlimitswitch') or \
               self._get_pv('highlimitswitch')


def check_pitch(f):
    def wrapper(*args):
        if args[0].pitch == UNSELECTED:
            args[0].cache.put(
                args[0]._name, 'status', (status.ERROR, 'pitch not selected')
            )
            raise IndexError('pitch not selected')
        return f(*args)

    return wrapper


class Selene(CanDisable, HasPrecision, IsController, Moveable):

    valuetype = float

    parameters = {
        'npitch': Param('Number of mirror segments', type=int, default=36,
                        mandatory=False, userparam=False, settable=False,),
        '_pitch': Param('Currently selected pitch', type=int,
                        default=UNSELECTED, mandatory=False, userparam=False,
                        settable=True,),
        'position': Param('Actual positions of the pitch', type=listof(float),
                          mandatory=True, userparam=False, settable=False,
                          prefercache=True,),
        'working_position': Param('Default position', type=listof(float),
                                  mandatory=True, userparam=False,
                                  settable=False, prefercache=True,),
        'low_limit_narrow': Param('Low limits in the narrow range',
                                  type=listof(float), mandatory=True,
                                  userparam=False, settable=False,
                                  prefercache=True,),
        'high_limit_narrow': Param('High limits in the narrow range',
                                   type=listof(float), mandatory=True,
                                   userparam=False, settable=False,
                                   prefercache=True,),
        'low_limit_wide': Param('Low limits in the wide range',
                                type=listof(float), mandatory=True,
                                userparam=False, settable=False,
                                prefercache=True,),
        'high_limit_wide': Param('High limits in the wide range',
                                 type=listof(float), mandatory=True,
                                 userparam=False, settable=False,
                                 prefercache=True,),
        'low_limit_hw': Param('Hardware low limits', type=listof(float),
                              mandatory=False, userparam=False, settable=False,
                              prefercache=True,),
        'high_limit_hw': Param('Hardware high limits', type=listof(float),
                               mandatory=False, userparam=False,
                               settable=False, prefercache=True,),
        'reference_position': Param('Reference position', type=listof(float),
                                    mandatory=False, userparam=False,
                                    settable=False, prefercache=True,),
        'backup_path': Param('Folder where the position and limits will be '
                             'saved', mandatory=True, userparam=False,
                             settable=False, type=str,),
        'limits': Param('Limits for the pitch currently selected',
                        settable=False, volatile=True, mandatory=False,
                        type=tupleof(float, float)),
        'range': Param('Whether the movement can be in the narrow or wide '
                       'range', type=oneof(None, NARROW, WIDE),
                       settable=True, volatile=True, mandatory=False),
        'enabled': Param('Whether the pitch is enabled or not '
                         'range', type=oneof(None, ACTIVE, INACTIVE),
                         settable=False, volatile=True, mandatory=False),
    }

    parameter_overrides = {
        'unit': Override(mandatory=False),
    }

    attached_devices = {
        'digital_input': Attach('Pitch channels', Readable, multiple=True),
        'motor': Attach('Motor', Moveable, multiple=True),
        'range_selector': Attach('Pitch channels', Moveable, multiple=True),
        'asyn': Attach('Direct communications to the MCUs', EpicsCommandReply)
    }

    def doInit(self, mode):
        self._status_message = ''
        self._mid = self._get_motor_id()

    def isAdevTargetAllowed(self, adev, adevtarget):
        if not isinstance(adev, Motor):
            return True, ''
        if adevtarget is None:
            adevtarget = self.position[self._pitch]
        low, high = self._attached_motor[self._get_motor_id()].userlimits
        if low <= adevtarget <= high:
            return True, ''
        return False, 'target is outside limits, can\'t be moved'

    @check_pitch
    def doStart(self, target):
        if not self.enabled:
            self.log.warning('pitch is not active')
            return
        self._attached_motor[self._get_motor_id()].maw(target)
        self.update_position()

    def doRead(self, maxage=0):
        """
        This is only needed to use `maw`
        :param maxage:
        :return: the position of the motor that is currently selected via the
        pitch
        """
        if self._pitch == UNSELECTED:
            return None
        return self._attached_motor[self._get_motor_id()].read(maxage)

    def doStatus(self, maxage=0):
        if self._pitch == UNSELECTED:
            return status.UNKNOWN, 'No pitch selected'

        motor_id = self._get_motor_id()
        first = motor_id * self.npitch // 2
        last = (motor_id + 1) * self.npitch // 2

        query_adevs = [
            self._attached_motor[motor_id],
            self._attached_range_selector[motor_id],
        ]
        query_adevs += [
            self._attached_digital_input[p + motor_id * self.npitch // 2]
            for p in range(first, last)
        ]

        st, msg = multiStatus(query_adevs, maxage)
        msg = ', '.join([m for m in msg.split(',') if 'Not selectable' not in
                         m])

        return st, msg

    def doPoll(self, n, maxage):
        self._pollParam('enabled')

    def doReadEnabled(self):
        if self._pitch == UNSELECTED:
            return None
        return self._attached_digital_input[self._pitch].read(0) == ACTIVE

    @property
    def pitch(self):
        """
        Return the number of the pitch currently selected
        :return: the pitch number
        """
        if self._pitch == UNSELECTED:
            return None
        return self._pitch + 1

    @pitch.setter
    def pitch(self, pitch):
        """
        Select (not enable) a pitch.
        If a pitch is enable, first eventually deactivate it (if so, store the
        motor position), then set the new pitch.
        :param pitch:
        :return:
        """
        if not self._attached_digital_input[pitch - 1].selectable:
            self.log.warning('pitch %d is not selectable', pitch)

        # disable current pitch and update the position
        if self._pitch != UNSELECTED and self.enabled:
            self.disable()

        # set the new pitch
        self._pitch = pitch - 1
        self._mid = self._get_motor_id()

    def doReadRange(self):
        if self._pitch == UNSELECTED:
            return None
        return self._attached_range_selector[self._get_motor_id()].read()

    def doWriteRange(self, target):
        if self._pitch == UNSELECTED:
            return
        if target ==\
                self._attached_range_selector[self._get_motor_id()].read():
            return

        if self.enabled:
            self.disable()

        if target == WIDE:
            limits = (self.low_limit_wide[self._pitch],
                      self.high_limit_wide[self._pitch],)
        else:
            limits = (self.low_limit_narrow[self._pitch],
                      self.high_limit_narrow[self._pitch],)

        self._attached_motor[self._get_motor_id()].abslimits = limits
        self._attached_range_selector[self._get_motor_id()].maw(target)

    @check_pitch
    def update_position(self):
        """
        Makes sure that the position stored in the 'position' list for the
        current pitch corresponds to the current motor position, and returns
        it
        :param maxage: not used
        :return: the current motor position
        """
        self.log.warning('update position of pitch %d', self.pitch)
        position = list(self.position)
        position[self._pitch] =\
            self._attached_motor[self._get_motor_id()].read(0)
        printinfo(
            'Updating position of pitch %d to %f'
            % (self._pitch, self._attached_motor[self._get_motor_id()].read(0))
        )
        self._setROParam('position', position)
        return position[self._pitch]

    def doReadLimits(self):
        if self._pitch == UNSELECTED:
            # this is required to prevent failure at startup
            return 0, 0
        return self._attached_motor[self._get_motor_id()].userlimits

    def doEnable(self, on):
        """
        Enable/disable the pitch
        """
        if not on:
            if not self.enabled:
                return
            self.log.info('disable pitch %d', self.pitch)
            self.update_position()
            self._attached_digital_input[self._pitch].disable()
            self._attached_digital_input[self._pitch].read()
            return

        if self.enabled:
            return
        if not self._attached_digital_input[self._pitch].selectable:
            self.log.error('pitch not selectable')
            return

        def get_limits():
            if self.range == WIDE:
                return self.low_limit_wide[self._pitch], \
                       self.high_limit_wide[self._pitch]
            return self.low_limit_narrow[self._pitch],\
                self.high_limit_narrow[self._pitch]

        position = self.position[self._pitch]
        limits = get_limits()
        printinfo('enable_active: setting pos, limits: %f, %s'
                  % (position, str(limits)))

        # Set the motor position. This should be possible with the PV as well
        self._attached_asyn.execute(
                f'Q{7 + self._get_motor_id()}59={position}')

        self._attached_motor[self._get_motor_id()].abslimits = limits
        self._attached_digital_input[self._pitch].enable()

    @check_pitch
    def move_to_working_position(self):
        """
        Drive the pitch to the working position
        :return: None
        """
        self.maw(self.working_position[self._pitch])
        self.read(0)

    @check_pitch
    def move_off_focus(self):
        """
        Drive the pitch slightly off focus to check alignement without driving
        to parking position.
        :return: None
        """
        if self._pitch < 18:
            storage_position = self.working_position[self._pitch] - 0.35
        else:
            storage_position = self.working_position[self._pitch] + 0.35
        low, high = self._attached_motor[self._get_motor_id()].userlimits
        if (storage_position < low) or (storage_position > high):
            raise ValueError(
                'requested position outside limits, value of '
                'pitch has not been moved'
            )
        self.maw(storage_position)

    @check_pitch
    def set_present_as_working_position(self):
        """
        Stores the current pitch position as the pitch working position
        :return: None
        """
        current_position = self.read(0)
        if (current_position < self.low_limit_narrow[self._pitch]) or (
            current_position > self.high_limit_narrow[self._pitch]
        ):
            self.log.error('this is forbidden in wide range')
            return
        position = list(self.working_position)
        position[self._pitch] = self.position[self._pitch]
        self._setROParam('working_position', position)

    @check_pitch
    def isAtParkingPosition(self):
        """
        Test if the pitch motor is at endswitch. If the pitch is active and the
        motor configured, this is posisble using the EPICS LLS and HLS. If not,
        one must compare the current position with the endswitch position.
        :return: True if at endswitch, else False
        """
        if self.enabled:
            return self._attached_motor[self._get_motor_id()].isAtEndswitch()
        if self._pitch < 18:
            return self.position[self._pitch] > self.high_limit_wide[
                self._pitch]
        return self.position[self._pitch] < self.low_limit_wide[self._pitch]

    @check_pitch
    def doPark(self):
        """
        Drives the motor to parking position using the special MCU command.
        :return: None
        """
        if self.range == NARROW:
            raise RuntimeError('narrow range selected')
        if not self.enabled:
            raise RuntimeError('pitch inactive')
        self._attached_asyn.execute(f'P{7 + self._get_motor_id()}50=3')
        session.delay(1)
        self.wait()

    def unselect(self):
        # disable current pitch and update the position
        if self.range == WIDE and not self.isAtParkingPosition():
            self.log.error('can\'t unselect in wide range')
            return
        if self.enabled:
            self.disable()
        self._pitch = UNSELECTED

    @check_pitch
    def _get_motor_id(self):
        """
        There are two motors driving the two blocks (1-18) and (19-36) of
        pitches. This function can be used to determine which motor drives
        the pitch currently selected.
        :return:
        """
        if self._pitch == UNSELECTED:
            return None
        return self._pitch // (self.npitch // 2)

    def backup(self):
        """
        Create a backup of the device parameters (positions/limits) serialised
        as JSON arrays. The folder name is generated using the current
        date/time. The path to the folder 'backup path' is set in the
        setupfile.
        :return: None
        """
        import json

        backup_folder = datetime.now().strftime('%Y%m%dT%H%M%S')
        os.makedirs(os.path.join(self.backup_path, backup_folder))

        for field in [
            'position',
            'working_position',
            'low_limit_narrow',
            'high_limit_narrow',
            'low_limit_wide',
            'high_limit_wide',
        ]:
            with open(os.path.join(self.backup_path, backup_folder, field),
                      'w', encoding="utf8") as f:
                j = json.loads(json.dumps(getattr(self, field)))
                json.dump(j, f)

    def reload(self, folder):
        """
        Recover the positions/limits from a backup. The path to the backup is a
        parameter of the device.
        :param folder: the name (usually corresponding to the date/time of
        saving) of the folder containing the backup files
        :return: None
        """
        import json

        for field in [
            'position',
            'working_position',
            'low_limit_narrow',
            'high_limit_narrow',
            'low_limit_wide',
            'high_limit_wide',
        ]:
            with open(os.path.join(self.backup_path, folder, field), 'r',
                      encoding="utf8") as f:
                value = json.load(f)
                self._setROParam(field, value)
