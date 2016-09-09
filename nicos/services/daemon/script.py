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

"""Thread that executes user scripts."""

import ast
import sys
import time
import weakref
import traceback
from os import path
from bdb import BdbQuit
from uuid import uuid1
from threading import Lock, Event, current_thread

from nicos import session, config
from nicos.utils import createThread
from nicos.utils.loggers import INPUT
from nicos.core.utils import system_user
from nicos.services.daemon.utils import formatScript, fixupScript, \
    updateLinecache, ScriptQueue, parseScript, splitBlocks
from nicos.services.daemon.pyctl import Controller, ControlStop
from nicos.services.daemon.debugger import Rpdb
from nicos.protocols.daemon import BREAK_AFTER_LINE, BREAK_NOW, STATUS_IDLE, \
    STATUS_IDLEEXC, STATUS_RUNNING, STATUS_INBREAK, STATUS_STOPPING, SIM_STATES
from nicos.core.sessions.utils import NicosCompleter
from nicos.core import SIMULATION, SLAVE, MASTER
from nicos.pycompat import exec_


class RequestError(Exception):
    """Exception raised if a request cannot be queued."""


class Request(object):
    """
    Abstract Request class.

    The server communicates with the script thread via Requests.  Each request
    is put onto a queue, which the script thread processes sequentially.  A
    request can be for script execution, but also for termination of the script
    thread.  Each request has a number, by which pending requests can be
    identified and ignored.
    """
    reqid = None
    quiet = False

    def __init__(self, user):
        try:
            self.user = user.name
            self.userlevel = user.level
        except AttributeError:
            raise RequestError('No valid user object supplied')
        self.reqid = str(uuid1())

    def serialize(self):
        return {'reqid': self.reqid, 'user': self.user}


class EmergencyStopRequest(Request):
    """An immediate stop request (while no script is running)."""


class ScriptError(Exception):
    """Exception raised if a script operation cannot be executed."""


class ScriptRequest(Request):
    """
    A request to execute a Python script.

    This class holds the script to execute as well, and has all operations that
    can be done with the script: execute it, and update it.
    """

    # pylint: disable=W0622
    def __init__(self, text, name=None, user=None, quiet=False,
                 settrace=None, handler=None, format=None):
        Request.__init__(self, user)
        self._run = Event()
        self._run.set()

        self.name = name
        self.quiet = quiet
        self.format = format
        # if not None, this is a set_trace function that's called first thing
        # by the controller, to immediately enter remote debugging
        self.settrace = settrace
        # a weakref to the handler of origin for this request
        self.handler = weakref.ref(handler) if handler else None
        # script text (SPM or Python commands)
        if '\n' in text and not text.endswith('\n'):
            text += '\n'
        self.text = text
        self.curblock = -1
        self.runtimes = []
        self.blockStart = -1
        self.simstate = SIM_STATES['pending']
        self.eta = -1

    def serialize(self):
        return {'reqid': self.reqid, 'name': self.name, 'script': self.text,
                'user': self.user}

    def __repr__(self):
        if self.name:
            return '%s: %r' % (self.name, self.text)
        return repr(self.text)

    def parse(self):
        self.code, self.blocks = parseScript(self.text, self.name, self.format,
                                             compilecode=True)
        # prefill runtimes with 0 so the results of the simulation can come in
        # any order
        self.resetSimstate()

    def execute(self, controller):
        """Execute the script in the given namespace, using "controller"
        to execute individual blocks.
        """
        session.scriptEvent('start', (self.name, self.text))
        session.countloop_request = None  # reset any pause flag from before
        # this is to allow the traceback module to report the script's
        # source code correctly
        updateLinecache('<script>', self.text)
        # note: checking session._experiment since using session.experiment
        # would try to create the device, which means you can't execute any
        # command when the experiment fails
        if session._experiment and session.mode == MASTER:
            session.experiment.scripts += [self.text]
            self._exp_script_index = len(session.experiment.scripts) - 1
        if self.name:
            session.elogEvent('scriptbegin', self.name)
            session.beginActionScope(path.basename(self.name))
        try:
            while self.curblock < len(self.code) - 1:
                self._run.wait()
                self.curblock += 1
                self.blockStart = time.time()
                self.emitETA(controller)
                controller.start_exec(self.code[self.curblock],
                                      controller.namespace,
                                      None,
                                      self.settrace)
        finally:
            if self.name:
                session.endActionScope()
            if session._experiment and session.mode == MASTER:
                session.experiment.scripts = session.experiment.scripts[:-1]
            if self.name:
                session.elogEvent('scriptend', self.name)

    def emitETA(self, controller):
        if self.simstate == SIM_STATES['success']:
            self.eta = self.blockStart + sum(self.runtimes[self.curblock:])

        controller.eventfunc('eta', (self.simstate, self.eta))

    def setSimstate(self, state):
        if state in SIM_STATES:
            self.simstate = SIM_STATES[state]

    def resetSimstate(self):
        self.setSimstate('pending')
        if self.blocks:
            self.runtimes = [0] * len(self.blocks)
        else:
            self.runtimes = []
        self.eta = -1

    def update(self, text, reason, controller, user):
        """Update the code with a new script.

        This method is called from a different thread than execute(),
        so we must unset the _run flag before doing anything to
        self.curblock, self.code or self.blocks.
        """
        if not self.blocks:
            raise ScriptError('cannot update single-line script')
        text = fixupScript(text)
        newcode, newblocks = splitBlocks(text)
        # stop execution after the current block
        self._run.clear()
        curblock = self.curblock  # this may be off by one
        try:
            # make sure that everything that has already been executed matches
            if curblock >= len(newblocks):
                # insufficient number of new blocks
                raise ScriptError('new script too short')
            # compare all executed blocks
            for i in range(curblock + 1):
                if not self._compare(self.blocks[i], newblocks[i]):
                    raise ScriptError('new script differs in already executed '
                                      'part of the code')
            # everything is ok, replace the script and the remaining blocks
            self.text = text
            # also set the updating user as the new user of the script
            # (but the old userlevel remains)
            self.user = user.name
            if session._experiment and session.mode == MASTER:
                scr = list(session.experiment.scripts)  # convert readonly list
                scr[self._exp_script_index] = self.text
                session.experiment.scripts = scr
            updateLinecache('<script>', text)
            self.code, self.blocks = newcode, newblocks
            self.resetSimstate()
            # let the client know of the update
            controller.eventfunc('processing', self.serialize())
            updatemsg = 'UPDATE (%s)' % reason if reason else 'UPDATE'
            session.log.log(INPUT, formatScript(self, updatemsg))
        finally:
            # let the script continue execution in any case
            self._run.set()

    def updateRuntime(self, block, time):
        try:
            self.runtimes[block] = time
        # in case a new simulation has been triggered by editing the script
        # and removing blocks
        except IndexError:
            pass

    def _compare(self, a, b):
        """Recursively compare two AST nodes for equality."""
        def inner_comp(a, b):
            if a.__class__ is not b.__class__:
                return False
            if isinstance(a, ast.AST):
                for field in a._fields:
                    aval = getattr(a, field, None)
                    bval = getattr(b, field, None)
                    if not inner_comp(aval, bval):
                        return False
                return True
            elif isinstance(a, list):
                if len(a) != len(b):
                    return False
                for aitem, bitem in zip(a, b):
                    if not inner_comp(aitem, bitem):
                        return False
                return True
            else:
                return a == b
        return inner_comp(a, b)


class ExecutionController(Controller):
    """
    The Controller object has two functions: it holds the state of the script
    thread, and it controls execution of scripts via a C trace function.

    The `script_thread_entry` method is called in a separate thread, which then
    processes the requests put into `self.queue` by the server thread.

    When `set_break` is called, execution is suspended and `_breakfunc` is
    called which waits until somebody calls `set_continue` or `set_stop`.  Since
    `break_only_in_filename` is given at creation time, a break request will
    only break when the execution frame is one from the toplevel script.

    The attributes `currentframe` and `lineno` correspond to the current
    execution frame and the current line number in the toplevel script.

    See the docstring of pyctl.Controller for more details on the inner
    working of the Controller object and the trace function.
    """

    def __init__(self, log, eventfunc, startupsetup, simmode, autosim):
        self.log = log              # daemon logger object
        self.eventfunc = eventfunc  # event emitting callback
        self.setup = startupsetup   # first setup on start
        # start in simulation mode?
        self.simmode = simmode and SIMULATION or SLAVE
        self.autosim = autosim      # simulate script when running it?

        self.queue = ScriptQueue()  # user scripts get put here
        self.current_script = None  # currently executed script
        # namespaces in which scripts execute
        self.namespace = session.namespace
        # completer for the namespaces
        self.completer = NicosCompleter(self.namespace)
        self.watchexprs = set()     # watch expressions to evaluate
        self.watchlock = Lock()     # lock for watch expression list modification
        self.estop_functions = []   # functions to run on emergency stop
        self.thread = None          # thread executing scripts
        self.reqid_work = None      # ID of the last executing request

        self.debugger = None        # currently running debugger (Rpdb)
        self.last_handler = None    # handler of current exec/eval
        # only one user or admin can issue non-read-only commands
        self.controlling_user = None
        Controller.__init__(self, break_only_in_filename='<script>')
        self.set_observer(self._observer)

    def _setup(self):
        # this code is executed as the first thing when the daemon starts
        session.handleInitialSetup(self.setup, self.simmode)
        # remove this function from the user namespace after completion
        self.namespace.pop('NicosSetup', None)

    def _observer(self, status, lineno):
        if status != STATUS_INBREAK:
            # Do not go into pause state immediately, since we will skip
            # many breakpoints if not on the highest level.
            self.eventfunc('status', (status, lineno))

    def _breakfunc(self, frame, flag):
        # check level of breakpoint reached
        fn = frame.f_code.co_filename
        if fn.startswith('<break>'):  # '<break>n' means stoplevel n
            bplevel = int(fn[7:])
        else:
            bplevel = BREAK_AFTER_LINE
        # flag is a tuple (mode, required stoplevel, user name)
        if flag[1] < bplevel or flag[0] in ('stop', 'emergency stop'):
            # don't pause/stop here...
            self.set_continue(flag)
        else:
            self.log.info('script paused in %s', self.current_location())
            session.log.info('Script paused by %s', flag[2])
            self.eventfunc('status', (STATUS_INBREAK, self.lineno))
        new_flag = self.wait_for_continue()
        # new_flag is either a flag coming from Handler.stop(), from
        # Handler.continue() or the old one from above
        if new_flag[0] == 'continue':
            # level is ignored here
            self.log.info('paused script continued')
            session.log.info('Script continued by %s', new_flag[2])
        elif new_flag[1] < bplevel:
            # didn't pause/stop here, try again on next breakpoint
            self.set_break(new_flag)
        elif new_flag[0] in ('stop', 'emergency stop'):
            # we can stop here, do it
            self.log.info('paused script now stopped: %s', new_flag)
            self.set_stop(new_flag)

    def current_location(self, verbose=False):
        frame = self.currentframe
        if verbose:
            return '\n' + ''.join(traceback.format_stack(frame))
        else:
            return traceback.format_stack(frame, 1)[0].strip()[5:]. \
                replace('\n    ', ': ')

    def new_request(self, request, notify=True):
        assert isinstance(request, Request)
        # first send the notification, otherwise the request could be processed
        # (resulting in a "processing" event) before the "request" event is
        # even sent
        if notify:
            self.eventfunc('request', request.serialize())
        # put the script on the queue (will not block)
        self.queue.put(request)
        return request.reqid

    def block_all_requests(self):
        deleted = self.queue.delete_all()
        self.eventfunc('blocked', deleted)

    def block_requests(self, requests):
        for req in requests:
            self.queue.delete_one(req)
            self.eventfunc('blocked', [req])

    def script_stop(self, level, user, message=None):
        """High-level "stop" routine."""
        if self.status == STATUS_STOPPING:
            return
        elif self.status == STATUS_RUNNING:
            self.log.info('script stop request while running')
            suffix = user.name
            if message:
                suffix += ': ' + message
            if level == BREAK_AFTER_LINE:
                session.log.info('Stop after command requested by %s', suffix)
            else:
                session.log.info('Stop requested by %s', suffix)
            self.block_all_requests()
            self.set_break(('stop', level, user.name))
            if level >= BREAK_NOW:
                session.countloop_request = ('pause',
                                             'Stopped by %s' % user.name)
        else:
            self.log.info('script stop request while in break')
            self.block_all_requests()
            self.set_continue(('stop', level, user.name))

    def script_immediate_stop(self, user, message=None):
        """High-level "immediate stop"/estop routine."""
        if self.status in (STATUS_IDLE, STATUS_IDLEEXC):
            # only execute emergency stop functions
            self.new_request(EmergencyStopRequest(user))
            return
        elif self.status == STATUS_STOPPING:
            return
        suffix = user.name
        if message:
            suffix += ': ' + message
        session.log.warn('Immediate stop requested by %s', suffix)
        self.block_all_requests()
        if self.status == STATUS_RUNNING:
            self.set_break(('emergency stop', 5, user.name))
        else:
            # in break
            self.set_continue(('emergency stop', 5, user.name))

    def get_queue(self):
        return self.queue.serialize_queue()

    def get_current_handler(self):
        # both of these attributes are weakrefs, so we have to call them to get
        # either the handler or None
        if self.last_handler:
            return self.last_handler()
        elif self.current_script and self.current_script.handler:
            return self.current_script.handler()
        return None

    def exec_script(self, code, user, handler):
        # execute code in the script namespace (this is called not from
        # the script thread, but from a handle thread)
        temp_request = ScriptRequest(code, None, user)
        temp_request.parse()
        session.log.log(INPUT, formatScript(temp_request, '---'))
        self.last_handler = weakref.ref(handler)
        try:
            for block in temp_request.code:
                exec_(block, self.namespace)
        finally:
            self.last_handler = None

    def eval_expression(self, expr, handler, stringify=False):
        self.last_handler = weakref.ref(handler)
        ns = {'session': session, 'config': config}
        ns.update(self.namespace)
        try:
            ret = eval(expr, ns)
            if stringify:
                return repr(ret)
            return ret
        except Exception as err:
            if stringify:
                return '<cannot be evaluated: %s>' % err
            return err
        finally:
            self.last_handler = None

    def simulate_script(self, uuid, code, name, user):
        req = ScriptRequest(code, name, user)
        # use a uuid provided from client
        if uuid:
            req.reqid = uuid
        self.simulate_request(req)

    def simulate_request(self, request, quiet=False):
        code, _ = parseScript(request.text, request.name, compilecode=False)
        session.runSimulation(code[0], request.reqid, wait=False,
                              quiet=quiet)

    def add_watch_expression(self, val):
        self.watchlock.acquire()
        try:
            self.watchexprs.add(val)
        finally:
            self.watchlock.release()

    def remove_watch_expression(self, val):
        self.watchlock.acquire()
        try:
            self.watchexprs.discard(val)
        finally:
            self.watchlock.release()

    def remove_all_watch_expressions(self, group):
        self.watchlock.acquire()
        try:
            for expr in self.watchexprs.copy():
                if expr.endswith(group):
                    self.watchexprs.remove(expr)
        finally:
            self.watchlock.release()

    def eval_watch_expressions(self):
        ret = {}
        self.watchlock.acquire()
        try:
            vals = list(self.watchexprs)
        finally:
            self.watchlock.release()
        for val in vals:
            try:
                expr = val.partition(':')[0]
                ret[val] = repr(eval(expr, self.namespace))
            except Exception as err:
                ret[val] = '<cannot be evaluated: %s>' % err
        return ret

    def debug_start(self, request):
        # remote debugging support: tell the Controller that we want the
        # debugger called immediately; we then wait for debugger commands from
        # the client and feed them to the Rpdb stdin queue
        self.debugger = Rpdb(self.debug_end)
        request.settrace = self.debugger.set_trace
        self.new_request(request)
        # let clients know we're debugging and expect commands via debug_input
        self.eventfunc('debugging', True)

    def debug_running(self):
        # remote debugging support of running script: set_debug() calls the
        # given set_trace during the next call to the controller's C trace
        # function, and then the debugger takes over; we then wait for debugger
        # commands from the client and feed them to the Rpdb stdin queue
        self.debugger = Rpdb(self.debug_end)
        self.set_debug(self.debugger.set_trace)
        # let clients know we're debugging and expect commands via debug_input
        self.eventfunc('debugging', True)

    def debug_input(self, line):
        # some debugger commands arrived from a client
        if self.debugger:
            self.debugger.stdin.put(line)

    def debug_end(self, tracing=True):
        # this is called by the debugger when a command such as "continue" or
        # "quit" is entered, which means that debugging is finished
        self.debugger = None
        self.eventfunc('debugging', False)
        # set our own trace function again (Pdb replaced it)
        if tracing:
            self.reset_trace()
        else:
            sys.settrace(None)

    def complete_line(self, line, lastword):
        if not session._spmode:
            return self.completer.get_matches(lastword, line)
        spmatches = session._spmhandler.complete(lastword, line)
        return [m + ' ' for m in spmatches]

    def add_estop_function(self, func, args):
        if not callable(func):
            raise TypeError('emergency stop function must be a callable')
        if not isinstance(args, tuple):
            raise TypeError('emergency stop function args must be a tuple')
        self.estop_functions.append((func, args))
        return len(self.estop_functions)

    def execute_estop(self, user):
        self.log.warn('emergency stop caught, executing ESFs')
        session.log.info('Stopping devices for immediate stop')
        # now execute emergency stop functions
        for (func, args) in self.estop_functions:
            try:
                self.log.info('executing ESF: %s%s', func, args)
                func(*args)
            except Exception:
                self.log.exception('ESF raised error')
            else:
                self.log.info('ESF finished')

    def rearrange_queue(self, ids):
        """Rearrange the queued scripts according to the given id sequence."""

        def match_ids(client_ids, queued_ids):
            """Checks consistency between the ID sequences."""
            queued_idset = set(queued_ids)
            client_idset = set(client_ids)
            if queued_idset ^ client_idset:
                if client_idset - queued_idset:
                    temp = client_idset - queued_idset
                    if set(client_ids[:len(temp)]) ^ temp:
                        raise RequestError('Inconsistency between clients '
                                           'script IDs and queued IDs')

                    # remove already executed scripts from clients id sequence
                    client_ids = client_ids[len(temp):]

                if queued_idset - client_idset:
                    temp = queued_idset - client_idset
                    if set(queued_ids[:-len(temp)]) ^ temp:
                        raise RequestError('Inconsistency between clients '
                                           'script IDs and queued IDs')

        with self.queue as qop:
            match_ids(ids, qop.get_ids())
            for new_index, script_id in enumerate(ids):
                qop.move_item(script_id, new_index)
                self.eventfunc('rearranged', qop.get_ids())

    def update_script(self, reqid, newcode, reason, user):
        """The desired update can be either for the executed script or a
        queued script.
        """
        with self.queue as qop:
            # check if currently executed script needs update
            if reqid == self.current_script.reqid or reqid is None:
                self.current_script.update(newcode, reason, self, user)
                if session.cache and self.autosim:
                    self.simulate_request(self.current_script, quiet=True)
                    self.current_script.setSimstate('running')
                return

            # update queued script with newuser and code
            qop.update(reqid, newcode, user)
            self.eventfunc('updated', qop.get_item(reqid).serialize())

    def start_script_thread(self, *args):
        if self.thread:
            raise RuntimeError('script thread already started')
        self.thread = createThread('daemon script_thread',
                                   self.script_thread_entry, args=args)

    def script_thread_entry(self):
        """The script execution thread entry point.  This thread executes setup
        code, then waits for scripts on self.queue.  The script is then
        executed in the context of self.namespace, using the controller (self)
        to watch execution.
        """
        self.log.debug('script_thread (re)started')
        session.script_thread_id = current_thread().ident
        try:
            self.namespace['NicosSetup'] = self._setup
            # and put it in the queue as the first request
            request = ScriptRequest('NicosSetup()', 'setting up NICOS',
                                    system_user, quiet=True, format='py')
            self.new_request(request, notify=False)

            while 1:
                # get a script (or other request) from the queue
                request = self.queue.get()

                if session.cache and self.autosim:
                    self.simulate_request(request, quiet=True)
                    request.setSimstate('running')
                self.reqid_work = request.reqid
                self.log.info('processing request %s', request.reqid)
                if isinstance(request, EmergencyStopRequest):
                    self.execute_estop(request.user)
                    continue
                elif not isinstance(request, ScriptRequest):
                    self.log.error('unknown request: %s', request)
                    continue
                # notify clients that we're processing this request now
                self.eventfunc('processing', request.serialize())
                # notify clients of "input"
                session.log.log(INPUT, formatScript(request))
                # parse the script and split it into blocks
                try:
                    self.current_script = request
                    self.current_script.parse()
                except Exception:
                    session.logUnhandledException(cut_frames=1)
                    continue
                try:
                    self.current_script.execute(self)
                except ControlStop as err:
                    if err.args[0] == 'emergency stop':
                        # block all pending requests (should have been done
                        # already, but to be on the safe side do it here again)
                        self.block_all_requests()
                        self.execute_estop(err.args[2])
                    else:
                        # in this case, we have already blocked all scripts
                        # queued before the "stop" command was given; scripts
                        # that are queued after that should be executed, so
                        # we don't block requests here
                        session.log.info('Script stopped by %s', err.args[2])
                except BdbQuit as err:  # pylint: disable=E0701
                    session.log.error('Script stopped through debugger')
                except Exception as err:  # pylint: disable=E0701
                    # the topmost two frames are still in the
                    # daemon, so don't display them to the user
                    # perhaps also send an error notification
                    try:
                        session.scriptEvent('exception', sys.exc_info())
                    except Exception:
                        # last resort: do not exit script thread even if we
                        # can't handle this exception
                        pass
                if self.debugger:
                    self.debug_end(tracing=False)
                session.clearActions()
                session.scriptEvent('finish', None)
        except Exception:
            self.log.exception('unhandled exception in script thread')
            session.log.error('internal error in NICOS daemon, please restart')
        finally:
            self.thread = None
