#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2014 by the NICOS contributors (see AUTHORS)
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
#   Pascal Neubert <pascal.neubert@frm2.tum.de>
#
# *****************************************************************************

import sys, socket, select

class CacheAccess(object):

    def __init__(self):
        self._connected = False
        self._sock = None
        self._timeout = 1.0
        self.entries = list()
        self._data = ''

    def setTimeout(self, time):
        """ Sets the timeout """
        self._timeout = time

    def connectToServer(self, ip, port, useTCP, attempts):
        """ Attempts to connect to a cache server """
        self._connected = False
        if useTCP:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            address = socket.gethostbyname(str(ip))
            self._sock.connect((address, port))
        except socket.error:
            return
        except socket.gaierror:
            return
        self._sock.setblocking(False)
        self._connected = True

    def requestFiltered(self, filterKey='', withTimeStamp = False):
        """
        Requests certain data from the respective cache server and saves it
        local.
        """
        self.entries = list()
        request = ''
        if withTimeStamp:
            request = '@'
        request += '*%s' % filterKey
        if filterKey:
            request += '*'
        request += '?\n'
        self._sock.send(request)
        self._data = ''
        while select.select([self._sock], [], [], self._timeout)[0]:
            self._data += self._sock.recv(select.PIPE_BUF)
        lines = self._data.splitlines(True)
        self._data = lines[-1:]
        for lineNum in range(len(lines[:-1])):
            self.entries.append(lines[lineNum])
        return self.entries

    def setKeyValue(self, key, value, ttl='', timeStamp=''):
        """ Sets the value of a key. """
        data = ''
        msg = ''
        if timeStamp != '' or ttl != '':
            if timeStamp != '':
                msg += str(timeStamp)
            if ttl != '':
                msg += str(ttl)
            msg += '@'
        msg += str(key) + '=' + str(value) + '\n'
        self._sock.send(msg)
        while select.select([self._sock], [], [], self._timeout)[0]:
            data += self._sock.recv(1)
        expData = str(key) + '=' + str(value) + '\n'
        if data == expData:
            return 0
        return 1

    def getKeyValue(self, key, withTimeStamp = False):
        """ Gets the value of a key. """
        data = ''
        if withTimeStamp:
            self._sock.send('@' + key + '?\n')
        else:
            self._sock.send(key + '?\n')
        while select.select([self._sock], [], [], self._timeout)[0]:
            data += self._sock.recv(select.PIPE_BUF)
        return data

    def subscribeKey(self, key):
        """ Subscribe to a key. """
        self._sock.send(key + ':')

    def closeConnection(self):
        """ Close the connection. """
        self._sock.setblocking(True)
        self._sock.close()
        self._connected = False

    def isConnected(self):
        """ Check if the cache access is connected to a server. """
        return self._connected

    def getTimeStamp(self, entry):
        """ Returns only the time stamp part from the given cache entry. """
        if entry.find('-') >= 0:
            return entry[:entry.find('-')]
        elif entry.find('+') >= 0:
            return entry[:entry.find('+')]
        else:
            return entry[:entry.find('@')]

    def getTTL(self, entry):
        """ Returns only the time to live part from the given cache entry. """
        if entry.find('-') >= 0:
            return entry[entry.find('-'):entry.find('@')]
        elif entry.find('+') >= 0:
            return entry[entry.find('+'):entry.find('@')]
        else:
            return ''

def main(argv = None):
    if not argv:
        argv = sys.argv
    cacheAccess = CacheAccess()
    cacheAccess.setTimeout(1.0)
    cacheAccess.connectToServer('127.0.0.1', 14869, True, 5)
    res = cacheAccess.requestFiltered()[0]
    root = res[:res.find('=')][:res[:res.find('=')].find('/')]
    print root
    cacheAccess.closeConnection()


if __name__ == '__main__':
    sys.exit(main(sys.argv))
