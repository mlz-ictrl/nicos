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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""Basic data acquisition, new API."""

from time import sleep, time as currenttime

from nicos import session
from nicos.core.errors import NicosError
from nicos.core.constants import SIMULATION, INTERRUPTED, FINAL
from nicos.core.params import Value


def _wait_for_continuation(delay, only_pause=False):
    """Wait until any countloop requests are processed and the watchdog
    "pausecount" is empty.

    Return True if measurement can continue, or False if detectors should be
    stopped.
    """
    while session.countloop_request:
        req, current_msg = session.countloop_request  # pylint: disable=E0633
        session.countloop_request = None
        if only_pause and req != 'pause':
            # for 'finish' requests, we don't want to finish *before* starting the
            # measurement, because then we don't have any results to return
            session.log.info('request for early finish ignored, not counting')
            return True
        exp = session.experiment
        if req == 'finish':
            session.log.warning('counting stopped: ' + current_msg)
            return False
        else:
            session.log.warning('counting paused: ' + current_msg)
        # allow the daemon to pause here, if we were paused by it
        session.breakpoint(3)
        # still check for other conditions
        while exp.pausecount:
            if exp.pausecount != current_msg:
                current_msg = exp.pausecount
                session.log.warning('counting paused: ' + current_msg)
            sleep(delay)
            # also allow the daemon to pause here
            session.breakpoint(3)
            if session.countloop_request:
                # completely new request? continue with outer loop
                break
    session.log.info('counting resumed')
    return True


def acquire(point, preset):
    """Low-level acquisition function.

    The loop delay is configurable in the instrument object, and defaults to
    0.025 seconds.

    The result is stored in the given argument, which must be an empty list.
    This is so that a result can be returned even when a stop exception is
    propagated upwards.
    """
    # put detectors in a set and discard them when completed
    detset = set(point.detectors)
    delay = (session.instrument and session.instrument.countloopdelay or 0.025
             if session.mode != SIMULATION else 0.0)

    session.beginActionScope('Counting')
    if session.countloop_request:
        _wait_for_continuation(delay, only_pause=True)
    if preset:
        for det in point.detectors:
            det.setPreset(**preset)
    session.data.updateMetainfo()
    point.started = currenttime()
    try:
        for det in point.detectors:
            det.start()
    except:
        session.endActionScope()
        raise
    sleep(delay)
    try:
        while True:
            looptime = currenttime()
            for det in list(detset):
                if session.mode != SIMULATION:
                    quality = det.duringMeasureHook(looptime - point.started)
                if det.isCompleted():
                    det.finish()
                    quality = FINAL
                if quality:
                    try:
                        res = det.readResults(quality)
                    except Exception:
                        det.log.exception('error reading measurement data')
                        res = None
                    session.data.putResults(quality, {det.name: res})
                if quality == FINAL:
                    detset.discard(det)
            if not detset:
                # all detectors finished measuring
                break
            if session.countloop_request:
                for det in detset:
                    if not det.pause():
                        session.log.warning(
                            'detector %r could not be paused' % det.name)
                if not _wait_for_continuation(delay):
                    for det in detset:
                        # next iteration of loop will see det is finished
                        det.finish()
                else:
                    for det in detset:
                        det.resume()
            sleep(delay)
    except BaseException as e:
        point.finished = currenttime()
        if e.__class__.__name__ != 'ControlStop':
            session.log.warning('Exception during count, trying to save data',
                                exc=True)
        for det in detset:
            try:
                # XXX: in theory, stop() can return True or False to indicate
                # whether saving makes sense.
                #
                # However, it might be better to leave that to the data sink
                # handling the INTERRUPTED quality.
                det.stop()
                res = det.readResults(INTERRUPTED)
            except Exception:
                det.log.exception('error reading measurement data')
                res = None
            session.data.putResults(INTERRUPTED, {det.name: res})
        raise
    finally:
        point.finished = currenttime()
        session.endActionScope()


def read_environment(envlist):
    """Read out environment devices to get entries in the dataset."""
    values = {}
    for dev in envlist:
        if isinstance(dev, DevStatistics):
            try:
                dev.dev.read(0)
            except NicosError:
                pass
            continue
        try:
            val = dev.read(0)
        except Exception:
            # XXX warn?
            # self.handleError('read', err)
            val = [None] * len(dev.valueInfo())
        values[dev.name] = (currenttime(), val)
    session.data.putValues(values)


class DevStatistics(object):
    """Object to use in the environment list to get not only a single device
    value, but statistics such as average, minimum or maximum over the time of
    counting during a scan point.
    """

    statname = None

    def __init__(self, dev):
        self.dev = dev

    def __str__(self):
        return '%s:%s' % (self.dev, self.statname)

    def retrieve(self, valuestats):
        raise NotImplementedError('%s.retrieve() must be implemented'
                                  % self.__class__.__name__)

    def valueInfo(self):
        raise NotImplementedError('%s.valueInfo() must be implemented'
                                  % self.__class__.__name__)


class Average(DevStatistics):
    """Collects the average of the device value."""

    statname = 'avg'

    def retrieve(self, valuestats):
        if self.dev.name in valuestats:
            return [valuestats[self.dev.name][0]]
        return [None]

    def valueInfo(self):
        return Value('%s:avg' % self.dev, unit=self.dev.unit,
                     fmtstr=self.dev.fmtstr),


class MinMax(DevStatistics):
    """Collects the minimum and maximum of the device value."""

    statname = 'minmax'

    def retrieve(self, valuestats):
        if self.dev.name in valuestats:
            return [valuestats[self.dev.name][2],
                    valuestats[self.dev.name][3]]
        return [None, None]

    def valueInfo(self):
        return (Value('%s:min' % self.dev, unit=self.dev.unit,
                      fmtstr=self.dev.fmtstr),
                Value('%s:max' % self.dev, unit=self.dev.unit,
                      fmtstr=self.dev.fmtstr))


DevStatistics.subclasses = {
    Average.statname: Average,
    MinMax.statname:  MinMax,
}
