#!/usr/bin/env python3
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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
#
# *****************************************************************************

"""
A benchmarking tool for the NICOS cache.
"""

import argparse
import random
import socket
import threading
import time


class Benchmarker:
    def udp(self):
        mains, _subs = self.connect(1)
        mains[0].sendall(b''.join(self.all_msg))
        mains[0].sendall(b'ben/%s/k*\n' % self.rnd_key)
        msg_set = self.recvall(mains[0])
        assert msg_set == self.all_set

        t1 = time.time()
        s = self.create_socket(socket.SOCK_DGRAM)
        s.sendall(b'ben/%s/k*\n' % self.rnd_key)
        msg_set = self.recvall(s)
        assert msg_set == self.all_set
        return t1

    def single_writer(self):
        mains, subs = self.connect(1)

        t1 = time.time()
        mains[0].sendall(b''.join(self.all_msg))
        for s in subs:
            msg_set = self.recvall(s)
            assert msg_set == self.all_set

        mains[0].sendall(b'ben/%s/k*\n' % self.rnd_key)
        msg_set = self.recvall(mains[0])
        assert msg_set == self.all_set
        return t1

    def multi_writer(self):
        mains, subs = self.connect(self.nclients)

        t1 = time.time()
        perclient = self.nkeys // self.nclients
        for i, main in enumerate(mains):
            threading.Thread(target=lambda i=i, m=main: m.sendall(
                b''.join(self.all_msg[i*perclient:(i+1)*perclient]))).start()
        for s in subs:
            msg_set = self.recvall(s)
            assert msg_set == self.all_set
        return t1

    def multi_writer_with_ttl(self):
        mains, subs = self.connect(self.nclients)

        t1 = time.time()
        perclient = self.nkeys // self.nclients
        for i, main in enumerate(mains):
            threading.Thread(target=lambda i=i, m=main: m.sendall(
                b''.join(self.all_msg_with_ttl[i*perclient:(i+1)*perclient]))
            ).start()
        for s in subs:
            msg_set = self.recvall(s)
            assert msg_set == self.all_set
        return t1

    def ask_only(self):
        mains, _subs = self.connect(1, 0)

        mains[0].sendall(b''.join(self.all_msg))
        mains[0].sendall(b'ben/%s/k*\n' % self.rnd_key)
        msg_set = self.recvall(mains[0])
        assert msg_set == self.all_set
        t1 = time.time()
        mains[0].sendall(b'ben/%s/k*\n' % self.rnd_key)
        msg_set = self.recvall(mains[0])
        assert msg_set == self.all_set
        return t1

    def ask_history(self):
        mains, _subs = self.connect(self.nclients, 0)

        hist_msg = [b'%.1f@ben/%s/k000000=%d\n' % (i+0.1, self.rnd_key, i)
                    for i in range(self.nkeys)]
        mains[0].sendall(b''.join(hist_msg))
        mains[0].sendall(b'ben/%s/k*\n' % self.rnd_key)
        expect = b'ben/%s/k000000=%d\n' % (self.rnd_key, self.nkeys - 1)
        msg_set = self.recvall(mains[0], len(expect))
        assert msg_set == set([expect.strip()])
        t1 = time.time()
        for main in mains:
            main.sendall(b'0-%f@ben/%s/k000000?\n' % (t1 + 10, self.rnd_key))
        for main in mains:
            msg_set = self.recvall(main, len(b''.join(hist_msg)))
            assert msg_set == set(m.strip() for m in hist_msg)
        return t1

    benches = {n: f for (n, f) in locals().items() if hasattr(f, '__name__')}

    def create_socket(self, tp=socket.SOCK_STREAM):
        s = socket.socket(socket.AF_INET, tp)
        s.connect((self.cache_host, 14869))
        return s

    def connect(self, nmain, nsub=None):
        mains = []
        for _ in range(nmain):
            mains.append(self.create_socket())
        subs = []
        for _ in range(self.nclients if nsub is None else nsub):
            sub = self.create_socket()
            sub.sendall(b'ben/%s/k:\n' % self.rnd_key)
            subs.append(sub)
        time.sleep(0.2)
        return mains, subs

    def recvall(self, s, length=None):
        res = b''
        start = time.time()
        length = length or len(b''.join(self.all_msg))
        while len(res) < length and time.time() - start < 10:
            res += s.recv(length)
        return set(res.splitlines())

    def main(self):
        parser = argparse.ArgumentParser(
            description='Run one of several NICOS cache benchmarks.'
        )
        parser.add_argument('-c', action='store', default='localhost',
                            metavar='HOST', help='cache host')
        parser.add_argument('-n', action='store', type=int, default=10000,
                            metavar='KEYS', help='number of keys')
        parser.add_argument('-s', action='store', type=int, default=10,
                            metavar='SUBSCRIBERS', help='number of clients')
        parser.add_argument('benchmark', action='store', type=str,
                            choices=self.benches)
        opts = parser.parse_args()

        self.cache_host = opts.c
        self.nclients = opts.s
        # make an even number of keys per client
        self.nkeys = opts.n // opts.s * opts.s

        self.rnd_key = b'%06x' % random.getrandbits(24)
        self.all_msg = [
            b'ben/%s/k%06d=%s\n' % (self.rnd_key, i, self.rnd_key)
            for i in range(self.nkeys)
        ]
        self.all_msg_with_ttl = [
            b'+5@ben/%s/k%06d=%s\n' % (self.rnd_key, i, self.rnd_key)
            for i in range(self.nkeys)
        ]
        self.all_set = set(s.strip() for s in self.all_msg)

        fn = getattr(self, opts.benchmark)
        t1 = fn()
        t2 = time.time()
        print(f'{opts.benchmark}: {self.nkeys} keys, '
              f'{self.nclients} subscribers: {t2 - t1:.4} sec')


if __name__ == '__main__':
    Benchmarker().main()
