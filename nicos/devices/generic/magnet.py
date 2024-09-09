# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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

"""
Class for magnets powered by unipolar power supplies.
"""

import math
import time
from contextlib import suppress

import numpy
from scipy.optimize import fsolve

from nicos import session
from nicos.core import Attach, HasLimits, LimitError, NicosError, Readable, \
    status, usermethod
from nicos.core.params import Param, oneof, tupleof
from nicos.core.sessions.utils import MASTER
from nicos.core.utils import multiStop
from nicos.devices.abstract import Magnet
from nicos.devices.generic.sequence import BaseSequencer, SeqDev
from nicos.utils import clamp, createThread
from nicos.utils.fitting import Fit
from nicos.utils.functioncurves import Curve2D, Curves, ufloat


class CalibratedMagnet(Magnet):
    """Base class for magnet supplies having a bipolar current source.

    Use this for magnets which can be calibrated, i.e. where::

        B(I) = Ic0 + c1*erf(c2*I) + c3*atan(c4*I)

    works reasonably well.
    Coefficients c0..c4 are given as 'calibration' parameter.
    """

    parameters = {
        'ramp': Param('Target rate of field change per minute',
                      unit='main/min', mandatory=False, settable=True,
                      volatile=True),
        'calibration': Param('Coefficients for calibration '
                             'function: [c0, c1, c2, c3, c4] calculates '
                             'B(I) = c0*I + c1*erf(c2*I) + c3*atan(c4*I)'
                             ' in T',
                             type=tupleof(float, float, float, float, float),
                             default=(1.0, 0.0, 0.0, 0.0, 0.0), settable=True,
                             chatty=True),
    }

    def _mapReadValue(self, value):
        return self._current2field(value)

    def _current2field(self, current, *coefficients):
        """Return field (B) in T for given current (I) in A.

        B(I) = c0 * I + c1 * erf(c2 * I) + c3 * atan(c4 * I)
        """
        v = coefficients or self.calibration
        if len(v) != 5:
            self.log.warning('Wrong number of coefficients in calibration '
                             'data!  Need exactly 5 coefficients!')
        return v[0]*current + v[1]*math.erf(v[2]*current) + \
            v[3]*math.atan(v[4]*current)

    def _mapTargetValue(self, target):
        maxcurr = self._attached_currentsource.abslimits[1]
        mincurr = -maxcurr
        maxfield = self._mapReadValue(maxcurr)
        minfield = self._mapReadValue(mincurr)
        if not minfield <= target <= maxfield:
            raise LimitError(self,
                             'requested field %g %s out of range %g..%g %s' %
                             (target, self.unit, minfield, maxfield, self.unit)
                             )

        res = fsolve(lambda cur: self._mapReadValue(cur) - target, 0)[0]
        self.log.debug('current for %g %s is %g', target, self.unit, res)
        return res

    def doStop(self):
        self._attached_currentsource.stop()

    def doReset(self):
        return self._attached_currentsource.reset()

    def doReadRamp(self):
        # This is an approximation!
        return self.calibration[0] * abs(self._attached_currentsource.ramp)

    def doWriteRamp(self, newramp):
        # This is an approximation!
        self._attached_currentsource.ramp = newramp / self.calibration[0]

    def doReadAbslimits(self):
        minfield, maxfield = Magnet.doReadAbslimits(self)
        # include 0 in allowed range
        minfield = min(minfield, 0)
        maxfield = max(maxfield, 0)
        # get configured limits if any, or take max from source
        limits = self._config.get('abslimits', (minfield, maxfield))
        # in any way, clamp limits to what the source can handle
        limits = [clamp(i, minfield, maxfield) for i in limits]
        return min(limits), max(limits)

    def doWriteUserlimits(self, value):
        HasLimits.doWriteUserlimits(self, value)
        # all Ok, set source to max of pos/neg field current
        maxcurr = max(self._mapTargetValue(v) for v in value)
        mincurr = min(self._mapTargetValue(v) for v in value)
        self._attached_currentsource.userlimits = (mincurr, maxcurr)

    def doTime(self, old_value, target):
        # get difference in current
        delta = abs(self._mapTargetValue(target) -
                    self._mapTargetValue(old_value))
        # ramp is per minute, doTime should return seconds
        return 60 * delta / self._attached_currentsource.ramp

    @usermethod
    def calibrate(self, fieldcolumn, *scannumbers):
        """Calibrate the B to I conversion, argument is one or more scan numbers.

        The first argument specifies the name of the device which should
        be used as a measuring device for the field.

        Example:

        >>> B_mira.calibrate(Bf, 351)
        """
        scans = session.experiment.data.getLastScans()
        self.log.info('determining calibration from scans, please wait...')
        Is = []
        Bs = []
        currentcolumn = self._attached_currentsource.name
        # XXX(dataapi): adapt to new Dataset class
        for scan in scans:
            if scan.counter not in scannumbers:
                continue
            if fieldcolumn not in scan.ynames or \
               currentcolumn not in scan.xnames:
                self.log.info('%s is not a calibration scan', scan.counter)
                continue
            xindex = scan.xnames.index(currentcolumn)
            yindex = scan.ynames.index(fieldcolumn)
            yunit = scan.yunits[yindex]
            if yunit == 'T':
                factor = 1.0
            elif yunit == 'mT':
                factor = 1e-3
            elif yunit == 'uT':
                factor = 1e-6
            elif yunit == 'G':
                factor = 1e-4
            elif yunit == 'kG':
                factor = 1e-1
            else:
                raise NicosError(self, 'unknown unit for B field '
                                 'readout: %r' % yunit)
            for xr, yr in zip(scan.xresults, scan.yresults):
                Is.append(xr[xindex])
                Bs.append(yr[yindex] * factor)
        if not Is:
            self.log.error('no calibration data found')
            return
        fit = Fit('calibration', self._current2field,
                  ['c%d' % i for i in range(len(self.calibration))],
                  [1] * len(self.calibration))
        res = fit.run(Is, Bs, [1] * len(Bs))
        if res._failed:
            self.log.warning('fit failed')
            return
        self.calibration = res._pars[1]


class BipolarSwitchingMagnet(BaseSequencer, CalibratedMagnet):
    """
    Base class for magnet supplies having a unipolar current source
    and a switching box for reversing the current (or not).

    Details of the switching need to be implemented in subclasses.
    This class contains the sequencing logic needed to reverse the field.
    Also, a non-linear relationship between field and current
    is possible (see :class:`.CalibratedMagnet`).
    """

    def _get_field_polarity(self):
        """Returns sign of field polarity (+1 or -1)

        and may return 0 for zero field.

        Note: need to be (re-)defined in derived classes.
        """
        return 0

    def _seq_set_field_polarity(self, polarity, sequence):
        """Appends the needed Actions to set the requested polarity

        to the given sequence. Must be able to handle polarities of +1, 0, -1
        and switch to that polarity correctly. If sensible, this may also do
        nothing.

        Note: need to be defined in derived classes.
        """
        raise NotImplementedError('please use a proper derived class and '
                                  'implement this there!')

    def _generateSequence(self, target):
        sequence = []
        currentsource = self._attached_currentsource
        if target != 0:
            need_pol = +1 if target > 0 else -1
            curr_pol = self._get_field_polarity()
            # if the switch values are not correct, drive to zero and switch
            if curr_pol != need_pol:
                if currentsource.read() != 0:
                    sequence.append(SeqDev(currentsource, 0.))
                # insert switching Sequence
                self._seq_set_field_polarity(need_pol, sequence)
        sequence.append(SeqDev(currentsource, abs(target)))
        if target == 0:
            self._seq_set_field_polarity(0, sequence)
        return sequence

    def _mapReadValue(self, value):
        absfield = CalibratedMagnet._mapReadValue(self, value)
        return self._get_field_polarity() * absfield

    def doStart(self, target):
        BaseSequencer.doStart(self, self._mapTargetValue(target))

    def doStop(self):
        BaseSequencer.doStop(self)
        if self.status()[0] == status.BUSY:
            multiStop(self._adevs)

    def doReset(self):
        BaseSequencer.doReset(self)
        return self._attached_currentsource.reset()

    def doReadAbslimits(self):
        maxcurr = self._attached_currentsource.abslimits[1]
        maxfield = self._mapReadValue(maxcurr)
        # get configured limits if any, or take max of source
        limits = self._config.get('abslimits', (-maxfield, maxfield))
        # in any way, clamp limits to what the source can handle
        limits = [clamp(i, -maxfield, maxfield) for i in limits]
        return min(limits), max(limits)

    def doWriteUserlimits(self, value):
        HasLimits.doWriteUserlimits(self, value)
        currentsource = self._attached_currentsource
        # all Ok, set source to max of pos/neg field current
        maxcurr = max(abs(self._mapTargetValue(i)) for i in value)
        currentsource.userlimits = (0, maxcurr)


class MagnetWithCalibrationCurves(Magnet):
    """Base class for a magnet, which relies on current-to-field curves
    obtained experimentally for different power supply ramps through a
    calibration procedure. Calibration curves are stored in a cached parameter.
    Requires an external magnetic field sensing nicos device attached as
    `magsensor`.
    """

    attached_devices = {
        'magsensor': Attach('Sensor of magnetic field', Readable),
    }

    parameters = {
        'calibration': Param(
            'Magnetic field fitting curves',
            type=dict, settable=True, default={'stepwise': {}, 'continuous': {}}
        ),
        'fielddirection': Param(
            'Direction in which magnetic field should change',
            type=oneof('increasing', 'decreasing'), settable=True
        ),
        'mode': Param(
            'Measurement mode: stepwise or continuous',
            type=oneof('stepwise', 'continuous'), default='stepwise',
            settable=True
        ),
        'ramp': Param(
            'Ramp of the currentsource',
            unit='A/min', type=float, settable=True
        ),
        'maxramp': Param(
            'Maximal ramp value',
            unit='A/min', type=float, mandatory=True
        ),
    }

    def _check_calibration(self, mode, ramp):
        if not self.calibration:
            raise NicosError(self, 'Magnet must be calibrated.')
        if mode not in self.calibration.keys():
            raise NicosError(self, 'Magnet not calibrated in %s mode.' % mode)
        if str(float(ramp)) not in self.calibration[mode].keys():
            raise NicosError(self, 'Magnet not calibrated for %s A/min '
                                   'currensource ramp.' % ramp)
        if len(self.calibration[mode][str(float(ramp))]) != 2:
            raise NicosError(self, 'Error reading calibration in %s mode for %s'
                                   ' A/min ramp. Performing new calibration '
                                   'might help.' % (mode, ramp))

    def _current2field(self, current):
        """Returns field in T for given current in A.
        """
        self._check_calibration(self.mode, self.ramp)
        curves = self.calibration[self.mode][str(float(self.ramp))]
        return curves.increasing()[0].yvx(current).y \
            if self.fielddirection == 'increasing' \
            else curves.decreasing()[0].yvx(current).y

    def _field2current(self, field):
        """Returns required current in A for requested field in T.
        """
        self._check_calibration(self.mode, self.ramp)
        curves = self.calibration[self.mode][str(float(self.ramp))]
        return curves.increasing()[0].xvy(field).x \
            if self.fielddirection == 'increasing' \
            else curves.decreasing()[0].xvy(field).x

    def doInit(self, mode):
        if mode == MASTER:
            self._cycling, self._measuring = False, False
            self._cycling_thread = None
            self._Ivt, self._Bvt, self._cycling_steps = Curve2D(), Curve2D(), []
            self._calibration_updated = False
            self._progress, self._maxprogress = 0, 0
            self._stop_requested = False

    def doRead(self, maxage=0):
        return self._attached_magsensor.doRead(maxage)

    def doStart(self, target):
        current = self._field2current(target).n
        self._attached_currentsource.doStart(current)

    def doStop(self):
        if self._cycling:
            self._stop_requested = True
        session.delay(1)
        self.ramp = self.maxramp
        self._attached_currentsource.ramp = self.maxramp
        self._attached_currentsource.doStop()

    def doStatus(self, maxage=0):
        cs = self._attached_currentsource.doStatus(maxage)
        ms = self._attached_magsensor.doStatus(maxage)
        return max(cs, ms)

    def doReset(self):
        cs = self._attached_currentsource.reset()
        ms = self._attached_magsensor.reset()
        return max(cs, ms)

    def doReadAbslimits(self):
        limits = [0, 0]
        with suppress(Exception):
            self._check_calibration(self.mode, self.ramp)
            limits = [self._current2field(I).n
                      for I in self._attached_currentsource.abslimits]
        return min(limits), max(limits)

    def doReadRamp(self):
        return self._attached_currentsource.ramp

    def doWriteRamp(self, value):
        if value > self.maxramp:
            raise NicosError(self, 'Currentsource ramp should not exceed %s'
                             % self.maxramp)
        self._attached_currentsource.ramp = value

    def cycle_currentsource(self, val1, val2, ramp, n):
        """Cycles current source from val1 [A] to val2 [A] n times at a given
        ramp in [A/min].
        """
        self._measuring = True
        self._Ivt, self._cycling_steps = Curve2D(), []
        temp = self.ramp
        self.ramp = 0
        # at least 100 measurement points if time between measurements is >0.5s
        # or as many as possible but the time between measurements is 0.5s
        num = 100
        dt = abs(val2 - val1) / num / (ramp / 60)
        if dt < 0.5:
            dt = 0.5
            num = int(abs(val2 - val1) / (dt * ramp / 60))
        ranges = [(val1, val2, num, False), (val2, val1, num, False)]
        self._progress = 0
        self._maxprogress = sum(len(numpy.linspace(*r)) for r in ranges) * n
        for r in ranges * n:
            self._cycling_steps.append(len(numpy.linspace(*r)))
            for i in numpy.linspace(*r):
                self._progress += 1
                self._attached_currentsource.doStart(i)
                self._Ivt.append((time.time(), i))
                session.delay(dt)
                if self._stop_requested:
                    break
            if self._stop_requested:
                break
        self._measuring = False

        if not self._stop_requested:
            self.doStop()
        self.ramp = temp
        self._cycling = False

    @usermethod
    def calibrate(self, mode, ramp, n):
        """Measures B(I) calibration curves.
        Calibration curves are stored in self.calibration as a dict:
        self.calibration = {'continuous': _ramps_, 'stepwise': _ramps_}
        Ramps are ramps of the currentsource and are also dicts:
        _ramps_ = {'200.0': _curves_, '400.0': _curves_}
        Curves must be a set of two curves:
        _curves_ = (_increasing_curve_, _decreasing_curve_)
        Increasing and decreasing curves must be lists of (X, Y(X)) tuples:
        _increasing_curve_ = [(0, 1), (1, 2), (2, 4),]
        X and Y values can be also uncertainties.core.ufloat.
        """
        self._stop_requested = False
        absmin = self._attached_currentsource.absmin
        absmax = self._attached_currentsource.absmax
        self.mode = mode
        self.ramp = float(ramp)
        self._attached_currentsource.doStart(self._attached_currentsource.absmin)
        self._hw_wait()

        with_std = hasattr(self._attached_magsensor, 'readStd')
        if mode == 'continuous':
            if self._cycling_thread is None:
                self._cycling = True
                self._cycling_thread = createThread('',
                                                    self.cycle_currentsource,
                                                    (absmin, absmax, float(ramp), n,))
            else:
                raise NicosError(self, 'Power supply is busy.')
            self._Bvt = Curve2D()
            while self._cycling and not self._stop_requested:
                try:
                    B = self._attached_magsensor.doRead()
                except Exception:
                    B = None
                if B:
                    self._Bvt.append((time.time(), B if not with_std else
                                      ufloat(B, self._attached_magsensor.readStd(B))))
                session.delay(0.5)
            self._cycling_thread.join()
            self._cycling_thread = None
            self._BvI = Curve2D.from_two_temporal(self._Ivt, self._Bvt)
        elif mode == 'stepwise':
            num = 100
            ranges = [(absmin, absmax, num, False), (absmax, absmin, num, False)]
            self._BvI, self._cycling_steps = Curve2D(), []
            for r in ranges * n:
                self._cycling_steps.append(len(numpy.linspace(*r)))
                for i in numpy.linspace(*r):
                    self._attached_currentsource.doStart(i)
                    # hardcoded 10 secs to reach quasi steady state condition
                    session.delay(10)
                    B = None
                    while B is None:
                        with suppress(Exception):
                            B = self._attached_magsensor.doRead()
                    self._BvI.append((i, B if not with_std else
                                      ufloat(B, self._attached_magsensor.readStd(B))))
                    if self._stop_requested:
                        break
                if self._stop_requested:
                    break
        if not self._stop_requested:
            self.doStop()

        curves = Curves.from_series(self._BvI, self._cycling_steps)
        calibration = Curves([curves.increasing().mean(), curves.decreasing().mean()])
        temp = self.calibration.copy()
        temp[mode][str(float(ramp))] = calibration
        self.calibration = temp
        self._calibration_updated = True
        self._stop_requested = False
