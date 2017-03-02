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

import os
import sys
import time
import logging
import tempfile
from os import path
from threading import Thread

import zmq

from nicos import session, config
from nicos.core import SIMULATION, NicosError
from nicos.core.utils import User
from nicos.core.sessions import Session
from nicos.core.sessions.utils import LoggingStdout
from nicos.protocols.daemon import serialize, unserialize
from nicos.utils import createSubprocess
from nicos.utils.loggers import TRANSMIT_ENTRIES
from nicos.utils.messaging import nicos_zmq_ctx
from nicos.pycompat import iteritems, exec_, cPickle as pickle


class SimLogSender(logging.Handler):
    """
    Log handler sending messages to the original daemon via a pipe.
    """

    def __init__(self, socket, session, finish_only=False):
        logging.Handler.__init__(self)
        self.socket = socket
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
    def run(cls, sock, prefix, setups, user, code):
        session.__class__ = cls

        socket = nicos_zmq_ctx.socket(zmq.DEALER)
        socket.connect(sock)

        # we either get an empty message (retrieve cache data ourselves)
        # or a pickled key-value database
        data = socket.recv()
        db = pickle.loads(data) if data else None

        session.globalprefix = prefix
        # send log messages back to daemon if requested
        session.log_sender = SimLogSender(socket, session)

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
            session.simulationSync(db)

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
    """Thread for starting a simulation process, receiving messages from a zmq
    socket and displaying/sending them to the client.
    """

    def __init__(self, sandbox, code, prefix, setups, user, emitter,
                 more_args=None):
        Thread.__init__(self, target=self._target,
                        name='SimulationSupervisor',
                        args=(sandbox, emitter, prefix, setups, code, user,
                              more_args or []))
        # "daemonize this thread" attribute, not referring to the NICOS daemon.
        self.daemon = True

    def _target(self, sandbox, emitter, prefix, setups, code, user, args):
        socket = nicos_zmq_ctx.socket(zmq.DEALER)
        poller = zmq.Poller()
        poller.register(socket, zmq.POLLIN)
        if sandbox:
            # create a new temporary directory for the sandbox helper to
            # mount the filesystem
            tempdir = tempfile.mkdtemp()
            rootdir = path.join(tempdir, 'root')
            os.mkdir(rootdir)
            # since the sandbox does not have TCP connection, use a Unix socket
            sockname = 'ipc://' + path.join(tempdir, 'sock')
            socket.bind(sockname)
            prefixargs = [sandbox, rootdir, str(os.getuid()), str(os.getgid())]
        else:
            port = socket.bind_to_random_port('tcp://127.0.0.1')
            sockname = 'tcp://127.0.0.1:%s' % port
            prefixargs = []
        scriptname = path.join(config.nicos_root, 'bin', 'nicos-simulate')
        userstr = '%s,%d' % (user.name, user.level)
        proc = createSubprocess(prefixargs +
                                [sys.executable, scriptname,
                                 sockname, prefix, ','.join(setups),
                                 userstr, code] + args)
        if sandbox:
            if not session.current_sysconfig.get('cache'):
                raise NicosError('no cache is configured')
            socket.send(pickle.dumps(session.cache.get_values()))
        else:
            # let the subprocess connect to the cache
            socket.send(b'')
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
                    break
            else:
                raise Exception('did not terminate within 5 seconds')
        except Exception:
            session.log.exception('Error waiting for dry run process')
        if sandbox:
            try:
                os.rmdir(rootdir)
                os.rmdir(tempdir)
            except Exception:
                pass
