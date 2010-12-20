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

import os
import bsddb
import select
import socket
import threading
from time import time as currenttime, sleep, localtime, strftime, mktime

from nicm import nicos, loggers
from nicm.device import Device, Param
from nicm.utils import listof, existingdir, intrange
from nicm.cache.utils import msg_pattern, line_pattern, DEFAULT_CACHE_PORT, \
     OP_TELL, OP_ASK, OP_WILDCARD, OP_SUBSCRIBE, OP_TELLOLD, Entry, \
     dump_entries, load_entries


class CacheUDPConnection(object):
    """
    An UDP connection to use instead of a TCP connection in the CacheWorker.
    """

    def __init__(self, udpsocket, remoteaddr, log, maxsize=1496):
        self.remoteaddr = remoteaddr
        self.udpsocket = udpsocket
        self.maxsize = maxsize
        self.log = log

    def fileno(self):
        # provide a pseudo-fileno; the actual value doesn't matter as long as
        # this is negative
        return -self.udpsocket.fileno()

    def close(self):
        self.log('UDP: close')

    def shutdown(self, how):
        self.log('UDP: shutdown')

    def recv(self, maxbytes):
        # reading more is not supported
        self.log('UDP: recv')
        return ''

    def send(self, data):
        datalen = len(data)
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

    def __init__(self, db, connection, name='', initstring='', initdata='',
                 loglevel=None):
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

        self.log = nicos.getLogger(name)
        self.log.setLevel(loggers.loglevels[loglevel])

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
                    self.log.info('got empty line, closing connection')
                    self.closedown()
                    return
                ret = self._handle_line(line)
                #self.log.debug('return is %r' % ret)
                if ret:
                    self.writeto(''.join(ret))
                # continue loop with next match
                match = line_pattern.match(data)
            # fileno is < 0 for UDP connections, where select isn't needed
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
            data += newdata
        self.closedown()

    def _handle_line(self, line):
        self.log.debug('handling line: %s' % line)
        match = msg_pattern.match(line)
        if not match:
            # disconnect on trash lines (for now)
            if line:
                self.log.warning('garbled line: %r' % line)
            self.closedown()
            return
        # extract and clean up individual values
        time, ttl, tsop, key, op, value = match.groups()
        key = key.lower()
        value = value or None
        try:
            time = float(time)
        except:
            time = currenttime()
        try:
            ttl = float(ttl)
        except:
            ttl = None
        if tsop == '-' and ttl:
            ttl = ttl - time

        # dispatch operations
        if op == OP_TELL:
            self.db.tell(key, value, time, ttl, self)
        elif op == OP_ASK:
            if ttl:
                return self.db.ask_hist(key, time, time+ttl)
            else:
                return self.db.ask(key, tsop, time, ttl)
        elif op == OP_WILDCARD:
            # both time and ttl are ignored for subscription requests,
            # but the return format changes when the @ is included
            return self.db.ask_wc(key, tsop, time, ttl)
        elif op == OP_SUBSCRIBE:
            # both time and ttl are ignored for subscription requests,
            # but the return format changes when the @ is included
            if tsop:
                self.ts_updates_on.add(key)
            else:
                self.updates_on.add(key)
        elif op == OP_TELLOLD:
            # the server gets a TELLOLD only for cluster subscriptions;
            # these can be ignored since we can figure out timeouts ourselves
            pass

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
        self.log.warning(self, 'other end closed, shutting down')
        self.closedown()
        return False

    def update(self, key, op, value, time, ttl):
        """Check if we need to send the update given."""
        if not self.connection:
            return False
        # make sure line has at least a default timestamp
        for mykey in self.ts_updates_on:
            # do a substring match on key
            if mykey in key:
                if not time:
                    time = currenttime()
                self.log.debug('sending update of %r to %r' % (key, value))
                if ttl is not None:
                    msg = '%s+%s@%s%s%s\r\n' % (time, ttl, key, op, value)
                else:
                    msg = '%s@%s%s%s\r\n' % (time, key, op, value)
                return self.writeto(msg)
        # same for requested updates without timestamp
        for mykey in self.updates_on:
            if mykey in key:
                self.log.debug('sending update of %r to %r' % (key, value))
                return self.writeto('%s%s%s\r\n' % (key, op, value))
        # no update neccessary, signal success
        return True


class CacheDatabase(Device):

    def doInit(self):
        raise NotImplementedError('CacheDatabase is an abstract class')


class MemoryCacheDatabase(CacheDatabase):
    """
    Central database of cache values, keeps everything in memory.
    """

    def doInit(self):
        self._db = {}
        self._lock = threading.Lock()

    def ask(self, key, ts, time, ttl):
        with self._lock:
            if key not in self._db:
                return [key + OP_TELLOLD + '\r\n']
            lastent = self._db[key][-1]
        # check for already removed keys
        if lastent.value is None:
            return [key + OP_TELLOLD + '\r\n']
        # check for expired keys
        if lastent.ttl:
            remaining = lastent.time + lastent.ttl - currenttime()
            op = remaining > 0 and OP_TELL or OP_TELLOLD
            if ts:
                return ['%s+%s@%s%s%s\r\n' % (lastent.time, lastent.ttl,
                                              key, op, lastent.value)]
            else:
                return [key + op + lastent.value]
        if ts:
            return ['%s@%s%s%s\r\n' % (lastent.time, key,
                                       OP_TELL, lastent.value)]
        else:
            return [key + OP_TELL + lastent.value + '\r\n']

    def ask_wc(self, key, ts, time, ttl):
        ret = set()
        with self._lock:
            # look for matching keys
            for dbkey, entries in self._db.iteritems():
                if key not in dbkey:
                    continue
                lastent = entries[-1]
                # check for removed keys
                if lastent.value is None:
                    continue
                # check for expired keys
                if lastent.ttl:
                    remaining = lastent.time + lastent.ttl - currenttime()
                    op = remaining > 0 and OP_TELL or OP_TELLOLD
                    if ts:
                        ret.add('%s+%s@%s%s%s\r\n' % (lastent.time, lastent.ttl,
                                                      dbkey, op, lastent.value))
                    else:
                        ret.add(dbkey + op + lastent.value + '\r\n')
                elif ts:
                    ret.add('%s@%s%s%s\r\n' % (lastent.time, dbkey,
                                               OP_TELL, lastent.value))
                else:
                    ret.add(dbkey + OP_TELL + lastent.value + '\r\n')
        return ret

    def tell(self, key, value, time, ttl, from_client):
        if value is None:
            # deletes cannot have a TTL
            ttl = None
        send_update = True
        with self._lock:
            entries = self._db.setdefault(key, [])
            if entries:
                lastent = entries[-1]
                if lastent.value == value and not lastent.ttl:
                    # not a real update
                    send_update = False
            # never cache more than a single entry, memory fills up too fast
            entries[:] = [Entry(time, ttl, value)]
        if send_update:
            for client in self._server._connected.values():
                if client is not from_client and client.is_active():
                    client.update(key, OP_TELL, value, time, ttl)


class DbCacheDatabase(MemoryCacheDatabase):
    """Cache database that keeps history in bsddb stores."""

    parameters = {
        'storepath': Param('Directory where history stores should be saved',
                           type=str, mandatory=True),
        'maxcached': Param('Maximum number of entries cached in memory',
                           type=int, default=200),
        'granularity': Param('For debugging purposes', type=intrange(3, 7),
                             default=3),
    }

    intervals = {
        3: 86400,
        4: 3600,
        5: 60,
        6: 1,
    }

    def doInit(self):
        self._db = {}
        self._stores = {}
        self._arctime = {}
        self._lock = threading.Lock()
        self._max = self.maxcached
        # the granularity determines how many elements of the time tuple make up
        # the key for a single database file; usually it is 3, meaning that
        # there is one database file per day (values > 3 are only supported for
        # debugging the database class)
        self._gran = self.granularity
        self._storefmt = '%04d' + '-%02d' * (self._gran - 1)
        # keep open two stores: this day's, and the previous day's
        time = currenttime()
        self._currday = localtime(time)[:self._gran]
        self._prevday = localtime(time - self.intervals[self._gran])[:self._gran]
        self._midnight = mktime(self._currday + (0,) * (9 - self._gran))
        self._nextmidnight = self._midnight + self.intervals[self._gran]
        self._store_lock = threading.Lock()
        with self._store_lock:
            self._currstore = self._open_store(self._currday)
            self._prevstore = self._open_store(self._prevday)
        # read the last entry for each key from disk
        nkeys = 0
        with self._lock:
            with self._store_lock:
                for key in self._currstore:
                    entries = load_entries(self._currstore[key])[-1:]
                    if entries:
                        self._db[key] = entries
                        self._arctime[key] = entries[-1].time
                        nkeys += 1
        self.printinfo('loaded %d keys from store' % nkeys)

    def doShutdown(self):
        # write remaining unarchived entries to disk
        nentries = 0
        with self._lock:
            with self._store_lock:
                for key, entries in self._db.iteritems():
                    self._archive(key, entries)
                    nentries += len(entries)
        self.printinfo('archived %d entries on shutdown' % nentries)
        with self._store_lock:
            self._close_store(self._currday)
            self._close_store(self._prevday)

    def _open_store(self, ymd):
        if ymd in self._stores:
            self._stores[ymd][1] += 1
            self.printdebug('incremented use count for store %s' % (ymd,))
            return self._stores[ymd][0]
        path = os.path.join(self.storepath, self._storefmt % ymd)
        db = bsddb.hashopen(path, 'c')
        self.printdebug('opened new store for %s' % (ymd,))
        self._stores[ymd] = [db, 1]
        return db

    def _close_store(self, ymd):
        info = self._stores[ymd]
        info[1] -= 1
        self.printdebug('decremented use count for store %s' % (ymd,))
        if info[1] == 0:
            db = self._stores.pop(ymd)[0]
            db.sync()
            db.close()
            self.printdebug('closed store for %s' % (ymd,))

    def _archive(self, key, entries):
        """Archive entries to the store(s).  Must be called with the store
        lock held.
        """
        # midnight is past: change stores
        if currenttime() > self._nextmidnight:
            newday = localtime()[:self._gran]
            # close previous day's store
            self._close_store(self._prevday)
            # this day's store is now previous day's
            self._prevstore = self._currstore
            self._currstore = self._open_store(newday)
            # set the days and midnight time correctly
            self._prevday = self._currday
            self._currday = newday
            self._midnight = mktime(self._currday + (0,) * (9 - self._gran))
            self._nextmidnight = self._midnight + self.intervals[self._gran]
        # divide the entries in two lists: those belonging to the previous
        # day, and those for the current day
        prev, curr = [], []
        midnight = self._midnight
        arctime = self._arctime.get(key, 0)
        for entry in entries:
            if entry.time <= arctime:
                continue
            elif entry.time < midnight:
                prev.append(entry)
            else:
                curr.append(entry)
        # dump them into their respective stores
        if prev:
            self._prevstore[key] = \
                self._prevstore.get(key, '') + dump_entries(prev)
            self._prevstore.sync()
        self._currstore[key] = \
            self._currstore.get(key, '') + dump_entries(curr)
        self._currstore.sync()
        self._arctime[key] = entries[-1].time
        self.printdebug('archived %d+%d entries for key %s' %
                        (len(prev), len(curr), key))

    # ask and ask_wc inherited from MemoryCacheDatabase

    def ask_hist(self, key, t1, t2):
        ret = []
        with self._lock:
            if key not in self._db:
                return []
            entries = self._db[key]
        if t1 < entries[0].time:
            # need to check in database files
            #with self._store_lock:
            #    self.
            pass
        for entry in entries:
            if t1 <= entry.time < t2:
                if entry.ttl:
                    ret.append('%s+%s@%s%s%s\r\n' %
                               (entry.time, entry.ttl, key,
                                OP_TELLOLD, entry.value))
                else:
                    ret.append('%s@%s%s%s\r\n' % (entry.time, key,
                                                  OP_TELLOLD, entry.value))
        return ret

    def tell(self, key, value, time, ttl, from_client):
        if value is None:
            # deletes cannot have a TTL
            ttl = None
        send_update = True
        with self._lock:
            entries = self._db.setdefault(key, [])
            if entries:
                lastent = entries[-1]
                if lastent.value == value and not lastent.ttl:
                    # not a real update
                    send_update = False
            entries.append(Entry(time, ttl, value))
            if len(entries) > self._max or ttl is None:
                # if ttl is None, the value should be stored immediately
                with self._store_lock:
                    self._archive(key, entries)
                    del entries[:-1]
        if send_update:
            for client in self._server._connected.values():
                if client is not from_client and client.is_active():
                    client.update(key, OP_TELL, value, time, ttl)


class CacheServer(Device):
    """
    The server class.
    """

    parameters = {
        'defaultport': Param('The default server port',
                             type=int, default=DEFAULT_CACHE_PORT),
        'clusterlist': Param('List of cluster connections', type=listof(str)),
    }

    attached_devices = {
        'db': CacheDatabase,
    }

    def doInit(self):
        self._stoprequest = False
        self._boundto = None
        self._serversocket = None
        self._serversocket_udp = None
        self._connected = {}  # worker connections
        self._adevs['db']._server = self

    def start(self):
        self._worker = threading.Thread(target=self._worker_thread)
        self._worker.start()

    def _worker_thread(self):
        self.printinfo('server starting')

        def bind_to(address, type='tcp'):
            if ':' not in address:
                host = address
                port = self.defaultport
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
                port = self.defaultport
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
            self.printdebug('trying to bind to ' + server)
            self._serversocket = bind_to(server)
            if self._serversocket:
                self._boundto = server
                break             # we had success: exit this loop

        # bind UDP broadcast socket
        self._serversocket_udp = bind_to('', 'udp')
        if self._serversocket_udp:
            self.printinfo('udp-bound to broadcast')

        if not self._serversocket and not self._serversocket_udp:
            self._stoprequest = True
            self.printerror("couldn't bind to any location, giving up!")
            return

        self.printinfo('starting main-loop bound to %s' % self._boundto)
        # now enter main serving loop
        while not self._stoprequest:
            # loop through connections, first to remove dead ones,
            # secondly to try to reconnect
            for addr, client in self._connected.items():
                if client:
                    if not client.is_active(): # dead or stopped
                        if addr in self.clusterlist:
                            self.printwarning('cluster connection to '
                                              '%s died' % addr)
                        else:
                            self.printinfo('client connection from '
                                           '%s died' % addr)
                        client.closedown()
                        client.worker.join() # wait for thread to end
                        del self._connected[addr]
            # check connections to cluster members
            for addr in self.clusterlist:
                if addr != self._boundto and addr not in self._connected:
                    # don't connect to self, only reconnect if not
                    # already connected
                    conn = connect_to(addr)
                    if not conn:
                        continue
                    # connect to cluster member, send QUERY-ALL and
                    # SUBSCRIBE-ALL, also put SUBSCRIBE-ALL into our
                    # input-buffer so we will update the cluster
                    # about local changes...
                    initstr = '@%s\r\n@%s\r\n' % (OP_WILDCARD, OP_SUBSCRIBE)
                    client = CacheWorker(
                        db=self._adevs['db'], connection=conn, name=addr,
                        initstring=initstr, initdata=initstr,
                        loglevel=self.loglevel)
                    self._connected[addr] = client
                    self.printinfo('(re-)connected to clusternode %s, '
                                   'syncing' % addr)

            # now check for additional incoming connections
            # build list of things to ckeck
            selectlist = []
            if self._serversocket:
                selectlist.append(self._serversocket)
            if self._serversocket_udp:
                selectlist.append(self._serversocket_udp)

            res = select.select(selectlist, [], [], 1)  # timeout 1 second
            if not res[0]:
                continue  # nothing to read -> continue loop
            if self._serversocket in res[0] and not self._stoprequest:
                # TCP connection came in
                conn, addr = self._serversocket.accept()
                addr = 'tcp://%s:%d' % addr
                self.printinfo('new connection from %s' % addr)
                # TODO: check addr, currently all are allowed....
                self._connected[addr] = CacheWorker(
                    self._adevs['db'], conn, name=addr, loglevel=self.loglevel)
            elif self._serversocket_udp in res[0] and not self._stoprequest:
                # UDP data came in
                data, addr = self._serversocket_udp.recvfrom(3072)
                nice_addr = 'udp://%s:%d' % addr
                self.printinfo('new connection from %s' % nice_addr)
                # TODO: check addr, currently all are allowed....
                conn = CacheUDPConnection(self._serversocket_udp, addr,
                                          log=self.printdebug)
                self._connected[nice_addr] = CacheWorker(
                    self._adevs['db'], conn, name=nice_addr, initdata=data,
                    loglevel=self.loglevel)
        self._serversocket.shutdown(socket.SHUT_RDWR)
        self._serversocket.close()
        self._serversocket = None

    def wait(self):
        while not self._stoprequest:
            sleep(1)
        self._worker.join()

    def quit(self):
        self.printinfo('quitting...')
        self._stoprequest = True
        for client in self._connected.values():
            self.printinfo('closing client %s' % client)
            if client.is_active():
                client.closedown()
        for client in self._connected.values():
            self.printinfo('waiting for %s' % client)
            client.worker.join()
        self.printinfo('waiting for server')
        self._worker.join()
        self.printinfo('server finished')
