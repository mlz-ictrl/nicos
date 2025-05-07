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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""Meta classes and Mixins for usage in NICOS."""

import threading
import types
from time import monotonic, time as currenttime

from nicos import session
from nicos.core import status
from nicos.core.constants import MAINTENANCE, MASTER, SLAVE
from nicos.core.errors import AccessError, CommunicationError, \
    ConfigurationError, ModeError
from nicos.core.params import Override, Param, anytype, dictof, floatrange, \
    intrange, limits, none_or, nonemptylistof, setof, string, tupleof
from nicos.core.utils import statusString, usermethod
from nicos.utils import formatArgs, lazy_property


class DeviceMixinMeta(type):
    """
    This class provides the __instancecheck__ method for non-Device derived
    mixins.
    """

    def __new__(mcs, name, bases, attrs):
        # set source class for parameters
        if 'parameters' in attrs:
            for pinfo in attrs['parameters'].values():
                pinfo.classname = attrs['__module__'] + '.' + name
        for base in bases:
            if hasattr(base, 'parameters'):
                for pinfo in base.parameters.values():
                    if pinfo.classname is None:
                        pinfo.classname = base.__module__ + '.' + base.__name__
        newtype = type.__new__(mcs, name, bases, attrs)
        for entry in newtype.__mergedattrs__:
            newentry = {}
            for base in reversed(bases):
                if hasattr(base, entry):
                    newentry.update(getattr(base, entry))
            newentry.update(attrs.get(entry, {}))
            setattr(newtype, entry, newentry)

        # add usermethods to registry, check names of methods to comply with
        # coding style
        for aname in attrs:
            if aname.startswith(('_', 'do')):
                continue
            value = getattr(newtype, aname)
            if not isinstance(value, (types.FunctionType, types.MethodType)):
                continue
            if hasattr(value, 'help_arglist'):
                args = '(%s)' % value.help_arglist
            else:
                args = formatArgs(value, strip_self=True)
            if value.__doc__:
                docline = value.__doc__.strip().splitlines()[0]
            else:
                docline = ''
            newtype.methods[aname] = (args, docline, newtype,
                                      hasattr(value, 'is_usermethod'))

        return newtype

    def __instancecheck__(cls, inst):
        from nicos.core.device import DeviceAlias, NoDevice  # isort:skip
        if inst.__class__ == DeviceAlias and inst._initialized:
            if isinstance(inst._obj, NoDevice):
                return issubclass(inst._cls, cls)
            return isinstance(inst._obj, cls)
        # does not work with Python 2.6!
        # return type.__instancecheck__(cls, inst)
        return issubclass(inst.__class__, cls)


class DeviceMixinBase(metaclass=DeviceMixinMeta):
    """
    Base class for all NICOS device mixin classes not derived from `Device`.

    This class sets the correct metaclass and is easier to use than setting the
    metaclass on each mixin class.  Mixins **must** derive from this class.
    """

    __mergedattrs__ = ['parameters', 'parameter_overrides', 'attached_devices',
                       'methods']


class AutoDevice(DeviceMixinBase):
    """Abstract mixin for devices that are created automatically as dependent
    devices of other devices.
    """


class HasAutoDevices(DeviceMixinBase):
    """
    This mixin can be inherited from device classes creating ``AutoDevices``.
    """

    autodevices = None

    parameters = {
        'autodevice_visibility': Param('Selects in which context the auto '
                                       'created devices should be '
                                       'shown/included',
                                       type=setof('metadata', 'namespace',
                                                  'devlist'),
                                       default=(),
                                       ),
    }

    def add_autodevice(self, autodevname, cls, **devparams):
        """
        Create the ``AutoDevice`` with the class given by the cls parameter.

        Fill the self.autodevices list with the names of the created devices.
        It will be used in the device shutdown to remove all generated
        devices if the device will be shutdown.

        The `namespace` parameter in `devparams` controls the visibility in of
        the auto device. If `namespace` is 'device' the device will be
        accessible by the syntax 'device.autodevname', in case of 'global' by
        'autodevname'.
        """
        if self.autodevices is None:
            self.autodevices = []

        fullname = autodevname
        if devparams.pop('namespace', 'device') != 'global':
            fullname = self.name + '.' + autodevname
        self.__dict__[autodevname] = cls(fullname, **devparams)
        self.autodevices.append(autodevname)

    def doShutdown(self):
        for name in self.autodevices or []:
            if name in self.__dict__:
                self.__dict__[name].shutdown()


class HasLimits(DeviceMixinBase):
    """
    This mixin can be inherited from device classes that are continuously
    moveable.  It automatically adds two parameters, absolute and user limits,
    and overrides :meth:`.isAllowed` to check if the given position is within
    the limits before moving.

    The `abslimits` parameter cannot be set after creation of the device and
    must be given in the setup configuration.

    The `userlimits` parameter gives the actual minimum and maximum values
    that the device can be moved to.  The user limits must lie within the
    absolute limits.

    **Important:** If the device is also an instance of `HasOffset`, it should
    be noted that the `abslimits` are in hardware units (disregarding the
    offset), while the `userlimits` are in logical units (taking the offset
    into account).

    The class also provides properties to read or set only one item of the
    limits tuple:

    .. attribute:: absmin
                   absmax

       Getter properties for the first/second value of `abslimits`.

    .. attribute:: usermin
                   usermax

       Getter and setter properties for the first/second value of `userlimits`.

    """

    parameters = {
        'userlimits': Param('User defined limits of device value', unit='main',
                            type=limits, settable=True, chatty=True,
                            category='limits', fmtstr='main'),
        'abslimits':  Param('Absolute limits of device value', unit='main',
                            type=limits, mandatory=True, fmtstr='main'),
    }

    @property
    def absmin(self):
        return self.abslimits[0]

    @property
    def absmax(self):
        return self.abslimits[1]

    def __getusermin(self):
        return self.userlimits[0]

    def __setusermin(self, value):
        self.userlimits = (value, self.userlimits[1])

    usermin = property(__getusermin, __setusermin)

    def __getusermax(self):
        return self.userlimits[1]

    def __setusermax(self, value):
        self.userlimits = (self.userlimits[0], value)

    usermax = property(__getusermax, __setusermax)

    del __getusermin, __setusermin, __getusermax, __setusermax

    def _checkLimits(self, limits):
        umin, umax = limits
        amin, amax = self.abslimits
        if isinstance(self, HasOffset):
            offset = getattr(self, '_new_offset', self.offset)
            umin += offset
            umax += offset
        else:
            offset = 0
        if umin > umax:
            raise ConfigurationError(
                self, 'user minimum (%s, offset %s) above the user '
                'maximum (%s, offset %s)' % (umin, offset, umax, offset))
        if umin < amin - abs(amin * 1e-12):
            raise ConfigurationError(
                self, 'user minimum (%s, offset %s) below the '
                'absolute minimum (%s)' % (umin, offset, amin))
        if umax > amax + abs(amax * 1e-12):
            raise ConfigurationError(
                self, 'user maximum (%s, offset %s) above the '
                'absolute maximum (%s)' % (umax, offset, amax))

    def doReadUserlimits(self):
        if 'userlimits' not in self._config:
            self.log.info('setting userlimits from abslimits, which are %s',
                          self.abslimits)
            return self.abslimits
        cfglimits = self._config['userlimits']
        self._checkLimits(cfglimits)
        return cfglimits

    def doWriteUserlimits(self, value):
        self._checkLimits(value)
        if isinstance(self, HasOffset) and hasattr(self, '_new_offset'):
            # when changing the offset, the userlimits are adjusted so that the
            # value stays within them, but only after the new offset is applied
            return
        curval = self.read(0)

        if self._check_in_range(curval, value)[0] == status.WARN:
            self.log.warning('current device value (%s) not within new '
                             'userlimits (%s, %s)',
                             self.format(curval, unit=True),
                             value[0], value[1])

    def _check_in_range(self, curval, userlimits):
        # take precision into account in case we drive exactly to the
        # user limit but the device overshoots a little
        precision = self.precision if isinstance(self, HasPrecision) else 0

        if curval + precision < userlimits[0]:
            return status.WARN, 'below user limit (%s)' % \
                                self.format(userlimits[0], unit=True)
        elif curval - precision > userlimits[1]:
            return status.WARN, 'above user limit (%s)' % \
                                self.format(userlimits[1], unit=True)

        return status.OK, ''

    def _adjustLimitsToOffset(self, value, diff):
        """Adjust the user limits to the given offset.

        Used by the HasOffset mixin class to adjust the offset. *value* is the
        offset value, *diff* the offset difference.
        """
        self._new_offset = value
        limits = self.userlimits
        self.userlimits = (limits[0] - diff, limits[1] - diff)
        del self._new_offset


class HasOffset(DeviceMixinBase):
    """Mixin class for Readable or Moveable devices that want to provide an
    'offset' parameter and that can be adjusted via adjust().

    This is *not* directly a feature of Moveable, because providing this
    transparently this would mean that `doRead()` returns the un-adjusted value
    while `read()` returns the adjusted value.  It would also mean that the
    un-adjusted value is stored in the cache, which is wrong for monitoring
    purposes.

    Instead, each class that provides an offset **must** inherit this mixin,
    and handle ``self.offset`` in `doRead()` and `doStart()`.

    The usual convention for the sign of the offset is that the device position
    is ``hardware_position - offset``, so ``self.offset`` has to be subtracted
    in `doRead()` and added in `doStart()`.

    If a different convention is used, `doAdjust()` must be overridden too.

    TODO: handle limit/offset coupling
    """
    parameters = {
        'offset': Param('Offset of device zero to hardware zero', unit='main',
                        settable=True, category='offsets', chatty=True,
                        fmtstr='main'),
    }

    def doWriteOffset(self, value):
        """Adapt the limits to the new offset."""
        old_offset = self.offset
        diff = value - old_offset
        if isinstance(self, HasLimits):
            self._adjustLimitsToOffset(value, diff)
        # For moveables, also adjust target to avoid getting value and
        # target out of sync
        if 'target' in self.parameters and self.target is not None:
            self._setROParam('target', self.target - diff)
        # Since offset changes directly change the device value, refresh
        # the cache instantly here
        if self._cache:
            self._cache.put(self, 'value', self.read(0) - diff,
                            currenttime(), self.maxage)
        session.elogEvent('offset', (str(self), old_offset, value))

    def doAdjust(self, oldvalue, newvalue):
        """Adapt the device offset so that 'oldvalue' is now called 'newvalue'.

        Used to implement the `adjust()` user command and related functions,
        since the offset can have different sign conventions depending on
        underlying systems.

        The base implementation assumes that ``dev_pos = hw_pos - offset``.
        """
        diff = oldvalue - newvalue
        self.offset += diff


class HasPrecision(DeviceMixinBase):
    """
    Mixin class for Readable and Moveable devices that want to provide a
    'precision' parameter.

    This is mainly useful for user info, and for high-level devices that have
    to work with limited-precision subordinate devices.

    The class also implements a default `doIsAtTarget` method, which checks
    the value is within the precision.
    """
    parameters = {
        'precision': Param('Precision of the device value (allowed deviation '
                           'of stable values from target)', unit='main',
                           fmtstr='main', type=floatrange(0),
                           settable=True, category='precisions'),
    }

    def doIsAtTarget(self, pos, target):
        if target is None:
            return True  # avoid bootstrapping problems
        return abs(target - pos) <= self.precision


class HasMapping(DeviceMixinBase):
    """
    Mixin class for devices that use a finite mapping between user supplied
    input and internal representation.

    This is mainly useful for devices which can only yield certain values or go
    to positions from a predefined set, like switching devices.

    Abstract classes that use this mixin are implemented in
    `nicos.devices.abstract.MappedReadable` and `.MappedMoveable`.
    """
    parameters = {
        'mapping':  Param('Mapping of device values to raw (internal) values',
                          unit='', settable=False, mandatory=True,
                          type=dictof(str, anytype)),
        'fallback': Param('Readback value if the raw device value is not in '
                          'the mapping or None to disable', default=None,
                          unit='', type=anytype, settable=False),
    }

    # mapped values usually are string constants and have no unit
    parameter_overrides = {
        'unit': Override(mandatory=False),
    }

    def doIsAllowed(self, target):
        if target not in self.mapping:
            return False, 'unknown value: %r, must be one of %s' % \
                (target, ', '.join(map(repr, sorted(self.mapping))))
        return True, ''


class HasTimeout(DeviceMixinBase):
    """
    Mixin class for devices whose wait() should have a simple timeout.

    Classes using this mixin may provide a `timeoutAction` which gets
    called once as soon as the device times out (and a status is obtained).
    Any Exceptions occurring therein will not stop a script!

    The time at which the device will get a timeout (in case it is still in
    `status.BUSY` or has not reached its target value which corresponds to
    `isAtTarget` being False if implemented) is determined upon calling
    `start` and is saved to the non-userparameter `_timesout`.
    If you need a more dynamic timeout calculation, you may provide a
    `doReadTimeout` method (with volatile=True) to calculate the extra amount
    on the fly.

    The relevant timestamps are internally stored in the (non-userparam)
    `_timesout`, which is either set to None, if there is no nicos-initiated
    movement, or to an iterable of tuples describing what action is supposedly
    performed and at which time it should be finished.
    If there is a doTime method, it is used to calculate the length of an
    intermediary 'ramping' phase and timeout. This may be followed by other
    phases. If `timeout` is not None, a last phase is added which takes
    `timeout` seconds to time out.

    You may set the `timeout` parameter to None in which case the device will
    never time out.
    """
    parameters = {
        'timeout':   Param('Time limit for the device to reach its target'
                           ', or None', unit='s', fmtstr='%.1f',
                           type=none_or(floatrange(0)),
                           settable=True, mandatory=False, chatty=True),
        '_timesout': Param('Device movement should finish between these '
                           'timestamps',
                           type=none_or(nonemptylistof(tupleof(string, float))),
                           unit='s', userparam=False, settable=True),
    }

    # derived classes may redefine this if they need different behaviour
    timeout_status = status.NOTREACHED

    # internal flag to determine if the timeout action has been executed
    _timeoutActionCalled = False

    @property
    def _startTime(self):
        # only read the parameter once from the cache db to avoid race
        # condition between the checks below
        timesout = self._timesout
        return timesout[0][1] if timesout else None

    @property
    def _timeoutTime(self):
        # see above
        timesout = self._timesout
        return timesout[-1][1] if timesout else None

    def _getTimeoutTimes(self, current_pos, target_pos, current_time):
        """Calculates timestamps for timeouts

        returns an iterable of tuples (status_string, timestamp) with ascending
        timestamps.
        First timestamp has to be `current_time` which is the only argument to
        this.
        The last timestamp will be used as the final timestamp to determine if
        the device's movement timed out or not.
        Additional timestamps (in between) may be set if need for
        _combinedStatus returning individual status text's (e.g. to
        differentiate between 'ramping' and 'stabilization').
        """
        res = [('start', current_time)]
        if hasattr(self, 'doTime'):
            res.append(('', res[-1][1] + self.doTime(current_pos, target_pos)))
        if self.timeout:
            res.append(('', res[-1][1] + self.timeout))
        return res

    def isTimedOut(self):
        """Method to (only) check whether a device's movement timed out or not.

        Returns False unless there was a timeout in which case it returns True.
        """
        if self.timeout is None:
            return False
        timeoutTime = self._timeoutTime
        if timeoutTime is not None:
            remaining = timeoutTime - monotonic()
            if remaining > 0:
                self.log.debug('%.2f s left before timeout', remaining)
            else:
                self.log.debug('timeout since %.2f s', -remaining)
            return remaining < 0
        return False

    def resetTimeout(self, target):
        """Method called to reset the timeout when the device is started to
        a new target.
        """
        self._timeoutActionCalled = False
        timesout = self._getTimeoutTimes(self.read(), target, monotonic())
        self._setROParam('_timesout', timesout)

    def _clearTimeout(self):
        self._setROParam('_timesout', None)

    def _targetReached(self):
        """Clears timeout in order to suppress further timeouts after the
        device has reached its target. This is determined by `_combinedStatus`.
        Thus this will just be checked when the status is polled periodically
        before the device timed out.
        This behaviour may be changed in derived classes,
        e.g. `HasWindowTimeout`.
        """
        self._clearTimeout()

    def _combinedStatus(self, maxage=0):
        """Create a combined status from doStatus, isAtTarget and timedOut

        If a timeout happens, use the status set by self.timeout_status and
        call `timeoutAction` once if defined. Pollers and other `SLAVE`s do
        *not* call `timeoutAction`.
        """
        from nicos.core.device import Readable  # isort:skip
        code, msg = Readable._combinedStatus(self, maxage)

        if code in (status.OK, status.WARN) and self._timeoutTime:
            if not self.isAtTarget(self.read(maxage)):
                code = status.BUSY
                msg = statusString('target not yet reached', msg)
            else:
                self._targetReached()
        if code == status.BUSY:
            if self.isTimedOut():
                code = self.timeout_status
                msg = statusString('movement timed out', msg)
                # only call once per timeout, flag is reset in Device.start()
                if not self._timeoutActionCalled and \
                        session.mode in (MASTER, MAINTENANCE):
                    try:
                        if hasattr(self, 'timeoutAction'):
                            self.timeoutAction()
                            self._timeoutActionCalled = True
                            return self._combinedStatus(maxage)
                    except Exception:
                        self.log.exception('error calling timeout action',
                                           exc=True)
                    finally:
                        self._timeoutActionCalled = True
            elif self._timesout:
                # give indication about the phase of the movement
                for m, t in self._timesout or []:
                    if t > monotonic():
                        msg = statusString(m, msg)
                        break
        elif code == status.ERROR:
            self._timeoutActionCalled = True

        return (code, msg)


class HasWindowTimeout(HasPrecision, HasTimeout):
    """
    Mixin class for devices needing a more fancy timeout handling than
    `HasTimeout`.

    Basically we keep a (length limited) history of past values and check if
    they are close enough to the target (deviation is smaller than
    `precision`). The length of that history is determined by
    :attr:`~HasWindowTimeout.window`.
    In any case the last read value is used to determine `isAtTarget`.
    If the value is outside the defined window for longer than
    :attr:`~HasTimeout.timeout` seconds after the HW is no longer busy.
    Also we add a stabilising phase in the timeouttimes list.
    """
    parameters = {
        'window': Param('Time window for checking stabilization',
                        unit='s', default=60.0, fmtstr='%.1f', settable=True,
                        category='general'),
    }

    parameter_overrides = {
        'precision': Override(mandatory=True, type=floatrange(1e-8)),
    }

    @lazy_property
    def _history(self):
        if self._cache:
            self._cache.addCallback(self, 'value', self._cacheCB)
            self._subscriptions.append(('value', self._cacheCB))
            t = currenttime()
            return self._cache.history(self, 'value', t - self.window, t)
        return []

    # use values determined by poller or waitForCompletion loop
    # to fill our history
    def _cacheCB(self, key, value, time):
        self._history.append((time, value))
        # clean out stale values, if more than one
        stale = None
        for i, entry in enumerate(self._history):
            t, _ = entry
            if t >= time - self.window:
                stale = i
                break
        else:
            return
        # remove oldest entries, but keep one stale
        if stale > 1:
            del self._history[:stale - 1]

    def _getTimeoutTimes(self, current_pos, target_pos, current_time):
        """Calculates timestamps for timeouts

        returns an iterable of tuples (status_string, timestamp) with ascending
        timestamps.
        First timestamp has to be `current_time` which is the only argument to
        this.
        The last timestamp will be used as the final timestamp to determine if
        the device's movement timed out or not.
        Additional timestamps (in between) may be set if need for
        _combinedStatus returning individual status text's (e.g. to
        differentiate between 'ramping' and 'stabilization').
        """
        res = HasTimeout._getTimeoutTimes(self, current_pos, target_pos,
                                          current_time)
        if not res:
            return None
        # we just append the window time after the timeout time
        # logically wrong order, but nobody uses the strings anyway
        res.append(('', res[-1][1] + self.window))
        return res

    def isAtTarget(self, pos=None, target=None):
        if target is None:
            target = self.target
        if pos is None:
            pos = self.read(0)

        ct = currenttime()
        self._cacheCB('value', pos, ct)
        if target is None:
            return True

        # check subset of _history which is in window
        # also check if there is at least one value before window
        # to know we have enough datapoints
        hist = self._history[:]
        window_start = ct - self.window
        hist_in_window = [v for (t, v) in hist if t >= window_start]
        stable = all(abs(v - target) <= self.precision
                     for v in hist_in_window)
        if 0 < len(hist_in_window) < len(hist) and stable:
            if hasattr(self, 'doIsAtTarget'):
                return self.doIsAtTarget(pos, target)
            return True
        return False

    def doTime(self, old_value, target):
        if old_value is None or target is None or old_value == target:
            return 0.
        if 'speed' in self.parameters and self.speed != 0:
            return abs(target - old_value) / self.speed + self.window
        elif 'ramp' in self.parameters and self.ramp != 0:
            return abs(target - old_value) / (self.ramp / 60.) + self.window
        return self.window

    def doEstimateTime(self, elapsed):
        if self.status()[0] != status.BUSY:
            return None
        if self.target is None:
            return None
        if 'setpoint' not in self.parameters or self.setpoint == self.target:
            # ramp finished, look at history to estimate from last point
            # outside
            now = currenttime()
            for t, v in reversed(list(self._history)):
                if abs(v - self.target) > self.precision:
                    return max(0, t + self.window - now + 1)
                if t < now - self.window:
                    break
            return 0.0
        # ramp unfinished, estimate ramp + window
        return self.doTime(self.read(), self.target)

    def _targetReached(self):
        """Do not call `_clearTimeout` as supposed by `HasTimeout` in order
        to check whether the value has drifted away from its window
        also after the target has been reached.
        """


class HasCommunication(DeviceMixinBase):
    """
    Mixin class for devices that communicate with external devices or
    device servers.

    Provides parameters to set communication tries and delays, and basic
    services to map external exceptions to NICOS exception classes.
    """

    parameters = {
        'comtries': Param('Maximum retries for communication',
                          type=intrange(1, 100), default=3, settable=True),
        'comdelay': Param('Delay between retries', unit='s', default=0.1,
                          fmtstr='%.1f', settable=True),
    }

    @lazy_property
    def _com_lock(self):
        return threading.Lock()

    def _com_retry(self, info, function, *args, **kwds):
        """Try communicating with the hardware/device.

        Parameter "info" is passed to _com_return and _com_raise methods that
        process the return value or exception raised after maximum tries.
        """
        tries = self.comtries
        with self._com_lock:
            while True:
                tries -= 1
                try:
                    result = function(*args, **kwds)
                    return self._com_return(result, info)
                except Exception as err:
                    if tries == 0:
                        self._com_raise(err, info)
                    else:
                        name = getattr(function, '__name__', 'communication')
                        self._com_warn(tries, name, err, info)
                    session.delay(self.comdelay)

    def _com_return(self, result, info):
        """Process *result*, the return value of communication.

        Can raise an exception to initiate a retry.  Default is to return
        result unchanged.
        """
        return result

    def _com_warn(self, retries, name, err, info):
        """Gives the opportunity to warn the user on failed tries.

        Can also call _com_raise to abort early.
        """
        if retries == self.comtries - 1:
            self.log.warning('%s failed, retrying up to %d times',
                             name, retries, exc=1)

    def _com_raise(self, err, info):
        """Process the exception raised either by communication or _com_return.

        Should raise a NICOS exception.  Default is to raise
        CommunicationError.
        """
        raise CommunicationError(self, str(err))


class CanDisable(DeviceMixinBase):
    """Mixin class for devices that can be disabled and enabled."""

    def _enable(self, on):
        """
        .. method:: doEnable(on)

           This method must be present and is called to execute the action
           with a True argument for `enable`, and False for `disable`.
        """
        what = 'enable' if on else 'disable'
        if self._mode == SLAVE:
            raise ModeError(self, '%s not possible in slave mode' % what)
        if getattr(self, 'requires', None):
            try:
                session.checkAccess(self.requires)
            except AccessError as err:
                raise AccessError(
                    self, 'cannot %s device: %s' % (what, err)) from None
        if self._sim_intercept:
            return
        self.doEnable(on)
        self.poll()

    @usermethod(doc="""Enable this device.""")
    def enable(self):
        """Enable this device.

        This operation is forbidden in slave mode.
        """
        self._enable(True)

    @usermethod(doc="""Disable this device.""")
    def disable(self):
        """Disable this device.

        This operation is forbidden in slave mode."""
        self._enable(False)

    def doEnable(self, on):
        """Execute the action to enable/disable.

        This method must be present and is called to execute the action with a
        `True` argument for `enable`, and `False` for `disable`.
        """
        raise NotImplementedError("Please implement the 'doEnable' method")


class IsController(DeviceMixinBase):
    """Mixin class for complex Controllers.

    This mixin should be used for cases where limits are strongly
    state-dependent.

    Subclasses need to implement :meth:`isAdevTargetAllowed` function.
    """

    def isAdevTargetAllowed(self, adev, adevtarget):
        """Check if target of an attached device is valid

        *adev* The attached device instance requesting the check.
        *adevtarget* The target value of the attached device to check for.

        returns a tuple(bool status, string reason)
        """
        raise NotImplementedError('Please implement the isAdevTargetAllowed'
                                  ' method')
