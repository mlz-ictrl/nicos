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

"""Simulation session with support for ZeroMQ messaging."""

from __future__ import print_function

import sys
import time
import logging
import subprocess
from os import path
from threading import Thread

import zmq

from nicos import session, config
from nicos.core import SIMULATION
from nicos.core.utils import User
from nicos.core.sessions import Session
from nicos.core.sessions.utils import LoggingStdout
from nicos.protocols.daemon import serialize, unserialize
from nicos.utils.loggers import TRANSMIT_ENTRIES
from nicos.utils.messaging import nicos_zmq_ctx
from nicos.pycompat import iteritems, exec_


class SimLogSender(logging.Handler):
    """
    Log handler sending messages to the original daemon via a pipe.
    """

    def __init__(self, port, session, finish_only=False):
        logging.Handler.__init__(self)
        self.socket = nicos_zmq_ctx.socket(zmq.PUSH)
        self.socket.connect('tcp://127.0.0.1:%d' % port)
        self.session = session
        self.finish_only = finish_only
        self.starttime = None
        self.devices = []
        self.aliases = []

    def begin_exec(self):
        from nicos.core import Readable
        from nicos.core.device import DeviceAlias
        # Collect information on timing and range of all devices
        self.starttime = self.session.clock.time
        for devname, dev in iteritems(self.session.devices):
            if isinstance(dev, DeviceAlias):
                self.aliases.append(devname)
            elif isinstance(dev, Readable):
                self.devices.append(devname)
                dev._sim_min = None
                dev._sim_max = None
        self.level = 0

    def emit(self, record):
        if not self.finish_only:
            msg = [getattr(record, e) for e in TRANSMIT_ENTRIES]
            if not hasattr(record, 'nonl'):
                msg[3] += '\n'
            self.socket.send(serialize(msg))

    def finish(self, exception=False):
        stoptime = -1 if exception else self.session.clock.time
        devinfo = {}
        for devname in self.devices:
            dev = self.session.devices.get(devname)
            minmax = dev._sim_getMinMax()
            for _name, _value, _min, _max in minmax:
                try:
                    devinfo[_name] = (_value, _min, _max, [])
                except Exception:
                    pass
        for devname in self.aliases:
            adev = self.session.devices.get(devname)
            if adev and adev.alias:
                devname = session.devices[adev.alias].name
                if devname in devinfo:
                    devinfo[devname][3].append(adev.name)
        self.socket.send(serialize((stoptime, devinfo)))

    def delay(self, _secs):
        # Not necessary for dry run.
        pass


class SimulationSession(Session):
    """
    Subclass of Session for spawned simulation processes.
    """

    sessiontype = SIMULATION
    has_datamanager = True

    def begin_setup(self):
        self.log_sender.level = logging.ERROR  # log only errors before code starts

    @classmethod
    def run(cls, port, prefix, setups, user, code):
        session.__class__ = cls

        session.globalprefix = prefix
        # send log messages back to daemon if requested
        session.log_sender = SimLogSender(port, session)

        username, level = user.rsplit(',', 1)
        session._user = User(username, int(level))

        try:
            session.__init__(SIMULATION)
        except Exception as err:
            try:
                session.log.exception('Fatal error while initializing')
            finally:
                print('Fatal error while initializing:', err, file=sys.stderr)
            return 1

        # Give a sign of life and then tell the log handler to only log
        # errors during setup.
        session.log.info('setting up dry run...')
        session.begin_setup()
        # Handle "print" statements in the script.
        sys.stdout = LoggingStdout(sys.stdout)

        try:
            # Initialize the session in simulation mode.
            session._mode = SIMULATION

            # Load the setups from the original system, this should give the
            # information about the cache address.
            session.log.info('loading simulation mode setups: %s',
                             ', '.join(setups))
            session.loadSetup(setups, allow_startupcode=False)

            # Synchronize setups and cache values.
            session.log.info('synchronizing to master session')
            session.simulationSync()

            # Set session to always abort on errors.
            session.experiment.errorbehavior = 'abort'
        except:  # really *all* exceptions -- pylint: disable=W0702
            session.log.exception('Exception in dry run setup')
            session.log_sender.finish()
            session.shutdown()
            return 1

        # Set up log handlers to output everything.
        session.log_sender.begin_exec()
        # Execute the script code.
        exception = False
        try:
            exec_(code, session.namespace)
        except:  # pylint: disable=W0702
            session.log.exception('Exception in dry run')
            exception = True
        else:
            session.log.info('Dry run finished')
        finally:
            session.log_sender.finish(exception)

        # Shut down.
        session.shutdown()

    def _initLogging(self, prefix=None, console=True):
        Session._initLogging(self, prefix, console=False)
        self.log.manager.globalprefix = self.globalprefix
        self.log.addHandler(self.log_sender)

    def getExecutingUser(self):
        return self._user


class SimulationSupervisor(Thread):
    """
    Thread for starting a simulation process, receiving messages from a pipe
    and displaying/sending them to the client.
    """

    def __init__(self, code, prefix, setups, user, emitter, more_args=None):
        scriptname = path.join(config.nicos_root, 'bin', 'nicos-simulate')
        Thread.__init__(self, target=self._target,
                        name='SimulationSupervisor',
                        args=(emitter, scriptname, prefix, setups, code, user,
                              more_args or []))
        # "daemonize this thread" attribute, not referring to the NICOS daemon.
        self.daemon = True

    def _target(self, emitter, scriptname, prefix, setups, code, user, args):
        socket = nicos_zmq_ctx.socket(zmq.PULL)
        poller = zmq.Poller()
        poller.register(socket, zmq.POLLIN)
        port = socket.bind_to_random_port('tcp://127.0.0.1')
        userstr = '%s,%d' % (user.name, user.level)
        # start nicos-simulate process
        proc = subprocess.Popen([sys.executable, scriptname,
                                 str(port), prefix, ','.join(setups),
                                 userstr, code] + args)
        while True:
            res = poller.poll(500)
            if not res:
                if proc.poll() is not None:
                    session.log.warning('Dry run has terminated prematurely')
                    return
                continue
            msg = unserialize(socket.recv())
            if isinstance(msg, list):
                # it's a message
                if emitter:
                    emitter.emit_event('message', msg)
                else:
                    record = logging.LogRecord(msg[0], msg[2], msg[5],
                                               0, msg[3], (), None)
                    record.message = msg[3].rstrip()
                    session.log.handle(record)
            else:
                # it's the result
                if emitter:
                    emitter.emit_event('simresult', msg)
                # In the console session, the summary is printed by the
                # sim() command.
                socket.close()
                break
        # wait for the process, but only for 5 seconds after the result
        # has arrived
        wait_start = time.time()
        try:
            # Python 3.x has a timeout argument for poll()...
            while time.time() < wait_start + 5:
                if proc.poll() is not None:
                    return
            raise Exception('did not terminate within 5 seconds')
        except Exception:
            session.log.exception('Error waiting for dry run process')
