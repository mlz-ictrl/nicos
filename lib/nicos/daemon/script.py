#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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

__version__ = "$Revision$"

import sys
import time
import traceback
import __builtin__
from Queue import Queue
from threading import Lock, Event, Thread

import ast

from nicos import session
from nicos.utils.loggers import INPUT
from nicos.daemon.utils import format_exception_cut_frames, format_script, \
     fixup_script, update_linecache
from nicos.daemon.pyctl import Controller, ControlStop
from nicos.sessions.utils import NicosCompleter, guessCorrectCommand

# compile flag to activate new division
CO_DIVISION = 0x2000


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
    reqno = None

    def __init__(self, user):
        try:
            self.user = user.name
            self.userlevel = user.level
        except AttributeError:
            raise RequestError("No valid user object supplied")
    def serialize(self):
        return {'reqno': self.reqno, 'user': self.user}


class EmergencyStopRequest(Request):
    """An emergency stop request (while no script is running)."""


class ScriptError(Exception):
    """Exception raised if a script operation cannot be executed."""

class ScriptRequest(Request):
    """
    A request to execute a Python script.

    This class holds the script to execute as well, and has all operations that
    can be done with the script: execute it, and update it.
    """

    def __init__(self, text, name=None, user=None):
        Request.__init__(self, user)
        self._run = Event()
        self._run.set()

        self.name = name
        # replace bare except clauses in the code with "except Exception"
        # so that ControlStop is not caught
        self.text = fixup_script(text)
        self.curblock = -1

    def serialize(self):
        return {'reqno': self.reqno, 'name': self.name, 'script': self.text,
                'user': self.user}

    def __repr__(self):
        if self.name:
            return self.name + ':\n' + self.text
        return self.text

    def parse(self, splitblocks=True):
        if '\n' not in self.text:
            # if the script is a single line, compile it like a line
            # in the interactive interpreter, so that expression
            # results are shown
            compiler = lambda src: compile('# coding: utf-8\n' + src + '\n',
                                           '<script>', 'single', CO_DIVISION)
            self.code = [session.commandHandler(self.text, compiler)]
            self.blocks = None
        elif sys.version_info < (2, 6) or not splitblocks:
            # Python < 2.6, no splitting possible
            self.code = [compile('# coding: utf-8\n' + self.text + '\n',
                                 '<script>', 'exec', CO_DIVISION)]
            self.blocks = None
        else:
            # long script, and can compile AST: split into blocks
            self.code, self.blocks = self._splitblocks(self.text)

    def execute(self, controller):
        """Execute the script in the given namespace, using "controller"
        to execute individual blocks."""
        # notify client of new script
        controller.eventfunc('processing', self.serialize())
        # notify clients of "input"
        session.log.log(INPUT, format_script(self))
        # this is to allow the traceback module to report the script's
        # source code correctly
        update_linecache('<script>', self.text)
        if session.experiment and session.mode == 'master':
            session.experiment.scripts += [self.text]
            self._exp_script_index = len(session.experiment.scripts) - 1
        if self.name:
            session.elog_event('scriptbegin', self.name)
        try:
            while self.curblock < len(self.code) - 1:
                self._run.wait()
                self.curblock += 1
                controller.start_exec(self.code[self.curblock],
                                      controller.namespace)
        finally:
            if session.experiment and session.mode == 'master':
                session.experiment.scripts = session.experiment.scripts[:-1]
            if self.name:
                session.elog_event('scriptend', self.name)

    def update(self, text, controller):
        """Update the code with a new script.

        This method is called from a different thread than execute(),
        so we must unset the _run flag before doing anything to
        self.curblock, self.code or self.blocks.
        """
        if not self.blocks:
            if ast is None:
                raise ScriptError('not using Python 2.6, cannot update script')
            raise ScriptError('cannot update single-line script')
        text = fixup_script(text)
        newcode, newblocks = self._splitblocks(text)
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
            if session.experiment and session.mode == 'master':
                scr = session.experiment.scripts
                scr[self._exp_script_index] = self.text
                session.experiment.scripts = scr
            update_linecache('<script>', text)
            self.code, self.blocks = newcode, newblocks
            # let the client know of the update
            controller.eventfunc('processing', self.serialize())
            session.log.log(INPUT, format_script(self, 'UPDATE'))
        finally:
            # let the script continue execution in any case
            self._run.set()

    def _splitblocks(self, text):
        """Parse a script into multiple blocks."""
        codelist = []
        mod = ast.parse('# coding: utf-8\n' + text + '\n', '<script>')
        assert isinstance(mod, ast.Module)
        # construct an individual compilable unit for each block
        for toplevel in mod.body:
            new_mod = ast.Module()
            new_mod.body = [toplevel]
            # do not change the name (2nd parameter); the controller
            # depends on that
            codelist.append(compile(new_mod, '<script>', 'exec', CO_DIVISION))
        return codelist, mod.body

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

    def __init__(self, log, eventfunc, startupsetup):
        self.log = log             # daemon logger object
        self.eventfunc = eventfunc # event emitting callback
        self.setup = startupsetup  # first setup on start
        self.in_startup = True     # True while startup code is executed
        self.queue = Queue()       # user scripts get put here
        self.current_script = None # currently executed script
        self.namespace = session.namespace
                                   # namespace in which scripts execute
        self.session_ns = {'session': session}
                                   # additional namespace for eval_expression()
        self.completer = NicosCompleter(self.namespace)
                                   # completer for the namespace
        self.watchexprs = set()    # watch expressions to evaluate
        self.watchlock = Lock()    # lock for watch expression list modification
        self.estop_functions = []  # functions to run on emergency stop
        self.thread = None         # thread executing scripts
        self.reqno_latest = 0      # number of the last queued request
        self.reqno_working = 0     # number of the last executing request
        self.blocked_reqs = set()  # set of blocked request numbers
        # only one user or admin can issue non-read-only commands
        self.controlling_user = None
        # functions to execute when script goes in break and continues
        self.breakfuncs = (None, None)
        Controller.__init__(self, break_only_in_filename='<script>')
        self.set_observer(self._observer)

    def _observer(self, status, lineno):
        self.eventfunc('status', (status, lineno))

    def _breakfunc(self, frame, arg):
        self.log.info('script interrupted in %s' % self.current_location())
        brfunc, contfunc = self.breakfuncs
        if brfunc:
            self.log.info('calling break function %r...' %
                          getattr(brfunc, '__name__', ''))
            try:
                brfunc() #pylint: disable=E1102
            except Exception:
                self.log.exception('break function raised error')
        # if arg is not None, stop immediately with given arg
        if arg is not None:
            self.set_continue(arg)
        flag = self.wait_for_continue()
        if flag:
            self.log.info('interrupted script stopped: %s' % (flag,))
            self.set_stop(flag)
        else:
            self.log.info('interrupted script continued')
            if contfunc:
                self.log.info('calling continue function %r...' %
                              getattr(contfunc, '__name__', ''))
                try:
                    contfunc() #pylint: disable=E1102
                except Exception:
                    self.log.exception('continue function raised error')

    def current_location(self, verbose=False):
        frame = self.currentframe
        if verbose:
            return '\n' + ''.join(traceback.format_stack(frame))
        else:
            return traceback.format_stack(frame, 1)[0].strip()[5:]. \
                   replace('\n    ', ': ')

    def new_request(self, request):
        assert isinstance(request, Request)
        if self.in_startup:
            raise RequestError('NICOS setup not finished')
        request.reqno = self.reqno_latest + 1
        self.reqno_latest += 1
        # first send the notification, otherwise the request could be processed
        # (resulting in a "processing" event) before the "request" event is
        # even sent
        self.eventfunc('request', request.serialize())
        # put the script on the queue (will not block)
        self.queue.put(request)

    def block_requests(self, requests):
        self.blocked_reqs.update(requests)
        self.eventfunc('blocked', requests)

    def exec_script(self, code, user):
        temp_request = ScriptRequest(code, None, user)
        temp_request.parse(splitblocks=False)
        session.log.log(INPUT, format_script(temp_request, '---'))
        exec temp_request.code[0] in self.namespace

    def simulate_script(self, code, name):
        session.forkSimulation(code, wait=False)

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
            except Exception, err:
                ret[val] = '<cannot be evaluated: %s>' % err
        return ret

    def eval_expression(self, expr):
        try:
            return repr(eval(expr, self.namespace, self.session_ns))
        except Exception, err:
            return '<cannot be evaluated: %s>' % err

    def add_estop_function(self, func, args):
        if not callable(func):
            raise TypeError('emergency stop function must be a callable')
        if not isinstance(args, tuple):
            raise TypeError('emergency stop function args must be a tuple')
        self.estop_functions.append((func, args))
        return len(self.estop_functions)

    def execute_estop(self, user):
        self.log.warn('emergency stop caught, executing ESFs')
        session.log.warn('Emergency stop requested by %s' % user)
        # block all pending scripts
        self.block_requests(range(self.reqno_work + 1, self.reqno_latest + 1))
        # now execute emergency stop functions
        for (func, args) in self.estop_functions:
            try:
                self.log.info('executing ESF: %s%s' % (func, args))
                func(*args)
            except Exception:
                self.log.exception('ESF raised error')
            else:
                self.log.info('ESF finished')

    def start_script_thread(self, *args):
        if self.thread:
            raise RuntimeError('script thread already started')
        self.thread = Thread(target=self.script_thread_entry, args=args)
        self.thread.setDaemon(True)
        self.thread.start()

    def script_thread_entry(self):
        """
        The script execution thread entry point.  This thread executes setup
        code, then waits for scripts on self.queue.  The script is then executed
        in the context of self.namespace, using the controller (self) to watch
        execution.
        """
        self.log.debug('script_thread (re)started')
        try:
            self.in_startup = True
            self.namespace.clear()
            self.namespace['__builtins__'] = __builtin__.__dict__
            setup_code = ('from nicos import session; '
                          'session.handleInitialSetup(%r, False)' % self.setup)
            for _ in range(2):
                # this is to allow the traceback module to report the script's
                # source code correctly
                update_linecache('<setup>', setup_code)
                try:
                    code = compile(setup_code, '<setup>', 'exec')
                    exec code in {}
                except Exception:
                    session.log.warning('Error loading previous setups, '
                                        'loading startup setup', exc=1)
                    setup_code = ('from nicos import session; '
                        'session.handleInitialSetup("startup", False)')
                else:
                    break
            else:
                self.log.warning('error in setup, terminating script_thread')
                self.thread = None
                return
            self.in_startup = False

            while 1:
                # get a script (or other request) from the queue
                request = self.queue.get()
                self.reqno_work = request.reqno
                if request.reqno in self.blocked_reqs:
                    self.log.info('request %d blocked, continuing' %
                                  request.reqno)
                    continue
                self.log.info('processing request %d' % request.reqno)
                if isinstance(request, EmergencyStopRequest):
                    self.execute_estop(request.user)
                    continue
                elif not isinstance(request, ScriptRequest):
                    self.log.error('unknown request: %s' % request)
                    continue
                # parse the script and split it into blocks
                try:
                    self.current_script = request
                    self.current_script.parse()
                except Exception:
                    session.logUnhandledException(cut_frames=1)
                    continue
                # record starting time to decide whether to send notification
                start_time = time.time()
                try:
                    self.current_script.execute(self)
                except ControlStop, err:
                    if err.args[0] == 'emergency stop':
                        self.execute_estop(err.args[1])
                    else:
                        session.log.info('Script stopped by %s' % (err.args[1],))
                    continue
                except Exception, err:
                    # the topmost two frames are still in the
                    # daemon, so don't display them to the user
                    session.logUnhandledException(cut_frames=2)
                    # perhaps also send an error notification
                    exception = format_exception_cut_frames(2)
                    session.notifyConditionally(
                        time.time() - start_time,
                        'Exception in script',
                        'An exception occurred in the executed script:\n\n' +
                        exception + '\n\nThe script was:\n\n' +
                        repr(self.current_script), 'error notification',
                        short='Exception: ' + exception.splitlines()[-1])
                    if isinstance(err, NameError):
                        guessCorrectCommand(self.current_script.text)
                    elif isinstance(err, AttributeError):
                        guessCorrectCommand(self.current_script.text, True)
        except Exception:
            self.log.exception('unhandled exception in script thread')
        finally:
            self.thread = None
