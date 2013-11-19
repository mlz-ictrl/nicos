#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Class for MIRA magnet consisting of the ESS-Lambda power supply and polarity
switches attached to digital IOs of a Phytron motor controller.
"""

import threading
from time import sleep

from PowerSupply import CurrentControl

from nicos import session
from nicos.core import Moveable, HasLimits, Param, Override, waitForStatus, \
     floatrange, listof, InvalidValueError, usermethod, status, NicosError
from nicos.devices.taco.core import TacoDevice
from nicos.devices.taco.io import DigitalOutput
from nicos.utils.fitting import Fit
from nicos.core import SIMULATION


class LambdaController(HasLimits, TacoDevice, Moveable):

    taco_class = CurrentControl

    attached_devices = {
        'plusswitch':  (DigitalOutput, 'Switch to set for positive polarity'),
        'minusswitch': (DigitalOutput, 'Switch to set for negative polarity'),
    }

    parameters = {
        'ramp':  Param('Rate of ramping', type=floatrange(1, 240), default=60,
                       unit='main/min', settable=True),
    }

    def doInit(self, mode):
        if mode != SIMULATION:
            self._dev.setRamp(0)
        self._thread = None
        self._stopflag = 0
        self._errorflag = None

    def _move_to(self, value):
        self._stopflag = 0
        try:
            if value != 0:
                minus, plus = self._adevs['minusswitch'], self._adevs['plusswitch']
                # select which switch must be on and which off
                switch = value < 0 and minus or plus
                other  = value < 0 and plus or minus
                # if the switch values are not correct, drive to zero and switch
                if switch.read() & 1 != 1:
                    self._move_to(0)
                    self.log.debug('adjusting polarity switches')
                    other.start(0)
                    switch.start(1)
                    # not waiting for a bit here can lead to a current spike
                    # through the magnet
                    sleep(2.0)
                # then, just continue ramping to the absolute value
                value = abs(value)
            self.log.debug('ramping to %.2f A' % value)
            currentval = self._taco_guard(self._dev.read)
            diff = value - currentval
            direction = diff > 0 and 1 or -1
            stepwidth = 5
            # half a second is the communication time
            delay = (60 / self.ramp) * 5 - 0.5
            steps, _fraction = divmod(abs(diff), stepwidth)
            for _i in xrange(int(steps)):
                if self._stopflag:
                    self.log.debug('got stop flag, quitting ramp')
                    return
                currentval += direction * stepwidth
                self.log.debug('ramp step: %.2f A' % currentval)
                self._taco_guard(self._dev.write, currentval)
                sleep(delay)
            self.log.debug('final step: %.2f A' % value)
            self._taco_guard(self._dev.write, value)
            self.log.debug('done')
            if value == 0 and abs(self._taco_guard(self._dev.read)) < 5:
                self.log.debug('switching off current')
                self._adevs['plusswitch'].start(0)
                self._adevs['minusswitch'].start(0)
        except Exception:
            self.log.warning('could not move to %.2f A' % value, exc=1)
            self._errorflag = 'ramping not successful'

    def doStart(self, value):
        if self._thread is not None:
            self._thread.join()
        self._errorflag = None
        # never go to zero directly; this will switch off both polarity relais,
        # which leads to a buildup of voltage in the supply
        if value == 0:
            value = 0.001
        self._thread = threading.Thread(target=self._move_to, args=(value,))
        self._thread.setDaemon(True)
        self._thread.start()

    def doRead(self, maxage=0):
        sign = +1
        if self._adevs['minusswitch'].read() & 1:
            sign = -1
        return sign * self._taco_guard(self._dev.read)

    def doWait(self):
        while self._thread and self._thread.isAlive():
            self._thread.join(1)
        waitForStatus(self, 0.5)

    def doStop(self):
        self._stopflag = True

    def doStatus(self, maxage=0):
        if self._errorflag:
            return status.ERROR, self._errorflag
        return TacoDevice.doStatus(self, maxage)

    def doReset(self):
        self._errorflag = None
        return TacoDevice.doReset(self)


class LambdaField(HasLimits, Moveable):

    attached_devices = {
        'controller':  (Moveable, 'The controller'),
    }

    parameters = {
        'calibration': Param('Coefficients for calibration polynomial: '
                             '[a0, a1, a2, ...] calculates '
                             'B(I) = a0 + a1*I + a2*I**2 + ... in T',
                             type=listof(float), settable=True,
                             default=[0, 1.]),
    }

    parameter_overrides = {
        'unit':   Override(mandatory=False, default='T'),
        'fmtstr': Override(default='%.4f'),
    }

    @usermethod
    def calibrate(self, *scannumbers):
        """Calibrate the B to I conversion, argument is one or more scan numbers.

        Example:

        >>> B_mira.calibrate(351)
        """
        scans = session.experiment._last_datasets
        self.log.info('determining calibration from scans, please wait...')
        Is = []
        Bs = []
        dBs = []
        for scan in scans:
            if scan.sinkinfo.get('number') not in scannumbers:
                continue
            if 'B' not in scan.ynames or 'I' not in scan.xnames:
                self.log.info('%s is not a calibration scan'
                              % scan.sinkinfo['number'])
                continue
            xindex = scan.xnames.index('I')
            yindex = scan.ynames.index('B')
            yunit = scan.yunits[yindex]
            if yunit == 'T':
                factor = 1.0
            elif yunit == 'mT':
                factor = 1e-3
            elif yunit == 'uT':
                factor = 1e-6
            else:
                raise NicosError(self, 'unknown unit for B field '
                                 'readout: %r' % yunit)
            for xr, yr in zip(scan.xresults, scan.yresults):
                Is.append(xr[xindex])
                Bs.append(yr[yindex] * factor)
                dBs.append(yr[yindex+1] * factor)
        if not Is:
            self.log.error('no calibration data found')
            return
        def model(x, *v):
            return sum(v[i]*x**i for i in range(4))
        fit = Fit(model, ['a%d' % i for i in range(4)], [1] * 4)
        res = fit.run('calibration', Is, Bs, dBs)
        if res._failed:
            self.log.warning('fit failed')
            return
        self.log.info('setting fit result: %s' % res._pars[1])
        self.calibration = res._pars[1]

    def doRead(self, maxage=0):
        I = self._adevs['controller'].read(maxage)
        B = 0
        for i, a_i in enumerate(self.calibration):
            B += a_i * I**i
        return B

    def doStart(self, value):
        def B(I):
            Bv = 0
            for i, a_i in enumerate(self.calibration):
                Bv += a_i * I**i
            return Bv
        # find correct I value by approximation
        Iv = 0
        for Iv in range(-250, 250):
            B1, B2 = B(Iv), B(Iv + 1)
            if B1 <= value <= B2 or B2 <= value <= B1:
                break
        else:
            raise InvalidValueError(
                self, 'cannot convert B = %.4f T to current' % value)
        I = Iv + (value - B1) / (B2 - B1)
        self.log.debug('B1=%.4f, B2=%.4f, Iv=%d, setting current to %.2f'
                       % (B1, B2, Iv, I))
        assert abs(B(I) - value) < 0.1
        self._adevs['controller'].start(I)

    def doStatus(self, maxage=0):
        return self._adevs['controller'].status(maxage)

    def doWait(self):
        self._adevs['controller'].wait()
