#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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
# *****************************************************************************

"""
The connection handler for the execution daemon, handling the protocol commands.
"""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import os
import zlib
import errno
import socket
import struct
import cPickle as pickle
from Queue import Queue
from SocketServer import BaseRequestHandler

from nicm import nicm_version
from nicm.daemon.util import LoggerWrapper
from nicm.daemon.pyctl import STATUS_IDLE, STATUS_RUNNING, \
     STATUS_STOPPING, STATUS_INBREAK
from nicm.daemon.script import EmergencyStopRequest, ScriptRequest, \
     ScriptError, RequestError


# nicosd response constants (XXX remove NICOSD prefix)
EOF = '\x04'
OK = "NICOSD OK\n"
BYE = "BYE...\n"
WARN = "NICOSD WARNING: "
ERROR = "NICOSD ERROR: "

WRITE_CHUNKSIZE = 8192
READ_BUFSIZE = 4096

lengthheader = struct.Struct('>I')

_queue_freelist = [Queue() for i in range(5)]


class CloseConnection(Exception):
    """Raised to unconditionally close the connection."""

licos_commands = {}

def command(needcontrol=False, needscript=None, deprecated=False):
    """
    Decorates a nicosd protocol command.  The `needcontrol` and `needscript`
    parameters can be set to avoid boilerplate in the handler functions.
    """
    def deco(func):
        def wrapper(self):
            if needcontrol:
                if not self.check_control():
                    return
            if needscript is True:
                if self.controller.status == STATUS_IDLE:
                    self.write(WARN, 'no script is running')
                    return
            elif needscript is False:
                if self.controller.status != STATUS_IDLE:
                    self.write(WARN, 'a script is running')
                    return
            try:
                return func(self)
            except CloseConnection:
                raise
            except Exception:
                self.log.exception('exception executing command %s' %
                                   func.__name__)
                self.write(ERROR, 'exception occurred executing command')
        wrapper.__name__ = func.__name__
        licos_commands[func.__name__] = wrapper
        return wrapper
    return deco

stop_queue = object()

# XXX redesign protocol

class ConnectionHandler(BaseRequestHandler):
    """
    This class is the SocketServer "request handler" implementation for the
    licos server.  One instance of this class is created for every control
    connection (not event connections) from a client.  When the event connection
    is opened, the `event_sender` method of the existing instance is spawned as
    a new thread.

    The `handle` method reads commands from the client, dispatches them to
    methods of the same name, and writes the responses back.

    Command methods must be decorated with the `@command` decorator; it
    registers the command for dispatching and avoids boilerplate: if the
    `needcontrol` argument is True, the command will need to be called in the
    controlling session.  If the `needscript` argument is True or False, the
    command can only be called if a script is running or not running,
    respectively.

    Note that the SocketServer interface is such that the request handling is
    done while the constructor runs, i.e. the `__init__` method calls `handle`.
    """

    def __init__(self, request, client_address, server):
        # HACK: the Queue constructor does an import of threading, therefore
        # constructing one here will lock the import system, which leads to
        # clients freezing on login while the startup modules are imported
        try:
            self.event_queue = _queue_freelist.pop()
        except IndexError:
            self.event_queue = Queue()
        # bind often used daemon attributes to self
        self.daemon = server.daemon
        self.controller = server.daemon._controller
        # register self as a new handler
        server.register_handler(self, client_address[0])
        self.sock = request
        self.log = LoggerWrapper(self.daemon._log,
                                 '[handler #%d] ' % self.ident)
        # read buffer
        self._buffer = ''
        # gzip responses?
        self.gzip = False
        # protocol level
        self.proto = 0
        try:
            # this calls self.handle()
            BaseRequestHandler.__init__(self, request, client_address, server)
        except CloseConnection:
            pass
        except Exception:
            self.log.exception('unhandled exception')
        self.event_queue.put(stop_queue)
        server.unregister_handler(self.ident)

    def write(self, prefix, msg=None):
        """Write a message to the client."""
        if msg is None:
            towrite = prefix + EOF
        else:
            towrite = prefix + msg + '\n' + EOF
        if self.gzip:
            towrite = zlib.compress(towrite[:-1])
            towrite = lengthheader.pack(len(towrite)) + towrite
        try:
            pos = 0
            max = len(towrite)
            while pos < max:
                str = towrite[pos:pos+WRITE_CHUNKSIZE]
                pos += WRITE_CHUNKSIZE
                if self.sock.send(str) != len(str):
                    self.log.error('write: connection broken')
                    raise CloseConnection
        except socket.error, err:
            self.log.error('write: connection broken %s' % err)
            raise CloseConnection

    def read(self):
        """Read a message from the client until "EOF"."""
        msg = ''
        while 1:
            msgpart, eof, self._buffer = self._buffer.partition(EOF)
            msg += msgpart
            if eof == EOF:
                return msg
            try:
                self._buffer = self.sock.recv(READ_BUFSIZE)
                if not self._buffer:
                    self.log.error('read: connection broken')
                    raise CloseConnection
            except socket.error, err:
                self.log.error('read: connection broken %s' % err)
                raise CloseConnection

    def check_host(self):
        """Match the connecting host against the daemon's trusted hosts list."""
        for allowed in self.daemon.trustedhosts:
            for possible in self.clientnames:
                if allowed == possible:
                    return
        self.write(ERROR, 'permission denied')
        self.log.error('login attempt from untrusted host: %s', self.clientnames)
        raise CloseConnection

    def check_control(self):
        """Check if the current thread is the session's controlling thread."""
        he = self.controller.controlling_user
        me = self.user[0]
        if self.user[2]:
            # admin may do anything
            return True
        if he is None:
            self.controller.controlling_user = me
            return True
        elif he != me:
            self.write(WARN, 'you do not have control of the session')
            return False
        return True

    def handle(self):
        """Handle a single connection."""
        host, aliases, addrlist = socket.gethostbyaddr(self.client_address[0])
        self.clientnames = [host] + aliases + addrlist
        self.log.debug('connection from %s', self.clientnames)

        # check trusted hosts list, if nonempty
        if self.daemon.trustedhosts:
            self.check_host()

        # get and export the DISPLAY
        try:
            self.write('display')
            self.display = self.read()
        except:
            self.log.error('invalid login: could not get DISPLAY var from %s',
                           self.clientnames)
            self.write(ERROR, 'could not get DISPLAY var')
            raise
        # XXX only works for the client that logged in last
        os.environ['DISPLAY'] = self.display

        # now, check login data (if config.passwd is an empty list, no login
        # control is done and everybody may log in)
        self.log.info('login attempt from %s', self.clientnames)
        self.write('login: ')
        login = self.read()
        self.write('passwd: ')
        passw = self.read()
        if self.daemon.passwd:
            for entry in self.daemon.passwd:
                if entry[0] == login:
                    self.user = entry
                    break
            else:
                self.log.warning('invalid login name: %s', login)
                self.write(WARN, 'Invalid login')
                raise CloseConnection
            if passw != self.user[1]:
                self.log.warning('invalid password from user %s', login)
                self.write(WARN, 'Invalid passwd')
                raise CloseConnection
        else:
            self.user = [login, passw, True]
        self.log.info('login succeeded: user %s, display %s',
                      login, self.display)
        self.write(OK)

        # start main command loop
        while 1:
            command = self.read()
            if command not in licos_commands:
                self.log.warning('got unknown command: %s', command)
                self.write(WARN, 'unknown command')
                continue
            licos_commands[command](self)

    def serialize(self, data):
        """Serialize an object according to the selected protocol."""
        return pickle.dumps(data).replace('\n', '\xff')

    def unserialize(self, data):
        """Unserialize an object according to the selected protocol."""
        return pickle.loads(data.replace('\xff', '\n'))

    # -- Event thread entry point ----------------------------------------------

    def event_sender(self, sock):
        """Take events from the handler instance's event queue and send them
        to the client using the event connection.
        """
        self.log.info('event sender started')
        queue_get = self.event_queue.get
        while 1:
            item = queue_get()
            if item is stop_queue:
                break
            event, data = item
            try:
                sock.send('%s %s\n' % (event, self.serialize(data)))
            except Exception, err:
                if isinstance(err, socket.error) and err.args[0] == errno.EPIPE:
                    # close sender on broken pipe
                    self.log.warning('broken pipe in event sender')
                    break
                self.log.exception('exception in event sender; '
                                   'event: %s, data: %r', event, data)
        self.log.debug('closing event connection')
        sock.close()

    # -- Daemon interface commands ---------------------------------------------

    @command()
    def set_gzip(self):
        """Order the daemon to gzip all responses."""
        self.write(OK)
        self.gzip = True

    # -- Script control commands ------------------------------------------------

    @command(needcontrol=False, needscript=False)
    def start_prg(self):
        """Start a script within the script thread."""
        self.write(OK)
        script_text = self.read()
        try:
            self.controller.new_request(ScriptRequest(script_text))
        except RequestError, err:
            self.write(WARN, str(err))
            return
        # take control of the session
        self.controller.controlling_user = self.user[0]
        self.write(OK)

    @command(needcontrol=False, needscript=False)
    def start_named_prg(self):
        """Start a named script within the script thread."""
        self.write(OK)
        script_name = self.read()
        if script_name == 'None':
            script_name = None
        self.write(OK)
        script_text = self.read()
        try:
            self.controller.new_request(ScriptRequest(script_text, script_name))
        except RequestError, err:
            self.write(WARN, str(err))
            return
        # take control of the session
        self.controller.controlling_user = self.user[0]
        self.write(OK)

    @command(needcontrol=False)
    def queue_named_prg(self):
        """Start a named script, or queue it if the script thread is busy."""
        self.write(OK)
        script_name = self.read()
        if script_name == 'None':
            script_name = None
        self.write(OK)
        script_text = self.read()
        try:
            self.controller.new_request(ScriptRequest(script_text, script_name))
        except RequestError, err:
            self.write(WARN, str(err))
            return
        self.write(OK)

    @command(needcontrol=True, needscript=True)
    def update_prg(self):
        """Update the currently running script."""
        self.write(OK)
        script_text = self.read()
        try:
            self.controller.current_script.update(script_text,
                                                  self.controller)
        except ScriptError, err:
            self.write(WARN, str(err))
            return
        self.write(OK)

    @command(needcontrol=True, needscript=True)
    def break_prg(self):
        """Interrupt the current script."""
        if self.controller.status == STATUS_STOPPING:
            self.write(WARN, 'script is already stopping')
        elif self.controller.status == STATUS_INBREAK:
            self.write(WARN, 'script is already interrupted')
        else:
            self.controller.set_break(None)
            self.log.info('script interrupt request')
            #time.sleep(0.01)
            self.write(OK)

    @command(needcontrol=True, needscript=True)
    def cont_prg(self):
        """Continue the interrupted script."""
        if self.controller.status == STATUS_STOPPING:
            self.write(WARN, 'could not continue script')
        elif self.controller.status == STATUS_RUNNING:
            self.write(WARN, 'script is not interrupted')
        else:
            self.log.info('script continue request')
            self.controller.set_continue(stop=False)
            self.write(OK)

    @command(needcontrol=True, needscript=True)
    def stop_prg(self):
        """Abort the interrupted script."""
        if self.controller.status == STATUS_STOPPING:
            self.write(OK)
        elif self.controller.status == STATUS_RUNNING:
            self.log.info('script stop request while running')
            self.controller.set_break('stop')
            self.write(OK)
        else:
            self.log.info('script stop request while in break')
            self.controller.set_continue(stop='stop')
            self.write(OK)

    @command(needcontrol=True)
    def emergency_stop(self):
        """Stop the script unconditionally and run emergency stop functions."""
        if self.controller.status == STATUS_IDLE:
            # only execute emergency stop functions
            self.log.warning('emergency stop without script running')
            self.controller.new_request(EmergencyStopRequest())
            self.write(OK)
            return
        elif self.controller.status == STATUS_STOPPING:
            self.write(OK)
            return
        self.log.warning('emergency stop request in %s',
                         self.controller.current_location(True))
        if self.controller.status == STATUS_RUNNING:
            self.controller.set_stop('emergency stop')
        else:
            # in break
            self.controller.set_continue(stop='emergency stop')
        self.write(OK)

    @command()
    def unqueue_prg(self):
        """Mark the given request number so that it is not executed."""
        self.write(OK)
        reqno = self.read()
        try:
            reqno = int(reqno)
            if reqno <= self.controller.reqno_work:
                raise ValueError('script already executing')
            # XXX: notify other clients
            self.controller.blocked_reqs.add(reqno)
        except Exception, err:
            self.write(WARN, 'reading reqno failed: %s' % err)
        else:
            self.write(OK)

    @command()
    def unqueue_all_prgs(self):
        """Mark all scripts not yet executed as blocked."""
        # XXX: notify other clients
        self.controller.blocked_reqs.update(
            range(self.controller.reqno_work + 1,
                  self.controller.reqno_latest + 1))
        self.write(OK)

    # -- Asynchronous script interaction ---------------------------------------

    @command(needcontrol=True, needscript=True)
    def exec_cmd(self):
        """Execute a Python statement in the context of the running script."""
        if self.controller.status == STATUS_STOPPING:
            self.write(WARN, 'script is stopping')
            return
        self.write(OK)
        cmd = self.read()
        try:
            self.log.info('executing command in script context\n%s', cmd)
            self.controller.exec_script(cmd)
        except Exception, err:
            self.log.exception('exception in exec_cmd command')
            self.write(WARN, 'exception raised while executing cmd: %s' % err)
        else:
            self.write(OK)

    # -- Runtime information commands ------------------------------------------

    @command()
    def get_version(self):
        """Return the daemon's version."""
        self.write('nicosd version: %s (licosd), '
                   'supports protocol 1' % nicm_version)

    @command()
    def get_all_status(self):
        """Return all important status info."""
        current_script = self.controller.current_script
        self.write(self.serialize(
                ((self.controller.status, self.controller.lineno),
                 current_script and current_script.text or '',
                 self.daemon._messages,
                 self.controller.eval_watch_expressions()
                 )))

    # -- Watch expression commands ---------------------------------------------

    @command()
    def get_value(self):
        """Evaluate and return a watch expression."""
        self.write(OK)
        expr = self.read().partition(':')[0]
        self.write(self.serialize(self.controller.eval_expression(expr)))

    @command(needcontrol=True)
    def add_values(self):
        """Add watch expressions."""
        self.write(OK)
        vallist = self.unserialize(self.read())
        if not isinstance(vallist, list):
            self.write(WARN, 'wrong argument type for add_values: %s' %
                       vallist.__class__.__name__)
            return
        for val in vallist:
            if not isinstance(val, str):
                self.write(WARN, 'wrong type for add_values item: %s' %
                           val.__class__.__name__)
                return
            if ':' not in val:
                val += ':default'
            self.controller.add_watch_expression(val)
        self.write(OK)

    @command(needcontrol=True)
    def del_values(self):
        """Delete watch expressions."""
        self.write(OK)
        vallist = self.unserialize(self.read())
        if not isinstance(vallist, list):
            self.write(WARN, 'wrong argument type for del_values: %s' %
                       vallist.__class__.__name__)
            return
        for val in vallist:
            if not isinstance(val, str):
                self.write(WARN, 'wrong type for del_values item: %s' %
                           val.__class__.__name__)
                return
            if ':' not in val:
                val += ':default'
            if val.startswith('*:'):
                group = val[val.find(':'):]
                self.controller.remove_all_watch_expressions(group)
            else:
                self.controller.remove_watch_expression(val)
        self.write(OK)

    # -- Data interface commands -----------------------------------------------

    @command()
    def get_dataset(self):
        """Get the whole current dataset, including curves."""
        data = self.daemon._data_handler
        if data.active_dataset:
            self.write(self.serialize(data.active_dataset.tolist()))
        else:
            self.write(self.serialize(None))

    @command()
    def get_datasets(self):
        """Get all datasets, including curves."""
        data = self.daemon._data_handler
        self.write(self.serialize(data.tolist()))

    # -- Miscellaneous commands ------------------------------------------------

    @command(needcontrol=True)
    def unlock_control(self):
        """Give up control of the session."""
        self.controller.controlling_user = None

    @command(needcontrol=True, needscript=False)
    def reload_nicm(self):
        """Reload the nicm interface, starting a new script thread."""
        try:
            # stop the script thread
            self.controller.stop_script_thread()
        except RuntimeError:
            # no script thread running
            pass
        # clear sys.modules
        self.daemon._module_manager.purge()
        # purge data from data handler
        self.daemon._data_handler.purge()
        # start a new script thread, this will reimport all modules
        self.controller.start_script_thread()
        self.write(OK)

    @command()
    def exit(self):
        """Close the session."""
        me = self.user[0]
        if self.controller.controlling_user == me:
            self.controller.controlling_user = None
        self.log.info('disconnect')
        self.write(BYE)
        raise CloseConnection
