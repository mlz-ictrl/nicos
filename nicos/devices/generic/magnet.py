#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
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

"""
Class for magnets powered by unipolar power supplies.
"""

import math

from nicos import session
from nicos.utils import clamp
from nicos.utils.fitting import Fit
from nicos.core import Moveable, HasLimits, status, ConfigurationError, \
    LimitError, usermethod, NicosError, Attach
from nicos.core.params import Param, Override, tupleof
from nicos.core.utils import multiStop
from nicos.devices.generic.sequence import SeqDev, BaseSequencer


class CalibratedMagnet(HasLimits, Moveable):
    """
    Base clase for magnet supplies having an bipolar current source.

    Use this for magnets which can be calibrated, i.e. where:
        B(I) = Ic0 + c1*erf(c2*I) + c3*atan(c4*I)
    works reasonably well.
    Coefficients c0..c4 are given as 'calibration' parameter.
    """

    attached_devices = {
        'currentsource': Attach('bipolar Powersupply', Moveable),
    }

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

    parameter_overrides = {
        'unit': Override(mandatory=False, default='T'),
        'abslimits': Override(mandatory=False, volatile=True),
    }

    def _current2field(self, current, *coefficients):
        """Return field in T for given current in A.

        Should be monotonic and asymetric or _field2current will fail!

        Note: This may be overridden in derived classes.
        """
        v = coefficients or self.calibration
        if len(v) != 5:
            self.log.warning('Wrong number of coefficients in calibration '
                             'data!  Need exactly 5 coefficients!')
        return current * v[0] + v[1] * math.erf(v[2] * current) + \
            v[3] * math.atan(v[4] * current)

    def _field2current(self, field):
        """Return required current in A for requested field in T.

        Default implementation does a binary search using _current2field,
        which must be monotonic for this to work!

        Note: This may be overridden in derived classes.
        """
        # binary search/bisection
        maxcurr = self._attached_currentsource.abslimits[1]
        mincurr = -maxcurr
        maxfield = self._current2field(maxcurr)
        minfield = -maxfield
        if not minfield <= field <= maxfield:
            raise LimitError(self,
                             'requested field %g %s out of range %g..%g %s' %
                             (field, self.unit, minfield, maxfield, self.unit))
        while minfield <= field <= maxfield:
            # binary search
            trycurr = 0.5 * (mincurr + maxcurr)
            tryfield = self._current2field(trycurr)
            if field == tryfield:
                self.log.debug('current for %g T is %g A' % (field, trycurr))
                return trycurr  # Gotcha!
            elif field > tryfield:
                # retry upper interval
                mincurr = trycurr
                minfield = tryfield
            else:
                # retry lower interval
                maxcurr = trycurr
                maxfield = tryfield
            # if interval is so small, that any error within is acceptable:
            if maxfield - minfield < 1e-4:
                ratio = (field - minfield) / (maxfield - minfield)
                trycurr = (maxcurr - mincurr) * ratio + mincurr
                self.log.debug('current for %g T is %g A' % (field, trycurr))
                return trycurr
        raise ConfigurationError(self,
                                 '_current2field polynome not monotonic!')

    def doRead(self, maxage=0):
        return self._current2field(self._attached_currentsource.read(maxage))

    def doStart(self, target):
        self._attached_currentsource.start(self._field2current(target))

    def doStop(self):
        self._attached_currentsource.stop()

    def doReset(self):
        return self._attached_currentsource.reset()

    def doReadRamp(self):
        # This is an approximation!
        return self.calibration[0]*abs(self._attached_currentsource.ramp)

    def doWriteRamp(self, newramp):
        # This is an approximation!
        self._attached_currentsource.ramp = newramp / self.calibration[0]

    def doReadAbslimits(self):
        minfield, maxfield = [self._current2field(I)
                              for I in self._attached_currentsource.abslimits]
        # include 0 in allowed range
        if minfield > 0:
            minfield = 0
        if maxfield < 0:
            maxfield = 0
        # get configured limits if any, or take max from source
        limits = self._config.get('abslimits', (minfield, maxfield))
        # in any way, clamp limits to what the source can handle
        limits = [clamp(i, minfield, maxfield) for i in limits]
        return min(limits), max(limits)

    def doWriteUserlimits(self, limits):
        HasLimits.doWriteUserlimits(self, limits)
        # all Ok, set source to max of pos/neg field current
        maxcurr = max(self._field2current(i) for i in limits)
        mincurr = min(self._field2current(i) for i in limits)
        self._attached_currentsource.userlimits = (mincurr, maxcurr)

    def doTime(self, startval, target):
        # get difference in current
        delta = abs(self._field2current(target) -
                    self._field2current(startval))
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
        scans = session.data._last_scans
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
                self.log.info('%s is not a calibration scan' % scan.counter)
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
    Base clase for magnet supplies having an unipolar current source
    and a switching box for reversing the current (or not).

    Details of the switching need to be implemented in subclasses.
    This class contains the sequencing logic needed to reverse the field.
    Also a non-linear relationship between field and current
    is possible (see ``CalibratedMagnet``).
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

    # pylint: disable=W0221
    def _generateSequence(self, value):
        sequence = []
        currentsource = self._attached_currentsource
        if value != 0:
            need_pol = +1 if value > 0 else -1
            curr_pol = self._get_field_polarity()
            # if the switch values are not correct, drive to zero and switch
            if curr_pol != need_pol:
                if currentsource.read() != 0:
                    sequence.append(SeqDev(currentsource, 0.))
                # insert switching Sequence
                self._seq_set_field_polarity(need_pol, sequence)
        sequence.append(SeqDev(currentsource, abs(value)))
        if value == 0:
            self._seq_set_field_polarity(0, sequence)
        return sequence

    def doRead(self, maxage=0):
        absfield = self._current2field(
            self._attached_currentsource.read(maxage))
        return self._get_field_polarity() * absfield

    def doStart(self, target):
        BaseSequencer.doStart(self, self._field2current(target))

    def doStop(self):
        BaseSequencer.doStop(self)
        if self.status()[0] == status.BUSY:
            multiStop(self._adevs)

    def doReset(self):
        BaseSequencer.doReset(self)
        return self._attached_currentsource.reset()

    def doReadAbslimits(self):
        maxcurr = self._attached_currentsource.abslimits[1]
        maxfield = self._current2field(maxcurr)
        # get configured limits if any, or take max of source
        limits = self._config.get('abslimits', (-maxfield, maxfield))
        # in any way, clamp limits to what the source can handle
        limits = [clamp(i, -maxfield, maxfield) for i in limits]
        return min(limits), max(limits)

    def doWriteUserlimits(self, limits):
        HasLimits.doWriteUserlimits(self, limits)
        currentsource = self._attached_currentsource
        # all Ok, set source to max of pos/neg field current
        maxcurr = max(abs(self._field2current(i)) for i in limits)
        currentsource.userlimits = (0, maxcurr)
