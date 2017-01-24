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

"""Logging utilities specific to NICOS."""

import os
import sys
import time
import traceback
from os import path
from logging import addLevelName, Manager, Logger, LogRecord, Formatter, \
    Handler, DEBUG, INFO, WARNING, ERROR

from nicos import session
from nicos.utils import colorize, formatExtendedTraceback
from nicos.pycompat import text_type, from_maybe_utf8, binary_type


LOGFMT = '%(asctime)s : %(levelname)-7s : %(name)s: %(message)s'
DATEFMT = '%H:%M:%S'
DATESTAMP_FMT = '%Y-%m-%d'
SECONDS_PER_DAY = 60 * 60 * 24

ACTION = INFO + 1
INPUT  = INFO + 6

loglevels = {'debug': DEBUG, 'info': INFO, 'action': ACTION, 'warning': WARNING,
             'error': ERROR, 'input': INPUT}

TRANSMIT_ENTRIES = ('name', 'created', 'levelno', 'message', 'exc_text',
                    'filename')


class NicosLogger(Logger):
    """
    Nicos logger class with special method behavior.
    """

    def exception(self, *msgs, **kwds):
        kwds['exc'] = True
        self.error(*msgs, **kwds)

    def _process(self, msgs, kwds):
        # standard logging keyword arg
        exc_info = kwds.pop('exc_info', None)
        # nicos easy keyword arg
        exc = kwds.pop('exc', None)
        if not exc_info:
            if isinstance(exc, Exception):
                exc_info = (type(exc), exc, None)
            elif exc:
                exc_info = sys.exc_info()
                # did an exception really occur?
                if exc_info[0] is None:
                    exc_info = None
        extramsgs = []
        if exc_info:
            if msgs:
                extramsgs += ['-']
            from nicos.core.errors import NicosError
            if issubclass(exc_info[0], NicosError):
                extramsgs += [exc_info[0].category + ' -', exc_info[1]]
            else:
                extramsgs += [exc_info[0].__name__ + ' -', exc_info[1]]

        if not msgs:
            msg = ''
            args = ()
        else:
            msg = msgs[0]
            if isinstance(msg, binary_type):
                msg = from_maybe_utf8(msg)
            else:
                msg = text_type(msg)
            args = msgs[1:]
        if extramsgs:
            if msg:
                msg += ' '
            msg += ' '.join(from_maybe_utf8(msg) if isinstance(msg, binary_type)
                            else text_type(msg) for msg in extramsgs)
        return msg, args, exc_info

    def error(self, *msgs, **kwds):
        msg, args, exc_info = self._process(msgs, kwds)
        Logger.error(self, msg, *args, exc_info=exc_info, extra=kwds)

    def warning(self, *msgs, **kwds):
        msg, args, exc_info = self._process(msgs, kwds)
        Logger.warning(self, msg, *args, exc_info=exc_info, extra=kwds)

    def info(self, *msgs, **kwds):
        msg, args, exc_info = self._process(msgs, kwds)
        Logger.info(self, msg, *args, exc_info=exc_info, extra=kwds)

    def debug(self, *msgs, **kwds):
        msg, args, exc_info = self._process(msgs, kwds)
        Logger.debug(self, msg, *args, exc_info=exc_info, extra=kwds)

    def action(self, msg):
        Logger.log(self, ACTION, msg)

    def _log(self, level, msg, args, exc_info=None, extra=None):
        record = LogRecord(self.name, level, self.manager.globalprefix,
                           0, msg, args, exc_info, '')

        try:
            record.message = (msg % args) if args else msg
        except (KeyError, TypeError):
            record.message = msg  # we don't do args substitution on demand
        if extra is not None:
            for key in extra:
                record.__dict__[key] = extra[key]
        self.handle(record)


class NicosConsoleFormatter(Formatter):
    """
    A lightweight formatter for the interactive console, with optional
    colored output.
    """

    def __init__(self, fmt=None, datefmt=None, colorize=None):
        Formatter.__init__(self, fmt, datefmt)
        if colorize:
            self.colorize = colorize
        else:
            self.colorize = lambda c, s: s

    def formatException(self, exc_info):
        return traceback.format_exception_only(*exc_info[0:2])[-1]

    def formatTime(self, record, datefmt=None):
        return time.strftime(datefmt or DATEFMT,
                             self.converter(record.created))

    def format(self, record):
        levelno = record.levelno
        datefmt = self.colorize('lightgray', '[%(asctime)s] ')
        if record.name == 'nicos':
            namefmt = ''
        else:
            namefmt = '%(name)-10s: '
        if levelno == ACTION:
            if os.name == 'nt':
                return ''
            # special behavior for ACTION messages: use them as terminal title
            fmtstr = '\x1b]0;%s%%(message)s\x07' % namefmt
        else:
            if levelno <= DEBUG:
                fmtstr = self.colorize('darkgray', '%s%%(message)s' % namefmt)
            elif levelno <= INFO:
                fmtstr = '%s%%(message)s' % namefmt
            elif levelno == INPUT:
                # do not display input again
                return ''
            elif levelno <= WARNING:
                fmtstr = self.colorize('fuchsia', '%s%%(levelname)s: %%(message)s'
                                       % namefmt)
            else:
                fmtstr = self.colorize('red', '%s%%(levelname)s: %%(message)s'
                                       % namefmt)
            fmtstr = '%(filename)s' + datefmt + fmtstr
            if not getattr(record, 'nonl', False):
                fmtstr += '\n'
        record.asctime = self.formatTime(record, self.datefmt)
        s = fmtstr % record.__dict__
        # never output more exception info -- the exception message is already
        # part of the log message because of our special logger behavior
        # if record.exc_info:
        #    # *not* caching exception text on the record, since it's
        #    # only a short version
        #    s += self.formatException(record.exc_info)
        return s


class NicosLogfileFormatter(Formatter):
    """
    The standard Formatter does not support milliseconds with an explicit
    datestamp format.  It also doesn't show the full traceback for exceptions.
    """

    extended_traceback = True

    def formatException(self, ei):
        if self.extended_traceback:
            s = formatExtendedTraceback(*ei)
        else:
            s = ''.join(traceback.format_exception(ei[0], ei[1], ei[2],
                                                   sys.maxsize))
            if s.endswith('\n'):
                s = s[:-1]
        return s

    def formatTime(self, record, datefmt=None):
        res = time.strftime(DATEFMT, self.converter(record.created))
        res += ',%03d' % record.msecs
        return res


class StreamHandler(Handler):
    """Reimplemented from logging: remove cruft, remove bare excepts."""

    def __init__(self, stream=None):
        Handler.__init__(self)
        if stream is None:
            stream = sys.stderr
        self.stream = stream

    def flush(self):
        self.acquire()
        try:
            if self.stream and hasattr(self.stream, 'flush'):
                self.stream.flush()
        finally:
            self.release()

    def emit(self, record, fs='%s\n'):  # pylint: disable=W0221
        try:
            msg = self.format(record)
            try:
                self.stream.write(fs % msg)
            except UnicodeEncodeError:
                self.stream.write(fs % msg.encode('utf-8'))
            self.flush()
        except Exception:
            self.handleError(record)


class NicosLogfileHandler(StreamHandler):
    """
    Logs to log files with a date stamp appended, and rollover on midnight.
    """

    def __init__(self, directory, filenameprefix='nicos', filenamesuffix=None,
                 dayfmt=DATESTAMP_FMT, use_subdir=True):
        if use_subdir:
            directory = path.join(directory, filenameprefix)
        if not path.isdir(directory):
            os.makedirs(directory)
        self._currentsymlink = path.join(directory, 'current')
        self._filenameprefix = filenameprefix
        self._filenamesuffix = filenamesuffix
        self._pathnameprefix = path.join(directory, filenameprefix)
        self._dayfmt = dayfmt
        # today's logfile name
        if filenamesuffix:
            basefn = self._pathnameprefix + '-' + time.strftime(dayfmt) + \
                '-' + filenamesuffix + '.log'
        else:
            basefn = self._pathnameprefix + '-' + time.strftime(dayfmt) + '.log'
        self.baseFilename = path.abspath(basefn)
        self.mode = 'a'
        StreamHandler.__init__(self, self._open())
        # determine time of first midnight from now on
        t = time.localtime()
        self.rollover_at = time.mktime((t[0], t[1], t[2] + 1,
                                        0, 0, 0, 0, 0, -1))
        self.setFormatter(NicosLogfileFormatter(LOGFMT, DATEFMT))
        self.disabled = False

    def _open(self):
        # update 'current' symlink upon open
        try:
            os.remove(self._currentsymlink)
        except OSError:
            # if the symlink does not (yet) exist, OSError is raised.
            # should happen at most once per installation....
            pass
        if hasattr(os, 'symlink'):
            os.symlink(path.basename(self.baseFilename), self._currentsymlink)
        # finally open the new logfile....
        return open(self.baseFilename, self.mode)

    def filter(self, record):
        return not self.disabled

    def emit(self, record):  # pylint: disable=W0221
        if record.levelno == ACTION:
            # do not write ACTIONs to logfiles, they're only informative
            return
        try:
            t = int(time.time())
            if t >= self.rollover_at:
                self.doRollover()
            if self.stream is None:
                self.stream = self._open()
            StreamHandler.emit(self, record)
        except Exception:
            self.handleError(record)

    def enable(self, enabled):
        if enabled:
            self.disabled = False
            self.stream.close()
            self.stream = self._open()
        else:
            self.disabled = True

    def close(self):
        self.acquire()
        try:
            if self.stream:
                self.flush()
                if hasattr(self.stream, 'close'):
                    self.stream.close()
                StreamHandler.close(self)
                self.stream = None
        finally:
            self.release()

    def doRollover(self):
        self.stream.close()
        if self._filenamesuffix:
            self.baseFilename = '%s-%s-%s.log' % (
                self._pathnameprefix, time.strftime(self._dayfmt),
                self._filenamesuffix)
        else:
            self.baseFilename = self._pathnameprefix + '-' + \
                time.strftime(self._dayfmt) + '.log'
        self.stream = self._open()
        t = time.localtime()
        self.rollover_at = time.mktime((t[0], t[1], t[2] + 1,
                                        0, 0, 0, 0, 0, -1))


class ColoredConsoleHandler(StreamHandler):
    """
    A handler class that writes colorized records to standard output.
    """

    def __init__(self):
        StreamHandler.__init__(self, sys.stdout)
        self.setFormatter(NicosConsoleFormatter(
            datefmt=DATEFMT, colorize=colorize))

    def emit(self, record):  # pylint: disable=W0221
        msg = self.format(record)
        try:
            self.stream.write(msg)
        except UnicodeEncodeError:
            self.stream.write(msg.encode('utf-8'))
        self.stream.flush()


class ELogHandler(Handler):

    def __init__(self):
        Handler.__init__(self)
        self.disabled = False

    def filter(self, record):
        return not self.disabled

    def emit(self, record):
        if record.levelno == ACTION or record.filename:
            # do not write ACTIONs to logfiles, they're only informative
            # also do not write messages from simulation mode
            return
        msg = [getattr(record, e) for e in TRANSMIT_ENTRIES]
        if not hasattr(record, 'nonl'):
            msg[3] += '\n'
        session.elogEvent('message', msg)


def initLoggers():
    addLevelName(ACTION, 'ACTION')
    addLevelName(INPUT, 'INPUT')
    Manager.globalprefix = ''
