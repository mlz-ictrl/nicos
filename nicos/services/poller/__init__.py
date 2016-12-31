#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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

"""Contains a process that polls devices automatically."""

import os
import sys
import errno
import signal
import traceback
import threading
import subprocess
from os import path
from time import time as currenttime, sleep

from nicos import session, config
from nicos.core import status, listof, Device, Readable, Param, \
    ConfigurationError, DeviceAlias
from nicos.utils import whyExited, watchFileContent, loggers, createThread
from nicos.devices.generic.cache import CacheReader
from nicos.pycompat import listitems, queue as Queue


POLL_MIN_VALID_TIME = 0.15  # latest time slot to poll before value times out due to maxage
POLL_BUSY_INTERVAL = 0.5    # if dev is busy, poll this often
POLL_MIN_WAIT = 0.1         # minimum amount of time between two calls to poll()


class Poller(Device):

    parameters = {
        'autosetup':  Param('True if all master setups should always be polled',
                            type=bool, default=True),
        'poll':       Param('Setups that should be polled if in master setup '
                            '(only used if autosetup is false)',
                            type=listof(str)),
        'alwayspoll': Param('Setups whose devices should always be polled',
                            type=listof(str), mandatory=True),
        'neverpoll':  Param('Setups that should never be polled, even if in '
                            'master setup', type=listof(str)),
        'blacklist':  Param('Devices that should never be polled',
                            type=listof(str)),
    }

    def doInit(self, mode):
        self._stoprequest = False
        self._workers = []
        self._creation_lock = threading.Lock()

    def doUpdateLoglevel(self, value):
        # override this since the base Device does not set a new loglevel in
        # a poller session
        self.log.setLevel(loggers.loglevels[value])

    def _worker_thread(self, devname, dev, queue):

        def reconfigure_dev_target(key, value, time, oldvalues={}):  # pylint: disable=W0102
            if value is not None:
                queue.put('dev_target', False)
                oldvalues[key] = value

        def reconfigure_dev_status(key, value, time, oldvalues={}):  # pylint: disable=W0102
            if value[0] != oldvalues.get(key):
                if value[0] == status.BUSY:  # just went busy, wasn't before!
                    queue.put('dev_busy', False)
                else:
                    queue.put('dev_normal', False)
                oldvalues[key] = value[0]  # only store status code!

        def reconfigure_adev_value(key, value, time, oldvalues={}):  # pylint: disable=W0102
            if value != oldvalues.get(key):
                queue.put('adev_value', False)
                oldvalues[key] = value

        def reconfigure_adev_target(key, value, time, oldvalues={}):  # pylint: disable=W0102
            if value != oldvalues.get(key):
                queue.put('adev_target', False)
                oldvalues[key] = value

        def reconfigure_adev_status(key, value, time, oldvalues={}):  # pylint: disable=W0102
            if value[0] != oldvalues.get(key):
                if value[0] == status.BUSY:  # just went busy, wasn't before!
                    queue.put('adev_busy', False)
                else:
                    queue.put('adev_normal', False)
                oldvalues[key] = value[0]  # only store status code!

        def reconfigure_param(key, value, time):
            queue.put('param', False)

        def poll_loop(dev):
            """
            Polling a device and react to updates received via cache

            The wait between pollings is controlled by an Queue, so that
            events from other threads (e.g. quit or cache updates) can
            trigger a wakeup.

            Based on the events received, the polling interval is adjusted.

            Read errors in the device raise and this gets restarted from the
            outer loop. If the received event is 'quit' we just exit here.
            """
            # get the initial values
            interval = dev.pollinterval
            maxage = dev.pollinterval - POLL_MIN_VALID_TIME

            i = 0
            lastpoll = 0  # last timestamp of succesfull poll

            while not self._stoprequest:
                # determine maximum waiting time with a default of 1h
                ct = currenttime()
                nextpoll = lastpoll + (interval or 3600)
                # note: dev.maxage is intended here!
                timesout = lastpoll + dev.maxage - POLL_MIN_VALID_TIME
                dnext = nextpoll - ct
                dto = timesout - ct
                maxwait = min(dnext, dto)
                self.log.debug('%-10s: maxwait is %g (nextpoll=%g, timesout=%g)',
                               dev, maxwait, dnext, dto)

                # only wait for events if there is time, otherwise just poll
                if maxwait > 0:
                    # wait for event
                    try:
                        # if the timeout is reached, this raises Queue.Empty
                        event = queue.get(True, maxwait)
                        self.log.debug('%-10s: Event %s', dev, event)

                        # handle events....
                        # use pass to trigger a poll or continue to just fetch the next event
                        if event == 'adev_busy':  # one of our attached_devices went busy
                            interval = POLL_BUSY_INTERVAL
                            maxage = POLL_BUSY_INTERVAL / 2
                            # also poll
                        elif event == 'adev_normal':  # one of our attached_devices is no more busy
                            pass  # also poll
                        elif event == 'adev_target':  # one of our attached_devices got new target
                            interval = POLL_BUSY_INTERVAL
                            maxage = POLL_BUSY_INTERVAL / 2
                            continue
                        elif event == 'adev_value':  # one of our attached_devices changed value
                            interval = POLL_BUSY_INTERVAL
                            maxage = POLL_BUSY_INTERVAL / 2
                            continue
                        elif event == 'dev_busy':  # our device went busy
                            interval = POLL_BUSY_INTERVAL
                            maxage = POLL_BUSY_INTERVAL / 2
                            continue
                        elif event == 'dev_normal':  # our device is no more busy
                            continue
                        elif event == 'dev_target':  # our device got new target
                            interval = POLL_BUSY_INTERVAL
                            maxage = POLL_BUSY_INTERVAL / 2
                            continue
                        elif event == 'dev_value':  # our device changed value
                            continue
                        elif event == 'param':  # update local vars
                            interval = dev.pollinterval
                            maxage = dev.pollinterval - POLL_MIN_VALID_TIME
                            continue
                        elif event == 'quit':  # stop doing anything
                            return

                    except Queue.Empty:
                        pass  # just poll if timed out
                else:
                    self.log.debug('%-10s: ignoring events for one round', dev)

                # also do rate-limiting if too many events occur which would
                # retrigger this device
                if lastpoll + POLL_MIN_WAIT > currenttime():
                    self.log.debug('%-10s: rate-limiting poll()', dev)
                    continue

                # only poll if enabled
                if dev.pollinterval is not None:
                    i += 1
                    # if the polling fails, raise into outer loop which handles this...
                    stval, rdval = dev.poll(i, maxage=maxage)
                    self.log.debug('%-10s: status = %-25s, value = %s',
                                   dev, stval, rdval)
                    # adjust timing of we are no longer busy
                    if stval is not None and stval[0] != status.BUSY:
                        interval = dev.pollinterval
                        maxage = dev.pollinterval - POLL_MIN_VALID_TIME
                # keep track of when we last (tried to) poll
                lastpoll = currenttime()
                # reset error count and waittime after first successful poll
                if i == 1:
                    errstate[:] = [0, 10]
                    self.log.info('%-10s: polled successfully', dev)
            # end of while not self._stoprequest
        # end of poll_loop(dev)

        errstate = [0, 10]  # number of errors, current wait time
        registered = False

        self.log.info('%-10s: starting main polling loop', devname)
        while not self._stoprequest:
            try:
                if dev is None:
                    # device creation should be serialized due to the many
                    # global state updates in the session object
                    with self._creation_lock:
                        dev = session.getDevice(devname)
                    if not isinstance(dev, Readable):
                        self.log.info('%s is not a readable', dev)
                        return
                    if isinstance(dev, (DeviceAlias, CacheReader)):
                        self.log.info('%s is a DeviceAlias or a CacheReader, '
                                      'not polling', dev)
                        return

                if not registered:
                    self.log.debug('%-10s: registering callbacks', dev)
                    # keep track of some parameters via cache callback
                    # session.cache.addCallback(dev, 'value', reconfigure_dev_value)  # spams events
                    session.cache.addCallback(dev, 'target', reconfigure_dev_target)
                    session.cache.addCallback(dev, 'status', reconfigure_dev_status)  # may spam events
                    session.cache.addCallback(dev, 'maxage', reconfigure_param)
                    session.cache.addCallback(dev, 'pollinterval', reconfigure_param)
                    # also subscribe to value and status updates of attached devices.
                    for adev in dev._adevs.values():
                        if not isinstance(adev, Readable):
                            continue
                        session.cache.addCallback(adev, 'value', reconfigure_adev_value)
                        session.cache.addCallback(adev, 'target', reconfigure_adev_target)
                        session.cache.addCallback(adev, 'status', reconfigure_adev_status)
                registered = True

                poll_loop(dev)

            except Exception:
                errstate[0] += 1
                # only warn 5 times in a row, and later occasionally
                if dev is None:
                    self.log.warning('%-10s: error creating device, '
                                     'retrying in %d sec',
                                     devname, errstate[1], exc=True)
                else:
                    self.log.warning('%-10s: error polling, retrying in '
                                     '%d sec', dev, errstate[1],
                                     exc=True)
                if errstate[0] % 5 == 0:
                    # use exponential back-off for the wait time; in the worst
                    # case wait 10 minutes between attempts
                    errstate[1] = min(2 * errstate[1], 600)
                # sleep up to wait time
                try:
                    queue.get(True, errstate[1])  # may return earlier
                except Queue.Empty:
                    pass
        # end of while not self._stoprequest
    # end of _worker_thread

    def start(self, setup=None):
        self._setup = setup
        if setup is None:
            return self._start_master()
        self.log.info('%s poller starting', setup)

        if setup == '[dummy]':
            return

        try:
            session.loadSetup(setup, allow_startupcode=False)
            for devname in session.getSetupInfo()[setup]['devices']:
                if devname in self.blacklist:
                    self.log.debug('not polling %s, it is blacklisted', devname)
                    continue
                # import the device class in the main thread; this is necessary
                # for some external modules like Epics
                self.log.debug('importing device class for %s', devname)
                try:
                    dev = session.createDevice(devname)
                except Exception:
                    # creation failed, try at least to import
                    dev = None
                    self.log.warning('%-10s: error creating device initially',
                                     devname, exc=True)
                    try:
                        session.importDevice(devname)
                    except Exception:
                        self.log.warning('%-10s: error importing device class, '
                                         'not retrying this device',
                                         devname, exc=True)
                        continue
                self.log.debug('starting thread for %s', devname)
                queue = Queue.Queue()
                worker = createThread('%s poller' % devname,
                                      self._worker_thread,
                                      args=(devname, dev, queue))
                worker.queue = queue
                self._workers.append(worker)
                # start staggered to not poll all devs at once....
                # use just a small delay, exact value does not matter
                sleep(0.0719)

        except ConfigurationError as err:
            self.log.warning('Setup %r has failed to load!', setup)
            self.log.error(err, exc=True)
            self.log.warning('Not polling any devices!')

        # start a thread checking for modification of the setup file
        createThread('refresh checker', self._checker, args=(setup,))
        self.log.info('%s poller startup complete', setup)

    def _checker(self, setupname):
        if setupname not in session._setup_info:
            # setup was removed since, do not try to watch it
            return
        fn = session._setup_info[setupname]['filename']
        if not path.isfile(fn):
            self.log.warning('setup watcher could not find %r', fn)
            return
        watchFileContent(fn, self.log)
        self.log.info('setup file changed; restarting poller process')
        self.quit()

    def wait(self):
        if self._setup is None:
            if os.name == 'nt':
                return self._wait_master_nt()
            return self._wait_master()
        while not self._stoprequest:
            sleep(1)
        for worker in self._workers:
            worker.join()

    def quit(self, signum=None):
        if self._setup is None:
            return self._quit_master(signum)
        if self._stoprequest:
            return  # already quitting
        self.log.info('poller quitting on signal %s...', signum)
        self._stoprequest = True
        for worker in self._workers:
            worker.queue.put('quit', False)  # wake up to quit
        for worker in self._workers:
            worker.join()
        self.log.info('poller finished')

    def reload(self):
        if self._setup is not None:
            # do nothing for single pollers
            return
        self.log.info('got SIGUSR1, restarting all pollers')
        for pid in list(self._childpids):
            try:
                os.kill(pid, signal.SIGTERM)
            except Exception as err:
                self.log.error(str(err))

    def statusinfo(self):
        self.log.info('got SIGUSR2')
        if self._setup is not None:
            info = []
            for worker in self._workers:
                wname = worker.getName()
                if worker.isAlive():
                    info.append('%s: alive' % wname)
                else:
                    info.append('%s: dead' % wname)
            self.log.info(', '.join(info))
            self.log.info('current stacktraces for each thread:')
            active = threading._active
            for tid, frame in listitems(sys._current_frames()):
                if tid in active:
                    name = active[tid].getName()
                else:
                    name = str(tid)
                self.log.info('%s: %s', name,
                              ''.join(traceback.format_stack(frame)))

    def _start_master(self):
        # the poller consists of two types of processes: one master process
        # that spawns and waits for the children (and restarts them in case
        # of unintended termination, e.g. by segfault); and N slave processes
        # (one for each setup loaded) that do the actual polling

        self._childpids = {}
        self._children = {}

        if not self._cache:
            raise ConfigurationError('the poller needs a cache configured')

        # wait for the cache connection (which might not yet be available if the
        # cache server has been started directly before the poller): the poller
        # is not useful if there is no cache connection, and if we connect later
        # we miss the mastersetups
        if not self._cache.is_connected():
            self.log.info('waiting until cache is connected')
            while not self._cache.is_connected():
                if self._stoprequest:  # stopped while waiting?
                    return
                sleep(0.2)

        # by default, the polled devices always reflects the loaded setups
        # in the current NICOS master, but it can be configured to only
        # poll specific setups if loaded, or always:
        #
        # * self.poll: poll if loaded by master
        # * self.alwayspoll: always poll
        # * self.neverpoll: never poll, even if loaded
        #
        mastersetups = set(self._cache.get(session, 'mastersetup') or [])
        if self.autosetup:
            self._setups = mastersetups
        else:
            self._setups = mastersetups & set(self.poll)
        self._setups.difference_update(self.neverpoll)
        self._setups.update(self.alwayspoll)

        if not self._setups:
            # if no pollers are running, this would terminate the _wait_master
            # loop instantly, so wait here until there are some setups
            self._setups.add('[dummy]')

        for setup in self._setups:
            self._start_child(setup)

        # listen for changes in master setups if we depend on them
        if self.autosetup or self.poll:
            self._cache.addCallback(session, 'mastersetup', self._reconfigure)

    def _reconfigure(self, key, value, time):
        self.log.info('reconfiguring for new master setups %s', value)
        session.readSetups()
        old_setups = self._setups

        if self.autosetup:
            new_setups = set(value)
        else:
            new_setups = set(value) & set(self.poll)
        new_setups.difference_update(self.neverpoll)
        new_setups.update(self.alwayspoll)
        if not new_setups:  # setup list shouldn't be empty, see above
            new_setups.add('[dummy]')
        self._setups = new_setups

        for setup in old_setups - new_setups:
            os.kill(self._children[setup].pid, signal.SIGTERM)
        for setup in new_setups - old_setups:
            self._start_child(setup)

    def _start_child(self, setup):
        poller_script = path.join(config.nicos_root, 'bin', 'nicos-poller')
        process = subprocess.Popen([sys.executable, poller_script, setup])
        # we need to keep a reference to the Popen object, since it calls
        # os.wait() itself in __del__
        self._children[setup] = process
        self._childpids[process.pid] = setup
        session.log.info('started %s poller, PID %s', setup, process.pid)

    def _wait_master(self):
        # wait for children to terminate; restart them if necessary
        while True:
            try:
                pid, ret = os.wait()
            except OSError as err:
                if err.errno == errno.EINTR:
                    # raised when the signal handler is fired
                    continue
                elif err.errno == errno.ECHILD:
                    # no further child processes found
                    break
                raise
            else:
                # a process exited; restart if necessary
                setup = self._childpids.pop(pid)
                del self._children[setup]
                if setup in self._setups and not self._stoprequest:
                    session.log.warning('%s poller terminated with %s, '
                                        'restarting', setup, whyExited(ret))
                    self._start_child(setup)
                else:
                    session.log.info('%s poller terminated with %s',
                                     setup, whyExited(ret))
        session.log.info('all pollers terminated')

    def _wait_master_nt(self):
        # this is the same as _wait_master, but with active polling instead
        # of using os.wait(), which does not exist on Windows
        while True:
            sleep(0.5)
            if not self._children:
                break
            for setup, ch in listitems(self._children):
                ret = ch.poll()
                if ret is not None:
                    # a process exited; restart if necessary
                    del self._childpids[ch.pid]
                    del self._children[setup]
                    if setup in self._setups and not self._stoprequest:
                        session.log.warning('%s poller terminated with %s, '
                                            'restarting', setup, ret)
                        self._start_child(setup)
                        break
                    else:
                        session.log.info('%s poller terminated with %s',
                                         setup, ret)
        session.log.info('all pollers terminated')

    def _quit_master(self, signum=None):
        self._stoprequest = True
        self.log.info('quitting on signal %s...', signum)
        for pid in self._childpids:
            try:
                os.kill(pid, signal.SIGTERM)
            except OSError as err:
                if err.errno == errno.ESRCH:
                    # process was already terminated
                    continue
                session.log.info('OSError during shutdown', exc=True)
            except Exception:
                session.log.info('Exception during shutdown', exc=True)

        def kill_all():
            for pid in self._childpids:
                try:
                    os.kill(pid, signal.SIGKILL)
                except Exception:
                    pass
        killer = threading.Timer(4, kill_all)
        killer.setDaemon(True)
        killer.start()
