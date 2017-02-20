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

"""
The connection handler for the execution daemon, handling the protocol
commands.
"""

import os
import base64
import socket
import tempfile
try:
    import rsa  # pylint: disable=F0401
except ImportError:
    rsa = None

import hashlib

from nicos import session, nicos_version, custom_version, config
from nicos.core import ADMIN, ConfigurationError, SPMError, User
from nicos.core.data import ScanData
from nicos.services.daemon.auth import AuthenticationError
from nicos.services.daemon.utils import LoggerWrapper
from nicos.services.daemon.script import ScriptRequest, ScriptError, \
    RequestError
from nicos.protocols.daemon import STATUS_IDLE, STATUS_IDLEEXC, \
    STATUS_RUNNING, STATUS_STOPPING, STATUS_INBREAK, SIM_STATES, \
    BREAK_NOW, DAEMON_COMMANDS, CloseConnection
from nicos.pycompat import queue, string_types


command_wrappers = {}


def command(needcontrol=False, needscript=None, name=None):
    """Decorates a protocol command.  The `needcontrol` and `needscript`
    parameters can be set to avoid boilerplate in the handler functions.
    """
    def deco(func):
        nargsmax = func.__code__.co_argcount - 1
        nargsmin = nargsmax - len(func.__defaults__ or ())

        def wrapper(self, args):
            if not nargsmin <= len(args) <= nargsmax:
                self.send_error_reply('invalid number of arguments')
                return
            if needcontrol:
                if not self.check_control():
                    self.send_error_reply('you do not have control '
                                          'of the session')
                    return
            if needscript is True:
                if self.controller.status in (STATUS_IDLE, STATUS_IDLEEXC):
                    self.send_error_reply('no script is running')
                    return
            elif needscript is False:
                if self.controller.status not in (STATUS_IDLE, STATUS_IDLEEXC):
                    self.send_error_reply('a script is running')
                    return
            try:
                return func(self, *args)
            except CloseConnection:
                raise
            except Exception:
                self.log.exception('exception executing command %s',
                                   name or func.__name__)
                self.send_error_reply('exception occurred executing command')
        wrapper.__name__ = func.__name__
        wrapper.orig_function = func
        command_wrappers[name or func.__name__] = wrapper
        return func
    return deco


# unique objects
stop_queue = (object(), '')
no_msg = object()


class SizedQueue(queue.Queue):
    """A Queue that limits the total size of event messages"""
    def _init(self, maxsize):
        assert maxsize > 0
        self.nbytes = 0
        queue.Queue._init(self, maxsize)

    def _qsize(self):
        # limit to self.maxsize because of equality test
        # for full queues in python 2.7
        return min(self.maxsize, self.nbytes)

    def _put(self, item):
        # size of the queue item should never be zero, so add one
        self.nbytes += len(item[1]) + 1
        self.queue.append(item)

    def _get(self):
        item = self.queue.popleft()
        self.nbytes -= len(item[1]) + 1
        return item


class ConnectionHandler(object):
    """Protocol-unaware connection handler.

    This is used as a mixin base class for ServerTransport subclasses to
    implement a specific protocol.

    Command methods must be decorated with the `@command` decorator; it
    registers the command for dispatching and avoids boilerplate: if the
    `needcontrol` argument is True, the command will need to be called in the
    controlling session.  If the `needscript` argument is True or False, the
    command can only be called if a script is running or not running,
    respectively.
    """

    def __init__(self, daemon):
        self.daemon = daemon
        self.controller = daemon._controller
        # limit memory usage to 100 Megs
        self.event_queue = SizedQueue(100*1024*1024)
        self.event_mask = set()
        self.log = LoggerWrapper(self.daemon.log,
                                 '[handler #%s] ' % self.ident)

    def close(self):
        try:
            self.event_queue.put(stop_queue, False)
        except queue.Full:
            # the event queue has already overflown because the event sender
            # was already closed; so we can ignore this
            pass

    def check_host(self):
        """Match the connecting host against the daemon's list of
        trusted hosts.
        """
        for allowed in self.daemon.trustedhosts:
            for possible in self.clientnames:
                if allowed == possible:
                    return
        self.send_error_reply('permission denied')
        self.log.error('login attempt from untrusted host: %s',
                       self.clientnames)
        raise CloseConnection

    def check_control(self):
        """Check if the current thread is the session's controlling thread."""
        he = self.controller.controlling_user
        me = self.user
        if self.user.level == ADMIN:
            # admin may do anything
            return True
        if he is None:
            self.controller.controlling_user = me
            return True
        if he.level > me.level:
            # user is not controlling, and currently controlling
            # user has higher priority
            return False
        # controlling user has same or lower priority (may be the same user)
        return True

    def handle(self):
        """Handle a single connection."""
        self.log.info('connection from %s', self.clientnames)

        # check trusted hosts list, if nonempty
        if self.daemon.trustedhosts:
            self.check_host()

        authenticators, hashing = self.daemon.get_authenticators()
        if rsa is not None:
            pubkey, privkey = rsa.newkeys(512)
            pubkeyStr = base64.encodestring(pubkey.save_pkcs1())
            bannerhashing = 'rsa,%s' % hashing
        else:
            pubkeyStr = ''
            bannerhashing = hashing

        # announce version and authentication modality
        self.send_ok_reply(dict(
            daemon_version = nicos_version,
            custom_version = custom_version,
            nicos_root = config.nicos_root,
            custom_path = config.custom_path,
            pw_hashing = bannerhashing,
            rsakey = pubkeyStr,
            protocol_version = self.get_version(),
        ))

        # read login credentials
        cmd, credentials = self.recv_command()
        if cmd != 'authenticate' or len(credentials) != 1 or \
           not isinstance(credentials[0], dict) or \
           not all(v in credentials[0] for v in ('login', 'passwd')):
            self.log.error('invalid login: %r, credentials=%r',
                           cmd, credentials)
            self.send_error_reply('invalid credentials')
            raise CloseConnection

        password = credentials[0]['passwd']
        if password[0:4] == 'RSA:':
            password = password[4:]
            password = rsa.decrypt(base64.decodestring(password.encode()),
                                   privkey)
            if hashing == 'sha1':
                password = hashlib.sha1(password).hexdigest()
            elif hashing == 'md5':
                password = hashlib.md5(password).hexdigest()

        # check login data according to configured authentication
        login = credentials[0]['login']
        self.log.info('auth request from login %r', login)
        if authenticators:
            auth_err = None
            for auth in authenticators:
                try:
                    self.user = auth.authenticate(login, password)
                    break
                except AuthenticationError as err:
                    auth_err = err  # Py3 clears "err" after the except block
                    continue
            else:  # no "break": all authenticators failed
                self.log.error('authentication failed: %s', auth_err)
                self.send_error_reply('credentials not accepted')
                raise CloseConnection
        else:
            self.user = User(login, ADMIN)

        # acknowledge the login
        self.log.info('login succeeded, access level %d', self.user.level)
        self.send_ok_reply(dict(
            user_level = self.user.level,
        ))

        # start main command loop
        while 1:
            command, data = self.recv_command()
            command_wrappers[command](self, data)

    # -- Event thread entry point ---------------------------------------------

    def event_sender(self):
        """Take events from the handler instance's event queue and send them
        to the client.
        """
        self.log.info('event sender started')
        queue_get = self.event_queue.get
        event_mask = self.event_mask
        while 1:
            item = queue_get()
            if item is stop_queue:
                break
            event, data = item
            if event in event_mask:
                continue
            try:
                self.send_event(event, data)
            except socket.timeout:
                # XXX move socket specific error handling to transport
                self.log.error('send timeout in event sender')
                break
            except socket.error as err:
                self.log.warning('connection broken in event sender: %s', err)
                break
            except Exception as err:
                self.log.exception('exception in event sender; event: %s, '
                                   'data: %s', event, repr(data)[:1000])
        self.log.info('closing connections from event sender')
        self.close()

    # -- Script control commands ----------------------------------------------

    @command(needscript=False)
    def start(self, name, code):
        """Start a script within the script thread.

        Same as queue(), but will reject the command if a script is running.
        """
        self.queue(name, code)

    @command()
    def queue(self, name, code):
        """Start a script, or queue it if the script thread is busy.

        :param name: name of the script (usually the filename) or ''
        :param code: code of the script
        :returns: ok or error
        """
        if not name:
            name = None
        try:
            reqid = self.controller.new_request(
                ScriptRequest(code, name, self.user, handler=self))
        except RequestError as err:
            self.send_error_reply(str(err))
            return
        # take control of the session
        self.controller.controlling_user = self.user
        self.send_ok_reply(reqid)

    @command()
    def unqueue(self, reqid):
        """Mark the given request ID (or all, if '*') so that it is not
        executed.

        :param reqid: (str) request UUID, or '*'
        :returns: ok or error (e.g. if the given script is not in the queue)
        """
        if reqid == '*':
            self.controller.block_all_requests()
        else:
            try:
                self.controller.block_requests([reqid])
            except IndexError:
                self.send_error_reply('script already executing')
                return
        self.send_ok_reply(None)

    @command(needcontrol=True, needscript=True)
    def update(self, newcode, reason, reqid=None):
        """Update the currently running script.

        :param newcode: new code for the current script
        :param reason: user-specified reason for the update
        :returns: ok or error (e.g. if the script differs in executing code)
        """
        try:
            self.controller.update_script(reqid, newcode, reason, self.user)
        except ScriptError as err:
            self.send_error_reply(str(err))
            return
        except IndexError:
            self.sed_error_reply('script doesn\'t exist')
            return
        self.send_ok_reply(None)

    @command(needcontrol=True, needscript=True, name='break')
    def break_(self, level):
        """Pause the current script at the next breakpoint.

        :param level: (int) stop level of breakpoint, constants are defined in
           `nicos.protocols.daemon`:

           * BREAK_AFTER_LINE - pause after current scan/line in the script
           * BREAK_AFTER_STEP - pause after scanpoint/breakpoint with level "2"
           * BREAK_NOW - pause in the middle of counting
        :returns: ok or error (e.g. if script is already paused)
        """
        level = int(level)
        if self.controller.status == STATUS_STOPPING:
            self.send_error_reply('script is already stopping')
        elif self.controller.status == STATUS_INBREAK:
            self.send_error_reply('script is already paused')
        else:
            session.log.info('Pause requested by %s', self.user.name)
            self.controller.set_break(('break', level, self.user.name))
            if level >= BREAK_NOW:
                session.countloop_request = ('pause',
                                             'Paused by %s' % self.user.name)
            self.log.info('script pause request')
            self.send_ok_reply(None)

    @command(needcontrol=True, needscript=True, name='continue')
    def continue_(self):
        """Continue the paused script.

        :returns: ok or error (e.g. if script is not paused)
        """
        if self.controller.status == STATUS_STOPPING:
            self.send_error_reply('could not continue script')
        elif self.controller.status == STATUS_RUNNING:
            self.send_error_reply('script is not paused')
        else:
            self.log.info('script continue request')
            self.controller.set_continue(('continue', 0, self.user.name))
            self.send_ok_reply(None)

    @command(needcontrol=True, needscript=True)
    def stop(self, level):
        """Abort the paused script.

        :param level: (int) stop level, constants are defined in
           `nicos.protocols.daemon`:

           * BREAK_AFTER_LINE - stop after current scan/line in the script
           * BREAK_AFTER_STEP - stop after scan point/breakpoint with level "2"
           * BREAK_NOW - stop in the middle of counting (but due to the special
             way the breakpoint while counting is implemented, it will
             actually just stop there if paused before, otherwise this is
             equivalent to level '2')
        :returns: ok or error
        """
        level = int(level)
        self.log.info('script stop request')
        self.controller.script_stop(level, self.user)
        self.send_ok_reply(None)

    # note: name finish() is already defined by BaseRequestHandler
    @command(name='finish', needcontrol=True, needscript=True)
    def finish_(self):
        """Finish the currently running action early and proceed.

        Currently, the only action that can be finished early is a count().

        :returns: ok or error
        """
        self.log.info('measurement finish request')
        if self.controller.status == STATUS_STOPPING:
            self.send_error_reply('script is stopping')
        else:
            session.log.info('Early finish requested by %s', self.user.name)
            session.countloop_request = \
                ('finish', 'Finished early by %s' % self.user.name)
        self.send_ok_reply(None)

    @command()
    def emergency(self):
        """Stop the script unconditionally and run emergency stop functions.

        This throws an exception into the thread running the script, so that
        the script is interrupted as soon as possible.  However, finalizers
        with "try-finally" are still run and can e.g. record count results.

        :returns: ok or error
        """
        if self.controller.status in (STATUS_IDLE, STATUS_IDLEEXC):
            self.log.warning('immediate stop without script running')
        else:
            self.log.warning('immediate stop request in %s',
                             self.controller.current_location(True))
        self.controller.script_immediate_stop(self.user)
        self.send_ok_reply(None)

    @command()
    def rearrange(self, ids):
        """Try to re-sort the queued scripts according to the given sequence of
        their IDs.

        :param ids: a list of request IDs that gives the new ordering

        :returns: ok or error
        """
        try:
            self.controller.rearrange_queue(ids)
        except RequestError as err:
            self.send_error_reply(str(err))
        else:
            self.send_ok_reply(None)

    # -- Asynchronous script interaction --------------------------------------

    @command(needcontrol=True, name='exec')
    def exec_(self, cmd):
        """Execute a Python statement in the context of the running script.

        :param cmd: Python statement
        :returns: ok or error (it is not an error if the script itself raised
           an exception)
        """
        if self.controller.status == STATUS_STOPPING:
            self.send_error_reply('script is stopping')
            return
        self.log.debug('executing command in script context\n%s', cmd)
        try:
            self.controller.exec_script(cmd, self.user, self)
        except Exception:
            session.logUnhandledException(cut_frames=0)
        self.send_ok_reply(None)

    @command()
    def eval(self, expr, stringify):
        """Evaluate and return an expression.

        :param expr: Python expression
        :param stringify: (bool) if True, return the `repr` of the result
        :returns: result of evaluation or an error if exception raised
        """
        self.log.debug('evaluating expression in script context\n%s', expr)
        try:
            retval = self.controller.eval_expression(expr, self, stringify)
        except Exception as err:
            self.log.exception('exception in eval command')
            self.send_error_reply('exception raised while evaluating: %s' % err)
        else:
            self.send_ok_reply(retval)

    @command()
    def simulate(self, name, code, uuid=None):
        """Simulate a named script by forking into simulation mode.

        :param name: name of the script (typically the filename)
        :param code: code of the script
        :param prefix: prefix string for the log output of the simulation
           process
        :returns: ok or error (e.g. if simulation is not possible)
        """
        self.log.debug('running simulation\n%s', code)
        try:
            self.controller.simulate_script(uuid, code,
                                            name or None, self.user)
        except SPMError as err:
            self.send_error_reply('syntax error in script: %s' % err)
        except Exception as err:
            self.log.exception('exception in simulate command')
            self.send_error_reply('exception raised running simulation: %s' % err)
        else:
            self.send_ok_reply(None)

    @command()
    def complete(self, line, lastword):
        """Get completions for the given prefix.

        :param line: the whole entered line
        :param lastword: the last word of the line
        :returns: list of matches
        """
        matches = sorted(set(self.controller.complete_line(line, lastword)))
        self.send_ok_reply(matches)

    # -- Runtime information commands -----------------------------------------

    @command()
    def getversion(self):
        """Return the daemon's version.

        :returns: version string
        """
        self.send_ok_reply(nicos_version)

    @command()
    def getstatus(self):
        """Return all important status info.

        :returns: dict of status info with the following entries:

           status
              tuple of (status constant, line number)
           script
              current script or ''
           watch
              dict of current watch expressions
           requests
              current request queue (list of serialized requests)
           mode
              current mode of the session as a string ('master', 'slave', ...)
           setups
              tuple of (current loaded setups, explicitly loaded setups)
           devices
              list of names of all existing devices
        """
        current_script = self.controller.current_script
        request_queue = self.controller.get_queue()
        eta = (current_script.simstate, current_script.eta) if current_script \
            else (SIM_STATES['pending'], 0)
        self.send_ok_reply(dict(
            status   = (self.controller.status, self.controller.lineno),
            script   = current_script and current_script.text or '',
            eta      = eta,
            watch    = self.controller.eval_watch_expressions(),
            requests = request_queue,
            mode     = session.mode,
            setups   = (list(session.loaded_setups),
                        session.explicit_setups),
            devices  = list(session.devices),
        ))

    @command()
    def getmessages(self, n):
        """Return the last *n* messages.

        :param n: number of messages to transfer or '*' for all messages
        :returns: list of messages (each message being a list of logging
           fields)
        """
        if n == '*':
            self.send_ok_reply(self.daemon._messages)
        else:
            self.send_ok_reply(self.daemon._messages[-int(n):])

    @command()
    def getscript(self):
        """Return the current script text, or an empty string.

        :returns: code of the current script
        """
        current_script = self.controller.current_script
        self.send_ok_reply(current_script and current_script.text or '')

    @command()
    def gethistory(self, key, fromtime, totime):
        """Return history of a cache key, if available.

        :param key: cache key (without prefix) to query history
        :param fromtime: start time as Unix timestamp
        :param totime: end time as Unix timestamp
        :returns: list of (time, value) tuples
        """
        if not session.cache:
            self.send_ok_reply([])
        history = session.cache.history('', key, float(fromtime),
                                        float(totime))
        self.send_ok_reply(history)

    @command()
    def getcachekeys(self, query):
        """Return a cache key query result, if available.

        XXX document this better

        :param query: input query
        :returns: list of (time, value) tuples
        """
        if not session.cache:
            self.send_ok_reply([])
            return
        if ',' in query:
            result = session.cache.query_db(query.split(','))
        else:
            result = session.cache.query_db(query)
        self.send_ok_reply(result)

    @command()
    def gettrace(self):
        """Return current execution status as a stacktrace.

        :returns: stack trace as a string
        """
        self.send_ok_reply(self.controller.current_location(True))

    # -- Watch expression commands --------------------------------------------

    @command(needcontrol=True)
    def watch(self, vallist):
        """Add watch expressions.

        :param vallist: list of expressions to add
        :returns: ack or error
        """
        if not isinstance(vallist, list):
            self.send_error_reply('wrong argument type for add_values: %s' %
                                  vallist.__class__.__name__)
            return
        for val in vallist:
            if not isinstance(val, string_types):
                self.send_error_reply('wrong type for add_values item: %s' %
                                      val.__class__.__name__)
                return
            if ':' not in val:
                val += ':default'
            self.controller.add_watch_expression(val)
        self.send_ok_reply(None)

    @command(needcontrol=True)
    def unwatch(self, vallist):
        """Delete watch expressions.

        :param vallist: list of expressions to remove, or ['*'] to remove all
        :returns: ack or error
        """
        if not isinstance(vallist, list):
            self.send_error_reply('wrong argument type for del_values: %s' %
                                  vallist.__class__.__name__)
            return
        for val in vallist:
            if not isinstance(val, string_types):
                self.send_error_reply('wrong type for del_values item: %s' %
                                      val.__class__.__name__)
                return
            if ':' not in val:
                val += ':default'
            if val.startswith('*:'):
                group = val[val.find(':'):]
                self.controller.remove_all_watch_expressions(group)
            else:
                self.controller.remove_watch_expression(val)
        self.send_ok_reply(None)

    # -- Data interface commands ----------------------------------------------

    @command()
    def getdataset(self, index):
        """Get one or more datasets.

        :param index: (int) index of the dataset or '*' for all datasets
        :returns: a list of datasets if index is '*', or a single dataset
           otherwise; or None if the dataset does not exist
        """
        if index == '*':
            try:
                self.send_ok_reply([ScanData(s)
                                    for s in session.data._last_scans])
            # session.experiment may be None or a stub
            except (AttributeError, ConfigurationError):
                self.send_ok_reply(None)
        else:
            index = int(index)
            try:
                dataset = ScanData(session.data._last_scans[index])
                self.send_ok_reply(dataset)
            except (IndexError, AttributeError, ConfigurationError):
                self.send_ok_reply(None)

    # -- Miscellaneous commands -----------------------------------------------

    @command(needcontrol=True)
    def debug(self, code):
        """Start a pdb session in the script thread context.  Experimental!

        The daemon is put into debug mode.  Replies to pdb queries can be given
        using the "debuginput" command.  Stopping the debugging (with "q" at
        the pdb prompt or finishing the script) will exit debug mode.

        :param code: code to start in debug mode
        :returns: ack or error
        """
        if self.controller.status in (STATUS_IDLE, STATUS_IDLEEXC):
            if not code:
                self.send_error_reply('no piece of code to debug given')
                return
            req = ScriptRequest(code, '', self.user, handler=self)
            self.controller.debug_start(req)
        else:
            if code:
                self.send_error_reply('code to debug given, but a '
                                      'script is already running')
                return
            self.controller.debug_running()
        self.send_ok_reply(None)

    @command(needcontrol=True, needscript=True)
    def debuginput(self, line):
        """Feed input lines to pdb.

        :param line: input to pdb
        :returns: ack or error
        """
        self.controller.debug_input(line)
        self.send_ok_reply(None)

    @command()
    def eventmask(self, events):
        """Disable sending of certain events to the client.

        :param events: a serialized list of event names
        :returns: ack
        """
        self.event_mask.update(events)
        self.send_ok_reply(None)

    @command()
    def eventunmask(self, events):
        """Enable sending of certain events to the client.

        :param events: a serialized list of event names
        :returns: ack
        """
        self.event_mask.difference_update(events)
        self.send_ok_reply(None)

    @command()
    def transfer(self, content):
        """Transfer a file to the server, encoded in base64.

        :param content: file content encoded with base64
        :returns: file name
        """
        fd, filename = tempfile.mkstemp(prefix='nicos')
        try:
            os.write(fd, content)
        finally:
            os.close(fd)
        self.send_ok_reply(filename)

    @command(needcontrol=True)
    def unlock(self):
        """Give up control of the session.

        :returns: ack
        """
        self.controller.controlling_user = None
        self.send_ok_reply(None)

    @command()
    def quit(self):
        """Close the session.

        :returns: ack and closes the connection
        """
        if self.controller.controlling_user is self.user:
            self.controller.controlling_user = None
        self.log.info('disconnect')
        self.send_ok_reply(None)
        raise CloseConnection

    @command()
    def authenticate(self, data):
        """Authenticate the client.

        This command may only be used during handshake.
        """
        raise CloseConnection


# make sure we handle all protocol defined commands
for cmd in DAEMON_COMMANDS:
    if cmd not in command_wrappers:
        raise RuntimeError('Daemon command %s not handled by server!' % cmd)
