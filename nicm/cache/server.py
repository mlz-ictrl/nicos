#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   NICM cache server process
#
# Author:
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
#   The basic NICOS methods for the NICOS daemon (http://nicos.sf.net)
#
#   Copyright (C) 2009 Jens Krüger <jens.krueger@frm2.tum.de>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# *****************************************************************************

"""NICM cache server."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import re
import select
import signal
import socket
import threading
from time import time as current_time, sleep

# regular expression matching a cache protocol message
msg_pattern = re.compile(r'''
    ^ (?:
      \s* (?P<time>\d+\.?\d*)?    # timestamp
      \s* [+]?                    # ttl operator
      \s* (?P<ttl>\d+\.?\d*)?     # ttl
      \s* (?P<tsop>@)             # timestamp mark
    )?
    \s* (?P<key>[^=!?]*?)         # key
    \s* (?P<op>[=!?])             # operator
    \s* (?P<value>[^\r\n]*?)      # value
    \s* $
    ''', re.X)

line_pattern = re.compile(r'([^\r\n]*)(\r\n|\r|\n)')


class CacheUDPConnection(object):
    """
    An UDP connection to use instead of a TCP connection in the CacheWorker.
    """

    def __init__(self, udpsocket, remoteaddr, log, maxsize=1496):
        self.remoteaddr = remoteaddr
        self.udpsocket = udpsocket
        self.log = log
        self.maxsize = maxsize
        # XXX log
        #print "UDPConnection: addr =",remoteaddr,", udpsocket =",udpsocket

    def fileno(self):
        # provide a pseudo-fileno; the actual value doesn't matter as long as
        # there is some thing with this id
        return -self.udpsocket.fileno()

    def close(self):
        self.log('UDP: close')

    def shutdown(self, how):
        self.log('UDP: shutdown')

    def recv(self, maxbytes):
        # not needed
        self.log('UDP: recv')
        return ''

    def send(self, data):
        datalen = len(data)
        #self.log('UDP: send %d bytes' % datalen)
        # split data into chunks which are less than self.maxsize
        # data ALWAYS contains the data not yet sent
        while data:
            # find rightmost \n within first self.maxsize bytes
            p = data[:self.maxsize].rfind('\n')
            # if not found, retry with \r
            if p == -1:
                p = data[:self.maxsize].rfind('\r')
            if p == -1:
                # line too long. cross your fingers and split SOMEWHERE
                p = self.maxsize - 1
            self.udpsocket.sendto(data[:p+1], self.remoteaddr)
            self.log('UDP: sent %d bytes' % (p+1))
            data = data[p+1:] # look at remaining data
        return datalen


class CacheWorker(object):
    """
    Worker thread class for the cache server.
    """

    def __init__(self, db, connection=None, name='',
                 initstring='', initdata=''):
        self.db = db
        self.connection = connection
        self.name = name
        try:
            self.connection.setblocking(True)
        except Exception:
            pass
        # list of subscriptions
        self.updates_on = set()
        # list of subscriptions with timestamp requested
        self.ts_updates_on = set()
        self.stoprequest = False
        self.worker = None

        self.log = db.log

        if initstring:
            if not self.writeto(initstring):
                self.stoprequest = True
                return
        self.worker = threading.Thread(None, self._worker_thread,
                                       'worker %s' % name, args=(initdata,))
        self.worker.setDaemon(True)
        self.worker.start()

    def __str__(self):
        return 'worker(%s)' % self.name

    def _worker_thread(self, initdata):
        data = initdata
        while not self.stoprequest:
            # split data buffer into message lines and handle these
            match = line_pattern.match(data)
            while match:
                line = match.group(1)
                data = data[match.end():]
                if not line:
                    self.log(self, 'got empty line, closing connection')
                    self.closedown()
                    return
                self.log(self, 'got line: %r' % line)
                ret = self._handle_line(line)
                if ret:
                    self.writeto('\r\n'.join(ret) + '\r\n')
                match = line_pattern.match(data)
            if self.connection and self.connection.fileno() > 0:
                # wait for data with 1-second timeout
                res = select.select([self.connection], [], [self.connection], 1)
                if self.connection in res[2]:
                    # connection is in error state
                    break
                if self.connection not in res[0]:
                    # no data arrived, wait some more
                    continue
            try:
                newdata = self.connection.recv(8192)
            except Exception:
                newdata = ''
            if not newdata:
                # no data received from blocking read, break connection
                break
            self.log(self, 'got new data: %r' % newdata)
            data += newdata
        self.closedown()

    def _handle_line(self, line):
        match = msg_pattern.match(line)
        if not match:
            # ignore trash lines (for now)
            #if line.upper().startswith(('GET', 'POST', 'HEAD')):
            self.closedown()
            return
        # extract and clean up individual values
        time, ttl, tsop, key, op, value = match.groups()
        key = key.lower()
        try:
            time = float(time)
        except:
            time = current_time()
        try:
            ttl = float(ttl)
        except:
            ttl = None

        # dispatch operations
        if op == '=':
            self.log(self, 'set key %r to %r' % (key, value))
            if value:
                self.db.tell(key, value, time, ttl)
            else:
                self.db.delete(key)
        elif op == '?':
            self.log(self, 'ask key %r' % key)
            if tsop:
                return self.db.ask_ts(key, time, ttl)
            else:
                return self.db.ask(key)
        elif op == '!':
            self.log(self, 'subscribe key %r' % key)
            if tsop:
                self.ts_updates_on.add(key)
            else:
                self.updates_on.add(key)

    def is_active(self):
        return not self.stoprequest and self.worker.isAlive()

    def closedown(self):
        if not self.connection:
            return
        self.stoprequest = True
        try:
            self.connection.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        try:
            self.connection.close()
        except Exception:
            pass
        self.connection = None

    def writeto(self, data):
        if not self.connection:
            return False
        tries = 0
        remaining = len(data)
        try:
            remaining -= self.connection.send(data)
        except:
            tries = 100
        while remaining > 0 and tries < 100:
            # some data still left, retry after some wait
            sleep(0.1)
            tries += 1
            # try to send all, but check if we could only send less
            try:
                remaining -= self.connection.send(data[-remaining:])
            except:
                tries = 100
        if not remaining:
            # signal success
            return True
        # Ok, if we can't write now, there is some serious problem.
        # forget writing and close all down
        self.log(self, 'other end closed, shutting down')
        self.closedown()
        return False

    def update(self, key, value, time):
        """Check if we need to send the update given in 'line'."""
        if not self.connection:
            return False
        # make sure line has at least a default timestamp
        for mykey in self.ts_updates_on:
            # do a substring match on key
            if mykey in key:
                if not time:
                    time = current_time()
                self.log(self, 'sending update: %r %r %r' % (time, key, value))
                return self.writeto('%s@%s=%s\r\n' % (time, key, value))
        # same for requested updates without timestamp
        for mykey in self.updates_on:
            if mykey in key:
                return self.writeto('%s=%s\r\n' % (key, value))
        # no update neccessary, signal success
        return True


class Entry(object):
    __slots__ = ('time', 'ttl', 'value')

    def __init__(self, time, ttl, value):
        self.time = time
        self.ttl = ttl
        self.value = value


class CacheDatabase(object):
    """
    Central database of cache values.
    """

    def __init__(self, server):
        self.server = server
        self.log = server.log

        self._db = {}
        self.lock = threading.Lock()

        # start self-cleaning timer
        self.cleanser()

    def cleanser(self):
        self.log('db running cleanser')
        # clean all expired values
        self.ask('')
        # and start again in 30 seconds
        t = threading.Timer(30, self.cleanser)
        t.setDaemon(True)
        t.start()

    def ask(self, key):
        self.log('db ask: %s' % key)
        self.lock.acquire()
        try:
            returning = set()
            expired = set()
            # look for matching keys
            for dbkey, entries in self._db.iteritems():
                if key in dbkey:
                    lastent = entries[-1]
                    # check for removed keys
                    if lastent.value is None:
                        returning.add('%s=' % dbkey)
                        continue
                    # check for expired keys
                    if lastent.ttl:
                        remaining = lastent.time + lastent.ttl - current_time()
                        if remaining <= 0:
                            expired.add(dbkey)
                            returning.add('%s=' % dbkey)
                            continue
                    returning.add('%s=%s' % (dbkey, lastent.value))
        finally:
            self.lock.release()
        for key in expired:
            self.delete(key)
        return returning

    def ask_ts(self, key, time, ttl):
        self.log('db ask_ts: %s, %s, %s' % (key, time, ttl))
        self.lock.acquire()
        try:
            returning = set()
            expired = set()
            # look for matching keys
            for dbkey, entries in self._db.iteritems():
                if key in dbkey:
                    lastent = entries[-1]
                    # check for removed keys
                    if lastent.value is None:
                        returning.add('%s=' % dbkey)
                        continue
                    # check for expired keys
                    if lastent.ttl:
                        remaining = lastent.time + lastent.ttl - current_time()
                        if remaining <= 0:
                            expired.add(dbkey)
                            returning.add('%s=' % dbkey)
                            continue
                        returning.add('%s+%s@%s=%s' %
                                      (lastent.time, lastent.ttl,
                                       dbkey, lastent.value))
                    else:
                        returning.add('%s@%s=%s' % (lastent.time, dbkey,
                                                    lastent.value))
        finally:
            self.lock.release()
        for key in expired:
            self.delete(key)
        return returning

    def tell(self, key, value, time, ttl):
        self.log('db tell: %s, %s, %s, %s' % (key, value, time, ttl))
        send_update = True
        self.lock.acquire()
        try:
            entries = self._db.setdefault(key, [])
            if entries:
                lastent = entries[-1]
                if lastent.value == value and not lastent.ttl:
                    # not a real update
                    send_update = False
            entries.append(Entry(time, ttl, value))
        finally:
            self.lock.release()
        if send_update:
            for client in self.server.connected.values():
                if client.is_active():
                    client.update(key, value, time)

    def delete(self, key):
        self.log('db delete: %s' % key)
        if key not in self._db:
            return
        self.lock.acquire()
        try:
            self._db[key].append(Entry(current_time(), None, None))
        finally:
            self.lock.release()


class CacheServer(object):
    """
    The server class.
    """

    def __init__(self, log):
        self.log = log
        self.defaultport = 14869
        self.clusterlist = ['127.0.0.1', '192.168.2.220']
        self.stoprequest = False
        self.db = CacheDatabase(self)
        self.boundto = None
        self.serversocket = None
        self.serversocket_udp = None
        self.connected = {}  # worker connections
        self.worker = threading.Thread(target=self._worker_thread)
        self.worker.start()

    def _worker_thread(self):
        def bind_to(address, type='tcp'):
            if ':' not in address:
                host = address
                port = int(self.defaultport)
            else:
                host, port = address.split(':')
                port = int(port)
            serversocket = socket.socket(socket.AF_INET,
                type == 'tcp' and socket.SOCK_STREAM or socket.SOCK_DGRAM)
            serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if type == 'udp':
                # we will be able to receive broadcasts
                serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            try:
                serversocket.bind((socket.gethostbyname(host), port))
                if type == 'tcp':
                    serversocket.listen(50) # max waiting connections....
                return serversocket
            except Exception:
                serversocket.close()
                return None             # failed, return None as indicator

        def connect_to(address):
            if ':' not in address:
                host = address
                port = int(self.defaultport)
            else:
                host, port = address.split(':')
                port = int(port)
            # open TCP client socket
            clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            clientsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                clientsocket.connect((socket.gethostbyname(host), port))
                return clientsocket
            except:
                clientsocket.close()
                return None

        # now try to bind to one, include 'MUST WORK' standalone names
        for server in self.clusterlist + [socket.getfqdn(), socket.gethostname()]:
            self.log('server trying to bind to ' + server)
            self.serversocket = bind_to(server)
            if self.serversocket:
                self.boundto = server
                break             # we had success: exit this loop
        self.log('server now bound to %s' % self.boundto)

        # bind UDP broadcast socket
        self.serversocket_udp = bind_to('', 'udp')
        if self.serversocket_udp:
            self.log('server udp-bound to broadcast')

        if not self.serversocket and not self.serversocket_udp:
            self.stoprequest = True
            # print "couldn't bind to any location, giving up!"
            return

        # print 'starting main-loop at %s'%self.boundto
        # now enter main serving loop
        while not self.stoprequest:
            # loop through connections, first to remove dead ones,
            # secondly to try to reconnect
            for addr, client in self.connected.items():
                if client:
                    if not client.is_active(): # dead or stopped
                        if addr in self.clusterlist:
                            self.log('cluster connection to %s died' % addr)
                        else:
                            self.log('client connection from %s died' % addr)
                        client.closedown()
                        client.worker.join() # wait for thread to end
                        del self.connected[addr]
            # check connections to cluster members
            for addr in self.clusterlist:
                if addr != self.boundto and addr not in self.connected:
                    # don't connect to self, only reconnect if not
                    # already connected
                    conn = connect_to(addr)
                    if not conn:
                        continue
                    # connect to cluster member, send QUERY-ALL and
                    # SUBSCRIBE-ALL, also put SUBSCRIBE-ALL into our
                    # input-buffer so we will update the cluster
                    # about local changes...
                    client = CacheWorker(
                        db=self.db, connection=conn, name=addr,
                        initstring='@?\r\n@!\r\n', initdata='@?\r\n@!\r\n')
                    self.connected[addr] = client
                    # print "(re-)connected to clusternode: ",addr, ' syncing'

            # now check for additional incoming connections
            # build list of things to ckeck
            selectlist = []
            if self.serversocket:
                selectlist.append(self.serversocket)
            if self.serversocket_udp:
                selectlist.append(self.serversocket_udp)

            res = select.select(selectlist, [], [], 1)  # timeout 1 second
            if not res[0]:
                continue  # nothing to read -> continue loop
            if self.serversocket in res[0]:
                # TCP connection came in
                conn, addr = self.serversocket.accept()
                addr = 'tcp://%s:%d' % addr
                # print 'new connection from %s'%addr
                # TODO: check addr, currently all are allowed....
                self.connected[addr] = CacheWorker(self.db, conn, name=addr)
            elif self.serversocket_udp in res[0]:
                # UDP data came in
                data, addr = self.serversocket_udp.recvfrom(3072)
                nice_addr = 'udp://%s:%d' % addr
                # print 'new connection from %s' % nice_addr
                # TODO: check addr, currently all are allowed....
                conn = CacheUDPConnection(self.serversocket_udp, addr, self.log)
                self.connected[nice_addr] = CacheWorker(
                    self.db, conn, name=nice_addr, initdata=data)
        self.serversocket.shutdown(socket.SHUT_RDWR)
        self.serversocket.close()
        self.serversocket = None

    def quit(self):
        self.stoprequest = True
        for client in self.connected.values():
            self.log('server closing client %s' % client)
            if client.is_active():
                client.closedown()
        for client in self.connected.values():
            self.log('server waiting for %s' % client)
            client.worker.join()
        print 'server waiting for server'
        self.worker.join()

if __name__ == '__main__':
    def log(x, y=''):
        print x, y
    log('starting server')
    server = CacheServer(log=log)
    def handler(signum, frame):
        log('shutting down...')
        server.quit()
    signal.signal(signal.SIGINT, handler)   # control-c
    signal.signal(signal.SIGTERM, handler)  # terminate
    while not server.stoprequest:
        sleep(1)
    log('server quitting')
    server.worker.join()
    log('server finished')
