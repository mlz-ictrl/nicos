#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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

"""Test the text client."""

from __future__ import print_function

import time

import mock

from nicos.clients.cli import NicosCmdClient, main as cli_main

from test.utils import daemon_addr


class CmdClient(NicosCmdClient):

    interact = None
    test_output = []
    test_status = ['idle']

    def readline(self, prompt, add_history=True):
        self.put(prompt)
        try:
            cmd = next(self.interact)
        except StopIteration:
            assert False, 'ran out of commands in input'
        del self.test_output[:]
        return cmd

    def put(self, string):
        self.test_output.append(string)

    def put_error(self, string):
        self.test_output.append('ERROR ' + string)

    def put_client(self, string):
        self.test_output.append('# ' + string)

    def set_status(self, status):
        self.test_status[0] = status
        NicosCmdClient.set_status(self, status)


def test_textclient(daemon):
    def dialog(out, sts):
        def has_msg(msg):
            return any(msg in line for line in out)

        def has_msg_wait(msg, timeout=5):
            start = time.time()
            while not any(msg in line for line in out):
                time.sleep(0.01)
                if time.time() > start + timeout:
                    print('messages:', out)
                    return False
            return True

        def wait_idle(timeout=5):
            start = time.time()
            while sts[0] != 'idle':
                time.sleep(0.01)
                if time.time() > start + timeout:
                    assert False, 'idle wait timeout'

        # messages after connection
        assert has_msg_wait('# Loaded setups:')
        assert has_msg('# Connected to')

        yield '/log 100'
        assert has_msg('# Printing 100 previous messages.')
        assert has_msg('setting up NICOS')
        assert has_msg('# End of messages.')

        yield '/help'
        assert has_msg('# This is the NICOS command-line client')

        yield 'NewSetup("daemontest")'
        assert has_msg_wait('setups loaded: daemontest')

        wait_idle()
        yield '/sim read()'
        assert has_msg_wait('# Simulated minimum runtime')
        assert has_msg('dm1')
        assert has_msg('dm2')

        yield 'read()'
        assert has_msg_wait('dm2')
        assert has_msg('dm1')

        wait_idle()
        yield 'help(read)'
        assert has_msg_wait('Help on the read command')

        wait_idle()
        yield 'set(dm2, "speed", 1); maw(dm2, 25)'
        assert has_msg_wait('moving to')
        yield 'maw(dm2, 50)'
        assert has_msg('# A script is already running')
        yield 'Q'  # queue
        assert has_msg('# Command queued')

        time.sleep(0.1)  # wait for the new request event to arrive
        yield '/pending'
        assert has_msg('# Showing pending')
        assert has_msg('maw(dm2, 50)')

        yield '/where'
        assert has_msg('# Printing current script')
        assert has_msg('--->')
        assert has_msg('maw(dm2, 25)')

        yield '/cancel *'
        assert has_msg_wait('removed from queue')
        assert has_msg('# No scripts or commands')

        yield '/trace'
        assert has_msg_wait('# End of stacktrace')
        assert has_msg('in maw')

        yield '/spy'
        yield 'dm1()'
        assert has_msg_wait('-> 0.0')
        yield 'xxxxx'
        assert has_msg_wait('cannot be evaluated')
        yield '/spy'

        yield '/stop'
        assert has_msg('Stop request')
        assert has_msg('Your choice?')
        yield 'S'  # stop immediately
        assert has_msg_wait('all devices stopped')

        yield '/disconnect'
        assert has_msg_wait('# Disconnected from server')

        yield '/quit'

    CmdClient.interact = dialog(CmdClient.test_output,
                                CmdClient.test_status)
    with mock.patch('nicos.clients.cli.NicosCmdClient', CmdClient):
        cli_main(['', 'guest:guest@' + daemon_addr])
