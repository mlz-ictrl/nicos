# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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
#   Mark Koennecke, <mark.koennecke@psi.ch>
#
# *****************************************************************************

import copy

import numpy as np
from IPython.core.magic import Magics, line_magic, magics_class, \
    needs_local_scope

from nicos.clients.base import ConnectionData, NicosClient
from nicos.protocols.daemon import STATUS_IDLE, STATUS_IDLEEXC
from nicos.utils.loggers import ACTION, INPUT

EVENTMASK = ('watch', 'datapoint', 'datacurve',
             'clientexec')


class IpythonNicosClient(NicosClient):

    livedata = {}
    status = 'idle'

    def signal(self, name, data=None, exc=None):
        accept = ['message', 'processing', 'done']
        if name in accept:
            self.log_func(name, data)
        elif name == 'livedata':
            converted_data = []
            for desc, ardata in zip(data['datadescs'], exc):
                npdata = np.frombuffer(ardata,
                                       dtype=desc['dtype'])
                npdata = npdata.reshape(desc['shape'])
                converted_data.append(npdata)
            self.livedata[data['det'] + '_live'] = converted_data
        elif name == 'status':
            status, _ = data
            if status in (STATUS_IDLE, STATUS_IDLEEXC):
                self.status = 'idle'
            else:
                self.status = 'run'
        else:
            if name != 'cache':
                # print(name, data)
                pass

    def command(self, line):
        com = '%s' % line.strip()
        if self.status == 'idle':
            self.run(com)
            return com
        return None

    def connect(self, conndata, eventmask=None):
        NicosClient.connect(self, conndata, eventmask)
        if self.daemon_info.get('protocol_version') < 22:
            raise RuntimeError('incompatible nicos server')


@magics_class
class Nicos(Magics):

    def __init__(self, shell):
        # You must call the parent constructor
        Magics.__init__(self, shell)
        self.message_queue = []
        self.cli = IpythonNicosClient(self.log)

    def log(self, name, txt):
        self.message_queue.append((name, txt))

    def print_queue(self):
        for msg in self.message_queue:
            print(msg[1])
        self.message_queue = []

    def connect(self, line):
        data = line.split()
        if len(data) < 5:
            print('Not enough data to connect, need host port user password')
            return
        con = ConnectionData(data[1], data[2], data[3], data[4])
        self.cli.connect(con, eventmask=EVENTMASK)
        state = self.cli.ask('getstatus')
        self.cli.signal('status', state['status'])
        self.print_queue()
        if self.cli.isconnected:
            print('Successfully connected to %s' % data[1])
        else:
            print('Failed to connect to %s' % data[1])

    def processCommand(self, line):
        start_detected = False
        ignore = [ACTION, INPUT]
        reqID = None
        testcom = self.cli.command(line)
        if not testcom:
            return 'NICOS is busy, cannot send commands'
        while True:
            if self.message_queue:
                # own copy for thread safety
                work_queue = copy.deepcopy(self.message_queue)
                self.message_queue = []
                for name, message in work_queue:
                    if name == 'processing':
                        if message['script'] == testcom:
                            start_detected = True
                            reqID = message['reqid']
                        continue
                    if name == 'done' and message['reqid'] == reqID:
                        return
                    if message[2] in ignore:
                        continue
                    if message[0] != 'nicos':
                        messagetxt = message[0] + ' ' + message[3]
                    else:
                        messagetxt = message[3]
                    if start_detected and reqID == message[-1]:
                        print(messagetxt.strip())

    def doVal(self, line):
        """
        This can be implemented on top of the client.devValue()
        and devParamValue() interfaces. The problem to be solved is
        how to make the data visible in ipython
        """
        data = line.split()
        par = data[1]
        # check for livedata first
        if par in self.cli.livedata:
            return self.cli.livedata[par]

        # Now check for scan data
        if par == 'scandata':
            xs, ys, _, names = self.cli.eval(
                '__import__("nicos").commands.analyze._getData()[:4]')
            return xs, ys, names

        # Try get device data from NICOS
        if par.find('.') > 0:
            devpar = par.split('.')
            return self.cli.getDeviceParam(devpar[0], devpar[1])
        else:
            return self.cli.getDeviceValue(par)

    def doHelp(self):
        helpdata = """
            %nicos /connect host port user password
            connects to a NICOS instance at host and port

            %nicos /quit
            disconnects from NICOS

            %nicos <some-nicos-command>
            executes the NICOS command against the daemon and returns the
            captured output

            %nicos /status
            returns the current run status of NICOS

            %nicos /live
            lists available live data names. Works only after the first
            counting operation

            var = %nicos /val <dev>
            reads the value of dev into var

            var = %nicos /val <dev.param>
            reads the value of the specified device parameter into var

            var = %nicos /val <detname>_live
            reads the live data from <detname> into var. The result is a
            list of arrays.

            xs, ys, names = %nicos /val scandata
            reads the data from the last scan into xs, ys and names. xs is
            the x-axis data, ys the counts and names is the names of the
            data used in the scan.
        """
        print(helpdata)

    def doLive(self):
        print('Available livedata:')
        keys = self.cli.livedata.keys()
        for k in keys:
            print(k)

    @line_magic
    @needs_local_scope
    def nicos(self, line, local_ns=None):
        line = line.strip()
        if line.startswith('/connect'):
            return self.connect(line)
        if line.startswith('/help'):
            return self.doHelp()
        if not self.cli.isconnected:
            print('Connect with /connect host port user pwd before I do '
                  'anything for you')
            return
        else:
            if line.startswith('/quit'):
                self.cli.disconnect()
            elif line.startswith('/val'):
                return self.doVal(line)
            elif line.startswith('/live'):
                return self.doLive()
            elif line.startswith('/status'):
                return self.cli.status
            else:
                self.processCommand(line)
            return

# In order to actually use these magics, you must register them with a
# running IPython.


def load_ipython_extension(ipython):
    """
    Any module file that define a function named `load_ipython_extension`
    can be loaded via `%load_ext module.path` or be configured to be
    autoloaded by IPython at startup time.
    """
    # You can register the class itself without instantiating it.  IPython will
    # call the default constructor on it.
    ipython.register_magics(Nicos)
