# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

"""The base class for communication with the NICOS server."""

import hashlib
import socket
import threading
from base64 import b64decode, b64encode
from time import time as currenttime

import rsa

from nicos.clients.proto.classic import ClientTransport
from nicos.protocols.daemon import ACTIVE_COMMANDS, DAEMON_EVENTS, \
    ProtocolError
from nicos.protocols.daemon.classic import COMPATIBLE_PROTO_VERSIONS, \
    PROTO_VERSION
from nicos.utils import createThread

BUFSIZE = 8192


class ErrorResponse(Exception):
    pass


class ConnectionData:
    def __init__(self, host, port, user, password, viewonly=False,
                 expertmode=False, **extrakwds):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.viewonly = viewonly
        self.expertmode = expertmode

    def copy(self):
        # the copy shouldn't get the password to enforce a retyping of it
        return ConnectionData(self.host, self.port, self.user, None,
                              self.viewonly, self.expertmode)

    def serialize(self):
        return vars(self)


class NicosClient:
    RECONNECT_TRIES = 25
    RECONNECT_TRIES_LONG = 5
    RECONNECT_INTERVAL_SHORT = 500  # in ms
    RECONNECT_INTERVAL_LONG = 2000

    def __init__(self, log_func):
        self.host = ''
        self.port = 0

        # if the daemon uses an old protocol version that we still support,
        # we need to fix up some requests -- this is set to the old version
        self.compat_proto = 0

        self.log_func = log_func
        self.lock = threading.Lock()
        self.isconnected = False
        self.disconnecting = False
        self.gzip = False
        self.last_reqid = None
        self.viewonly = True
        self.user_level = None
        self.last_action_at = 0

        self.transport = ClientTransport()

    def signal(self, name, *args):
        # must be overwritten
        raise NotImplementedError

    def connect(self, conndata, eventmask=None):
        """Connect to a NICOS daemon.

        *conndata* is a ConnectionData object.

        *eventmask* is a tuple of event names that should not be sent to this
        client.
        """
        self.disconnecting = False
        if self.isconnected:
            raise RuntimeError('client already connected')

        try:
            self.transport.connect(conndata)
        except OSError as err:
            msg = err.args[1] if len(err.args) >= 2 else str(err)
            self.signal('failed', 'Server connection failed: %s.' % msg, err)
            return
        except Exception as err:
            self.signal('failed', 'Server connection failed: %s.' % err, err)
            return

        # read banner
        try:
            success, banner = self.transport.recv_reply()
            if not success:
                raise ProtocolError('invalid response format')
            if 'daemon_version' not in banner:
                raise ProtocolError('daemon version missing from response')
            daemon_proto = banner.get('protocol_version', 0)
            if daemon_proto != PROTO_VERSION:
                if daemon_proto in COMPATIBLE_PROTO_VERSIONS:
                    self.compat_proto = daemon_proto
                else:
                    raise ProtocolError('daemon uses protocol %d, but this '
                                        'client requires protocol %d, do you '
                                        'need to update NICOS?'
                                        % (daemon_proto, PROTO_VERSION))
        except Exception as err:
            self.signal('failed', 'Server (%s:%d) handshake failed: %s.'
                        % (conndata.host, conndata.port, err), err)
            return

        # log-in sequence
        self.isconnected = True
        password = conndata.password
        pw_hashing = banner.get('pw_hashing', 'sha1')

        if pw_hashing[0:4] == 'rsa,':
            if rsa is not None:
                encodedkey = banner.get('rsakey', None)
                if encodedkey is None:
                    raise ProtocolError('rsa requested, but rsakey missing in banner')
                pubkey = rsa.PublicKey.load_pkcs1(b64decode(encodedkey))
                password = rsa.encrypt(password.encode(), pubkey)
                password = 'RSA:' + b64encode(password).decode()
            else:
                pw_hashing = pw_hashing[4:]
        if pw_hashing == 'sha1':
            password = hashlib.sha1(password.encode()).hexdigest()
        elif pw_hashing == 'md5':
            password = hashlib.md5(password.encode()).hexdigest()

        credentials = {
            'login': conndata.user,
            'passwd': password,
            'display': '',
        }

        response = self.ask('authenticate', credentials)
        if not response:
            self._close()
            return
        self.user_level = response['user_level']

        if eventmask:
            self.tell('eventmask', eventmask)

        try:
            self.transport.connect_events(conndata)
        except Exception as err:
            self.signal('failed', 'Event connection failed: %s.' % err, err)
            return

        # start event handler
        self.event_thread = createThread('event handler', self.event_handler)

        self.host, self.port = conndata.host, conndata.port
        self.login = conndata.user
        self.viewonly = conndata.viewonly

        self.daemon_info = banner
        self.signal('connected')

    def event_handler(self):
        while 1:
            try:
                event, data, blobs = self.transport.recv_event()
            except InterruptedError:
                continue
            except Exception as err:
                if not self.disconnecting:
                    self.log_func('Error getting event: %s' % err)
                    self.signal('broken', 'Server connection broken.')
                    self._close()
                return
            try:
                if DAEMON_EVENTS[event][1]:
                    self.signal(event, data, blobs)
                else:
                    self.signal(event, data)
            except Exception as err:
                self.log_func('Error in event handler: %s' % err)

    def disconnect(self):
        self.disconnecting = True
        try:
            self.transport.send_command('quit', ())
        except Exception:
            # if the connection is already dead, at least close the socket
            pass
        self._close()

    def _close(self):
        self.transport.disconnect()
        self.gzip = False
        if self.isconnected:
            self.isconnected = False
            self.signal('disconnected')

    def handle_error(self, err):
        if isinstance(err, ErrorResponse):
            self.signal('error', 'Error from daemon: %s.' % (err.args[0],))
        else:
            if isinstance(err, ProtocolError):
                msg = 'Communication error: %s.' % (err.args[0],)
            elif isinstance(err, socket.timeout):
                msg = 'Connection to server timed out.'
            elif isinstance(err, OSError):
                msg = 'Server connection broken: %s.' % (err.args[1],)
            # we cannot handle this without breaking connection, since
            # it generally means that the response is not yet received;
            # and to carry on means that we receive the pending response
            # "in reply" to one of the next commands
            elif isinstance(err, KeyboardInterrupt):
                msg = 'Server communication interrupted by user.'
            else:
                msg = 'Exception occurred: %s.' % (err,)
            self.signal('broken', msg)
            self._close()

    def tell(self, command, *args):
        """Excecute a command that does not generate a response.

        The arguments are the command and its parameter(s), if necessary.
        """
        if not self.isconnected:
            self.signal('error', 'You are not connected to a server.')
            return
        elif self.viewonly and command in ACTIVE_COMMANDS:
            self.signal('error', 'Your client is set to view-only mode.')
            return
        try:
            with self.lock:
                self.transport.send_command(command, args)
                success, data = self.transport.recv_reply()
                if not success:
                    raise ErrorResponse(data)
                return True
        except (Exception, KeyboardInterrupt) as err:
            return self.handle_error(err)

    def tell_action(self, command, *args):
        """Execute a command and reset the last action time."""
        self.last_action_at = currenttime()
        return self.tell(command, *args)

    def ask(self, command, *args, **kwds):
        """Execute a command that generates a response, and return the response.

        The arguments are the command and its parameter(s), if necessary.

        A *quiet=True* keyword can be given if no error should be generated if
        the client is not connected.  When not connected, you can give a
        *default* keyword to return.
        """
        if not self.isconnected:
            if not kwds.get('quiet', False):
                self.signal('error', 'You are not connected to a server.')
            return kwds.get('default')
        elif self.viewonly and command in ACTIVE_COMMANDS:
            self.signal('error', 'Your client is set to view-only mode.')
            return kwds.get('default')
        try:
            with self.lock:
                self.transport.send_command(command, args)
                success, data = self.transport.recv_reply()
                if not success:
                    if not kwds.get('noerror', False):
                        raise ErrorResponse(data)
                    return kwds.get('default')
                return data
        except (Exception, KeyboardInterrupt) as err:
            self.handle_error(err)
            return kwds.get('default')

    def run(self, code, filename=None, noqueue=False):
        """Run a piece of code."""
        self.last_action_at = currenttime()
        if noqueue:
            new_reqid = self.ask('start', filename or '', code, noerror=True)
            if new_reqid is not None:
                self.last_reqid = new_reqid
            else:
                return None
        else:
            self.last_reqid = self.ask('queue', filename or '', code)
        return self.last_reqid

    def eval(self, expr, default=Ellipsis, stringify=False):
        """Evaluate a Python expression in the daemon's namespace and return
        the result.

        If the *default* is not given, an exception while evaluating is
        propagated as an exception to the client.  If it is given, the
        default is returned instead.  The default is also returned when the
        client is not connected.

        If *stringify* is true, the result is returned as a string.
        """
        result = self.ask('eval', expr, bool(stringify), quiet=True,
                          default=default)
        if isinstance(result, BaseException):
            if default is not Ellipsis:
                return default
            raise result  # pylint: disable=raising-bad-type
        return result

    # high-level functionality

    def getDeviceList(self, needs_class='nicos.core.device.Device',
                      only_explicit=True, exclude_class=None,
                      special_clause=None):
        """Return a list of NICOS devices.

        The *needs_class* argument can be given if the devices should be
        restricted to a certain base class, such as
        ``'nicos.core.device.Moveable'``.

        If *only_explicit* is true, only devices that are in the NICOS
        namespace will be returned (i.e. those with namespace visibility and
        that have been explicitly created afterward).
        """
        query = 'list(dn for (dn, d) in session.devices.items() ' \
                'if %r in d.classes' % needs_class
        if exclude_class is not None:
            query += ' and %r not in d.classes' % exclude_class
        if only_explicit:
            query += ' and dn in session.explicit_devices'
        if special_clause:
            query += ' and ' + special_clause
        query += ')'
        if res := self.eval(query, []):
            return sorted(res, key=lambda d: d.lower())
        return []

    def getDeviceValue(self, devname):
        """Return current device value."""
        return self.eval('session.getDevice(%r).read()' % devname, None)

    def getDeviceValuetype(self, devname):
        """Return device value type.

        This is what has been set as the ``dev.valuetype`` attribute.
        """
        return self.eval('session.getDevice(%r).valuetype' % devname, None)

    def getDeviceParamInfo(self, devname):
        """Return info about all parameters of the device.

        The info is a dictionary of parameter name mapping to a dictionary with
        all attributes of the `.Param` instance for the parameter.
        """
        query = 'dict((pn, pi.serialize()) for (pn, pi) in ' \
                'session.getDevice(%r).parameters.items())' % devname
        result = self.eval(query, {})
        if result and 'alias' in result:
            query = 'dict((pn, pi.serialize()) for (pn, pi) in ' \
                    'session.getDevice(session.getDevice(%r).alias).' \
                    'parameters.items())' % devname
            if result2 := self.eval(query, {}):
                result.update(result2)
        return result or {}

    def getDeviceParams(self, devname):
        """Return values of all device parameters from cache, as a dictionary."""
        params = {}
        devkeys = self.ask('getcachekeys', devname.lower() + '/',
                           quiet=True, default=[])
        for item in devkeys:
            try:
                key, value = item
            except ValueError:
                continue
            param = key.rsplit('/', 1)[1]
            params[param] = value
        return params

    def getCacheKey(self, key):
        """Return (key, value) for the given cache key."""
        keys = self.ask('getcachekeys', key, quiet=True, default=[])
        for item in keys:
            if item[0] == key:
                return item
        return None

    def getDeviceParam(self, devname, param):
        """Return value of a specific device parameter from cache."""
        if ret := self.getCacheKey(devname.lower() + '/' + param):
            return ret[1]
        return None
