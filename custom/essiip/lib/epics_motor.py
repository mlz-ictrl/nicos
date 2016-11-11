from nicos.devices.epics import EpicsAnalogMoveable
from nicos.core import status, Param, Override, pvname
from nicos.devices.abstract import Motor, HasOffset, CanReference


class EpicsMotor(CanReference, HasOffset, EpicsAnalogMoveable, Motor):
    """
    This device exposes some of the functionality provided by the EPICS motor record.
    The PV-names for the fields of the record (readback, speed, etc.) are derived
    by combining the motorpv-parameter with the predefined field names.
    """
    parameters = {
        'motorpv': Param('Name of the motor record PV.',
                         type=pvname, mandatory=True, settable=False),
    }

    parameter_overrides = {
        # readpv and writepv are determined automatically from the base-PV
        'readpv': Override(mandatory=False, userparam=False, settable=False),
        'writepv': Override(mandatory=False, userparam=False, settable=False),

        # speed may change from outside, can't rely on cache
        'speed': Override(volatile=True),
    }

    # Fields of the motor record with which an interaction via Channel Access is required.
    motor_record_fields = {
        'readpv': 'DRBV',
        'writepv': 'DVAL',
        'donemoving': 'DMOV',
        'stop': 'STOP',

        'homeforward': 'HOMF',
        'homereverse': 'HOMR',

        'speed': 'VELO',
        'set': 'SET',

        'highlimit': 'DHLM',
        'lowlimit': 'DLLM',
    }

    def _get_pv_parameters(self):
        """
        Implementation of inherited method to automatically account for fields present in motor record.
        :return: List of PV aliases.
        """
        return self.motor_record_fields.keys()

    def _get_pv_name(self, pvparam):
        """
        Implementation of inherited method that translates between PV aliases and actual PV names. Automatically adds
        a prefix to the PV name according to the motorpv parameter.
        :param pvparam: PV alias.
        :return: Actual PV name.
        """
        motor_record_prefix = getattr(self, 'motorpv')
        motor_field = self.motor_record_fields[pvparam]

        return '.'.join((motor_record_prefix, motor_field))

    def doReadSpeed(self):
        return self._get_pv('speed')

    def doWriteSpeed(self, newValue):
        speed = self._get_valid_speed(newValue)

        if speed != newValue:
            self.log.warning('Selected speed %s is outside the parameter '
                             'limits, using %s instead.', newValue, speed)

        self._put_pv('speed', speed)

    def _get_valid_speed(self, newValue):
        min_speed = self._get_pvctrl('speed', 'lower_ctrl_limit', 0.0)
        max_speed = self._get_pvctrl('speed', 'upper_ctrl_limit', 0.0)

        valid_speed = newValue
        if min_speed != 0.0:
            valid_speed = max(min_speed, valid_speed)

        if max_speed != 0.0:
            valid_speed = min(max_speed, valid_speed)

        return valid_speed

    def doRead(self, maxage=0):
        return self._get_pv('readpv') - self.offset

    def doStart(self, pos):
        self._put_pv_blocking('writepv', pos + self.offset)

    def doStatus(self, maxage=0):
        done_moving = self._get_pv('donemoving')

        if done_moving == 0:
            return status.BUSY, 'Motor is moving to target...'

        return status.OK, ''

    def doStop(self):
        self._put_pv('stop', 1, False)

    def doReadAbslimits(self):
        absmin = self._get_pv('lowlimit')
        absmax = self._get_pv('highlimit')

        return (absmin, absmax)

    def doReference(self):
        self._put_pv_blocking('homeforward', 1)
