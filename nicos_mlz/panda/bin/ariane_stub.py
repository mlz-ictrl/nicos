#!/usr/bin/env python3
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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

import json
import traceback
from random import random

import zmq

ctx = zmq.Context()
rep = ctx.socket(zmq.REP)
rep.bind('tcp://0.0.0.0:11657')
ID = b'ARIANE'


class AI:
    def reset(self, data):
        assert data['mode'] == 'single'
        self.l1, self.l2 = data['limits']
        assert len(self.l1) == len(self.l1) == 2

    def put_result(self, data):
        assert len(data['locs']) == len(data['counts'])
        assert len(data['locs'][0]) == 2

    def get_nextloc(self):
        return [
            self.l1[0] + random() * (self.l1[1] - self.l1[0]),
            self.l2[0] + random() * (self.l2[1] - self.l2[0])
        ]

    def put_problem(self, data):
        pass


def run_service():
    print('ARIANE stub: waiting for requests...')
    ai = AI()

    while True:
        msg = rep.recv_multipart()
        print(f'\n< {msg}')

        try:
            assert len(msg) == 4
            assert msg[0] == ID
            action = msg[2]
            data = json.loads(msg[3].decode())

            if action == b'ping':
                ret_data = {'success': True, 'version': '1.0 (stub)'}
            elif action == b'reset':
                ai.reset(data)
                ret_data = {'success': True}
            elif action == b'next_loc':
                loc = ai.get_nextloc()
                ret_data = {'success': True, 'loc': loc, 'stop': False}
            elif action == b'result':
                ai.put_result(data)
                ret_data = {'success': True}
            elif action == b'problem_locs':
                ai.put_problem(data)
                ret_data = {'success': True}
            elif action == b'heuris_experi_param':
                ret_data = {'success': True, 'level_backgr': 0,
                            'thresh_intens': 1000000}
            elif action == b'stop':
                ret_data = {'success': True}
            else:
                raise ValueError('unknown action')

        except Exception as err:
            traceback.print_exc()
            ret_data = {'success': False, 'error': str(err)}

        ret_msg = [ID, b'', msg[2], json.dumps(ret_data).encode()]
        print(f'> {ret_msg}')
        rep.send_multipart(ret_msg)


if __name__ == '__main__':
    run_service()
