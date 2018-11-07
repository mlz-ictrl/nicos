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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#   Artur Glavic <artur.glavic@psi.ch>
#
# *****************************************************************************

from __future__ import absolute_import, division, print_function

from nicos.core import HasCommunication, Param
from nicos.core.params import host
from nicos.utils import tcpSocketContext


class MoxaCommunicator(HasCommunication):
    """Implements communication to Moxa terminal server.
    """

    parameters = {
        'hostport': Param('Host and port of Moxa device', type=host()),
        'timeout': Param('The timeout for the communication', type=float,
                         settable=True, default=1.0),
        'terminator': Param('Command terminator', type=str, default='\r\n',
                            userparam=False, settable=False)
    }

    def _command_pre_send(self, sock):
        """This function is executed before sending the command. The subclasses
        should implement this method if something is to be executed after
        connecting to socket and before sending the command.
        """
        pass

    def _command_post_send(self, sock):
        """This function is executed after sending the command. The subclasses
        should implement this method if for e.g. the reply is to be checked
        before returning the output.
        """
        pass

    def _command_tty(self, cmd, has_output=True):
        # open TCP connection to Moxa terminal server and close after execution
        dp = self.hostport.split(':')[-1]
        with tcpSocketContext(self.hostport, dp, timeout=self.timeout) as sock:
            self._command_pre_send(sock)
            sock.send('%s%s' % (cmd, self.terminator))
            self._command_post_send(sock)
            if has_output:
                return self._com_readline(sock)

    def _com_readline(self, sock):
        out = sock.recv(1)
        while out[-1] != '\n':
            out += sock.recv(1)
        return out

    def _flush_tty(self, sock=None):
        if sock is None:
            # open TCP connection to Moxa terminal server and close after
            dp = self.hostport.split(':')[-1]
            with tcpSocketContext(self.hostport, dp, timeout=0.25) as lsock:
                return lsock.recv(1024)
        else:
            sock.settimeout(0.25)
            return sock.recv(1024)
