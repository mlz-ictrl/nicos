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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""NICOS cache server.

The NICOS cache is a network service that accepts TCP connections and UDP
packets and stores received key-value pairs, sending updates back to interested
clients.  All key-value pairs can have a timestamp and a time-to-live, after
which they are considered "expired".

Constants and functions needed to implement a cache clients are contained in the
module `nicos.protocols.cache`.  It also contains the documentation of the used
line protocol.
"""

import select
import socket
import threading
from time import time as currenttime, sleep

from nicos import session, config
from nicos.core import Device, Param, host, Attach
from nicos.utils import loggers, closeSocket, createThread, getSysInfo
from nicos.pycompat import queue, listitems, listvalues, from_utf8, to_utf8

# pylint: disable=W0611
from nicos.services.cache.database import CacheDatabase, FlatfileCacheDatabase, \
    MemoryCacheDatabase, MemoryCacheDatabaseWithHistory
from nicos.protocols.cache import msg_pattern, line_pattern, \
    DEFAULT_CACHE_PORT, OP_TELL, OP_ASK, OP_WILDCARD, OP_SUBSCRIBE, \
    OP_TELLOLD, OP_LOCK, OP_REWRITE, CYCLETIME, BUFSIZE


class CacheWorker(object):
    """Worker thread class for the cache server.

    One worker starts two threads: one for receiving data from the connection,
    and one for sending.  Data to send must be posited in `self.send_queue`.
    """

    def __init__(self, db, sock, name, loglevel):
        self.name = name
        # actual value handling is done by the database object
        self.db = db
        # the socket object
        self.sock = sock
        # timeout for send (recv is covered by select timeout)
        self.sock.settimeout(5)
        # list of subscriptions
        self.updates_on = set()
        # list of subscriptions with timestamp requested
        self.ts_updates_on = set()
        self.stoprequest = False

        self.log = session.getLogger(name)
        self.log.setLevel(loggers.loglevels[loglevel])

        # start sender thread (if necessary)
        self.start_sender(name)

        # start receiver thread
        self.receiver = createThread('receiver %s' % name, self._receiver_thread)

    def start_sender(self, name):
        self.send_queue = queue.Queue()
        self.sender = createThread('sender %s' % name, self._sender_thread)

    def __str__(self):
        return 'worker(%s)' % self.name

    def is_active(self):
        return not self.stoprequest and self.receiver.isAlive()

    def closedown(self):
        # try our best to close the connection gracefully
        # assign to local to avoid race condition (self.sock
        # set to None by someone else calling closedown)
        #
        # This may be called more than once!
        sock, self.sock, self.stoprequest = self.sock, None, True
        if sock is not None:
            closeSocket(sock)

    def join(self):
        self.send_queue.put('end')   # to wake from blocking get()
        self.sender.join()
        self.receiver.join()

    def _sender_thread(self):
        while not self.stoprequest:
            data = self.send_queue.get()
            # self.log.debug('sending: %r' % data)
            if self.sock is None:  # connection already closed
                return
            try:
                self.sock.sendall(to_utf8(data))
            except socket.timeout:
                self.log.warning('send timed out, shutting down')
                self.closedown()
            except Exception:
                # if we can't write (or it would be blocking), there is some
                # serious problem: forget writing and close down
                self.log.warning('other end closed, shutting down')
                self.closedown()

    def _receiver_thread(self):
        data = b''
        while not self.stoprequest:
            data = self._process_data(data, self.send_queue.put)
            # wait for data with 3 times the client timeout
            try:
                res = select.select([self.sock], [], [], CYCLETIME * 3)
            except TypeError:
                # TypeError is raised when the connection gets closed and set to
                # None and select finds no fileno()
                return
            except select.error as err:
                self.log.warning('error in select', exc=err)
                self.closedown()
                return
            if self.sock not in res[0]:
                # no data arrived, wait some more
                continue
            try:
                newdata = self.sock.recv(BUFSIZE)
            except Exception:
                newdata = b''
            if not newdata:
                # no data received from blocking read, break connection
                break
            # self.log.debug('newdata: %s' % newdata)
            data += newdata
        self.closedown()

    def _process_data(self, data, reply_callback):
        # split data buffer into message lines and handle these
        match = line_pattern.match(data)
        while match:
            line = match.group(1)
            data = data[match.end():]
            if not line:
                self.log.info('got empty line, closing connection')
                self.closedown()
                return b''
            try:
                ret = self._handle_line(from_utf8(line))
            except Exception as err:
                self.log.warning('error handling line %r' % line, exc=err)
            else:
                # self.log.debug('return is %r' % ret)
                for item in ret:
                    reply_callback(item)
            # continue loop with next match
            match = line_pattern.match(data)
        return data

    def _handle_line(self, line):
        # self.log.debug('handling line: %s' % line)
        match = msg_pattern.match(line)
        if not match:
            # disconnect on trash lines (for now)
            if line:
                self.log.warning('garbled line: %r' % line)
            self.closedown()
            return []
        # extract and clean up individual values
        time, ttlop, ttl, tsop, key, op, value = match.groups()
        key = key.lower()
        value = value or None  # no value -> value gets deleted
        try:
            time = float(time)
        except (TypeError, ValueError):
            # some timestamp is required -- note that this assumes clocks not
            # to be too far out of sync between server and clients
            time = currenttime()
        try:
            ttl = float(ttl)
        except (TypeError, ValueError):
            ttl = None
        # acceptable syntax: either time1-time2 and time1+ttl; convert to ttl
        if ttlop == '-' and ttl:
            ttl = ttl - time

        # dispatch operations to database object
        if op == OP_TELL:
            self.db.tell(key, value, time, ttl, self)
        elif op == OP_ASK:
            if ttl:
                return self.db.ask_hist(key, time, time + ttl)
            else:
                # although passed, time and ttl are ignored here
                return self.db.ask(key, tsop, time, ttl)
        elif op == OP_WILDCARD:
            # time and ttl are currently ignored for wildcard requests
            return self.db.ask_wc(key, tsop, time, ttl)
        elif op == OP_SUBSCRIBE:
            # both time and ttl are ignored for subscription requests,
            # but the return format changes when the @ is included
            if tsop:
                self.ts_updates_on.add(key)
            else:
                self.updates_on.add(key)
        elif op == OP_TELLOLD:
            # the server shouldn't get TELLOLD, ignore it
            pass
        elif op == OP_LOCK:
            return self.db.lock(key, value, time, ttl)
        elif op == OP_REWRITE:
            self.db.rewrite(key, value)
        return []

    def update(self, key, op, value, time, ttl):
        """Check if we need to send the update given."""
        # make sure line has at least a default timestamp
        for mykey in self.ts_updates_on:
            # do a substring match on key
            if mykey in key:
                if not time:
                    time = currenttime()
                # self.log.debug('sending update of %s to %s' % (key, value))
                if ttl is not None:
                    msg = '%s+%s@%s%s%s\n' % (time, ttl, key, op, value)
                else:
                    msg = '%s@%s%s%s\n' % (time, key, op, value)
                self.send_queue.put(msg)
                return  # send at most one update
        # same for requested updates without timestamp
        for mykey in self.updates_on:
            if mykey in key:
                # self.log.debug('sending update of %s to %s' % (key, value))
                self.send_queue.put(key + op + value + '\n')
                return  # send at most one update


class CacheUDPWorker(CacheWorker):
    """Special subclass for handling UDP requests."""

    def __init__(self, db, sock, name, data, remoteaddr, loglevel):
        # "data" is what we received over the UDP socket, "remoteaddr" is the
        # address for replies
        self.data = data
        self.remoteaddr = remoteaddr
        CacheWorker.__init__(self, db, sock, name, loglevel)

    def start_sender(self, name):
        pass

    def join(self):
        self.receiver.join()

    def closedown(self):
        # not closing self.sock here; it is the UDP server socket...
        self.stoprequest = True
        self.sock = None

    def _receiver_thread(self):
        # we will never read any more data: just process what we got and send
        # any needed responses synchronously
        try:
            self._process_data(self.data,
                               lambda reply: self._sendall(to_utf8(reply)))
        except Exception as err:
            self.log.warning('error handling UDP data %r' % self.data, exc=err)
        self.closedown()

    def _sendall(self, data, maxsize=1496):
        """Replacement for sendall() on TCP sockets: send all data via UDP
        in as many packets as needed.
        """
        datalen = len(data)
        # split data into chunks which are less than maxsize
        while data:
            # find rightmost \n within first maxsize bytes
            p = data[:maxsize].rfind('\n')
            if p == -1:
                # line too long. cross your fingers and split SOMEWHERE
                p = maxsize - 1
            self.sock.sendto(data[:p + 1], self.remoteaddr)
            self.log.debug('UDP: sent %d bytes' % (p + 1))
            data = data[p + 1:]  # look at remaining data
        return datalen


class CacheServer(Device):
    """
    The server class.
    """

    parameters = {
        'server':   Param('Address to bind to (host or host:port)', type=host,
                          mandatory=True),
    }

    attached_devices = {
        'db': Attach('The cache database instance', CacheDatabase),
    }

    def doInit(self, mode):
        self._stoprequest = False
        # TCP server address if bound to TCP
        self._boundto = None
        # server sockets for TCP and UDP
        self._serversocket = None
        self._serversocket_udp = None
        # worker connections
        self._connected = {}
        self._attached_db._server = self
        self._connectionLock = threading.Lock()

    def start(self, *startargs):
        if config.instrument == 'demo' and 'clear' in startargs:
            self._attached_db.clearDatabase()
        self._attached_db.initDatabase()
        self.storeSysInfo()
        self._worker = createThread('server', self._server_thread)

    def storeSysInfo(self):
        key, res = getSysInfo('cache')
        self._attached_db.tell(key, res, currenttime(), None, None)

    def _bind_to(self, address, proto='tcp'):
        # bind to the address with the given protocol; return socket and address
        if ':' not in address:
            host = address
            port = DEFAULT_CACHE_PORT
        else:
            host, port = address.split(':')
            port = int(port)
        serversocket = socket.socket(
            socket.AF_INET, proto == 'tcp' and socket.SOCK_STREAM or socket.SOCK_DGRAM)
        serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if proto == 'udp':
            # we want to be able to receive UDP broadcasts
            serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        try:
            serversocket.bind((socket.gethostbyname(host), port))
            if proto == 'tcp':
                serversocket.listen(50)  # max waiting connections....
            return serversocket, (host, port)
        except Exception:
            serversocket.close()
            return None, None     # failed, return None as indicator

    def _server_thread(self):
        self.log.info('server starting')

        # bind UDP broadcast socket
        self.log.debug('trying to bind to UDP broadcast')
        self._serversocket_udp = self._bind_to('', 'udp')[0]
        if self._serversocket_udp:
            self.log.info('UDP bound to broadcast')

        # now try to bind TCP socket, include 'MUST WORK' standalone names
        self.log.debug('trying to bind to ' + self.server)
        self._serversocket, self._boundto = self._bind_to(self.server)

        # one of the must have worked, otherwise continuing makes no sense
        if not self._serversocket and not self._serversocket_udp:
            self._stoprequest = True
            self.log.error("couldn't bind any sockets, giving up!")
            return

        if not self._boundto:
            self.log.warning('starting main loop only bound to UDP broadcast')
        else:
            self.log.info('TCP bound to %s:%s' % self._boundto)

        # now enter main serving loop
        while not self._stoprequest:
            # loop through connections, first to remove dead ones,
            # secondly to try to reconnect
            for addr, client in listitems(self._connected):
                if client:
                    if not client.is_active():  # dead or stopped
                        self.log.info('client connection %s closed' % addr)
                        client.closedown()
                        client.join()  # wait for threads to end
                        del self._connected[addr]

            # now check for additional incoming connections
            # build list of things to check
            selectlist = []
            if self._serversocket:
                selectlist.append(self._serversocket)
            if self._serversocket_udp:
                selectlist.append(self._serversocket_udp)

            # 3 times client-side timeout
            res = select.select(selectlist, [], [], CYCLETIME * 3)
            if not res[0]:
                continue  # nothing to read -> continue loop
            # lock aginst code in self.quit
            with self._connectionLock:
                if self._stoprequest:
                    break
                if self._serversocket in res[0]:
                    # TCP connection came in
                    conn, addr = self._serversocket.accept()
                    addr = 'tcp://%s:%d' % addr
                    self.log.info('new connection from %s' % addr)
                    self._connected[addr] = CacheWorker(
                        self._attached_db, conn, name=addr, loglevel=self.loglevel)
                elif self._serversocket_udp in res[0]:
                    # UDP data came in
                    data, addr = self._serversocket_udp.recvfrom(3072)
                    nice_addr = 'udp://%s:%d' % addr
                    self.log.info('new connection from %s' % nice_addr)
                    self._connected[nice_addr] = CacheUDPWorker(
                        self._attached_db, self._serversocket_udp, name=nice_addr,
                        data=data, remoteaddr=addr, loglevel=self.loglevel)
        if self._serversocket:
            closeSocket(self._serversocket)
        self._serversocket = None

    def wait(self):
        while not self._stoprequest:
            sleep(self._long_loop_delay)
        self._worker.join()

    def quit(self, signum=None):
        self.log.info('quitting on signal %s...' % signum)
        self._stoprequest = True
        # without locking, the _connected list may not have all clients yet....
        with self._connectionLock:
            for client in listvalues(self._connected):
                self.log.info('closing client %s' % client)
                if client.is_active():
                    client.closedown()
        with self._connectionLock:
            for client in listvalues(self._connected):
                self.log.info('waiting for %s' % client)
                client.closedown()  # make sure, the connection closes down
                client.join()
        self.log.info('waiting for server')
        self._worker.join()
        self.log.info('server finished')
