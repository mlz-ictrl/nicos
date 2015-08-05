#!/usr/bin/env python
import re
import sys
import socket
import inspect
import optparse
from math import ceil

# default cache server to use when no arguments are given
CACHES = ["localhost"]

def myround(f):
    """round x.xxxxxx to x.x format for all decades

    i.e. 0.00123 -> 0.0013, 12345 -> 13000
    (rounds away from zero!)
    values less than 1e-38 get transformed to 0!
    """
    # too small
    if abs(f) < 1e-38:
        return f
    # remove decades
    shift = 0
    while abs(f)<1:
        shift += 1
        f *= 10
    while abs(f)>10:
        shift -= 1
        f /= 10
    # f is now between 1 and 10
    # round 10*f up to next integer
    s = -1 if f < 0 else +1
    f = 0.1 * ceil(abs(f)*10) * s
    # re-apply decades
    while shift > 0:
        shift -= 1
        f /= 10
    while shift < 0:
        shift += 1
        f *= 10
    return f

# THE FIXES...

def fix_precision(slope=float, precision=float):
    minprec = myround(2. / abs(slope))
    if precision < minprec:
        return dict(precision=minprec)

def fix_pollinterval_and_maxage(pollinterval=float, maxage=float):
    res = {}
    if pollinterval < 1:
        res['pollinterval'] = pollinterval = 1.
    minmaxage = myround(float(2 * pollinterval + ceil(pollinterval / 12.5)))
    if maxage < minmaxage:
        res['maxage'] = maxage = minmaxage
    return res


# Framwork

class CClient(object):
    '''very crude and basic cache client'''
    msg_pattern = re.compile(r'''
    ^ (?:
      \s* (?P<time>\d+\.?\d*)?                   # timestamp
      \s* (?P<ttlop>[+-]?)                       # ttl operator
      \s* (?P<ttl>\d+\.?\d*(?:[eE][+-]?\d+)?)?   # ttl
      \s* (?P<tsop>@)                            # timestamp mark
    )?
    \s* (?P<key>[^=!?:*$]*?)                     # key
    \s* (?P<op>[=!?:*$~])                        # operator
    \s* (?P<value>[^\r\n]*?)                     # value
    \s* $
    ''', re.X)

    def __init__(self, cachehost, cacheport = 14869):
        if ':' in cachehost:
            cachehost, cacheport = cachehost.split(':', 1)
        self._cachehost = cachehost
        self._cacheport = int(cacheport)
        self._socket = None
        self._connect()

    def __del__(self):
        self._disconnect()

    def _reconnect(self):
        if self._socket:
            self._disconnect()
        self._connect()

    def _disconnect(self, socket=socket):
        if self._socket is None:
            return
        try:
            self._socket.shutdown(socket.SHUT_RDWR)
        except socket.error:
            pass
        try:
            self._socket.close()
        except socket.error:
            pass
        self._socket = None

    def _connect(self):
        # open socket and set options
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((self._cachehost, self._cacheport))
        self._socket = s

    def _comm(self, request):
        self._socket.sendall(request + '\n###?\n') # always put a end-of-list marker
        data = ''
        reloop = False
        while True:
            try:
                newdata = self._socket.recv(1024)
            except socket.timeout:
                return
            if newdata:
                data += newdata
                while '\n' in data:
                    l, data = data.split('\n', 1)
                    if l == '###!':
                        return
                    yield l
                continue
            if reloop:
                return
            reloop = True

    def _split(self, line):
        '''splits a cache-response-line into components, defaulting to '' for missing parts.'''
        m = self.msg_pattern.match(line)
        if m:
            g = m.groupdict()
            if g['tsop'] == '@':
                _ts = g['time']
                _ttl = (g['ttl'] - _ts) if g['ttlop'] == '-' else g['ttl']
            else:
                _ts = None
                _ttl = None
            _key = g['key']
            _op = g['op']
            _value = g['value']
            return _ts, _ttl, _key, _op, _value

    def devices(self):
        '''iterator over all known devices'''
        for line in self._comm('/value*'):
            if line.startswith('nicos'):
                _, dev, key = line.split('/', 2)
                if key.startswith('value') and key[5] in '!=':
                    yield dev

    def querykey(self, device=None, key=None):
        '''asks about the most recent value of a device.key'''
        if device is not None:
            key = 'nicos/%s/%s' % (device, key)
        for line in self._comm(key + '?'):
            if line.startswith(key):
                _op = line[len(key)]
                value = line[len(key) + 1:]
        if value:
            return eval(value)

    def querykeys(self, device=None, key=None):
        '''asks about the most recent valuea of a all subkeys of device'''
        if device is not None:
            key = 'nicos/%s/' % device
        for line in self._comm(key + '*'):
            _ts, _ttl, _key, _op, _value = self._split(line)
            if _key.startswith(key):
                yield _ts, _ttl, _key.split('/'), _op, _value

    def set(self, device=None, key=None, timestamp=None, ttl=None, value=Ellipsis):
        '''send a new cache-entry'''
        if device is not None:
            key = 'nicos/%s/%s' % (device, key)
        request = []
        if timestamp:
            request.append('%.3f' % timestamp)
            if ttl:
                request.append('+%.3f' % ttl)
            request.append('@')
        request.append(key)
        if value is Ellipsis:
            request.append('!')
        else:
            request.append('=%s' % value.strip())
        for _result in self._comm(''.join(request)):
            pass

    def apply(self, dryrun, verbose, *fixes):
        '''apply a fix to all matching devices in the cache'''
        if verbose:
            print "Querying list of devices"
        devlist = list(self.devices())
        if verbose:
            print "Checking Devices..."
        for dev in devlist:
            if verbose:
                print dev, '\r',
            for fix in fixes:
                # ask fix about required keys and types
                argspec = inspect.getargspec(fix)
                keys = argspec.args
                types = argspec.defaults
                if len(keys) != len(types):
                    print "Can not apply fix", fix.__name__, "not all argumens have types as default!"
                # ask cache about the values of the keys
                args = [self.querykey(dev, k) for k in keys]
                if None in args:
                    # not all required keys are defined for this device -> continue with next
                    continue
                # try to convert
                try:
                    args = [t(k) for k, t in zip(args, types)]
                except Exception as e:
                    print fix.__name__, e, args
                    continue
                # ask fix what it wants to fix
                res = fix(*args)
                if res:
                    if not isinstance(res, dict):
                        print "Error: a fix should return a DICT of the fixed key:value pairs!"
                        continue
                    print "Would fix" if dryrun else "FIXING", fix.__name__,'for device %s :' % dev
                    for k, a in zip(keys, args):
                        print '\t',k,'=', repr(a)
                    print "\t\t => ", res
                    for k, v in res.items():
                        if not dryrun:
                            self.set(dev, k, value=repr(v))

if __name__ == '__main__':
    parser = optparse.OptionParser(usage='usage: %prog [options] cachesrv:cacheport')
    parser.add_option('-F', '--really-fix', dest='dryrun', action='store_false',
                      help='opposite of -n, really perform the fixes!', default=True)
    parser.add_option('-n', '--dry-run', dest='dryrun', action='store_true',
                      help='Only show what would be changed (default)', default=True)
    parser.add_option('-v', '--verbose', dest='verbose', action='store_true',
                      help='show additional information', default=False)
    parser.add_option('-c', '--cache-srv', dest='caches', action='append',
                      help='connect to this cache-server:cache-port, can be specified multiple times', default=[])

    opts, restargs = parser.parse_args()

    for arg in restargs:
        if '.' in arg or ':' in arg:
            opts.caches.append(arg)
            continue
        parser.print_help()
        print
        print 'fix_cache_entries.py: error: no such option:', arg
        sys.exit(2)

    fixes = [f for (n, f) in globals().items() if n.startswith('fix_')]
    for cache in opts.caches or CACHES:  # fallback to default
        print "Checking", cache, 'in', 'dryrun' if opts.dryrun else 'real', 'mode'
        c = CClient(cache)
        c.apply(opts.dryrun, opts.verbose, *fixes)
