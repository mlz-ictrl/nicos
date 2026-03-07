# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2026-present by the NICOS contributors (see AUTHORS)
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
#   Artur Glavic <artur.glavic@psi.ch>
#
# *****************************************************************************

import os.path
from time import time
from subprocess import Popen, PIPE, TimeoutExpired
from threading import Thread

from nicos.core import DataSinkHandler, Param
from nicos.devices.datasinks import FileSink


class ScriptRunnerThread(Thread):
    def __init__(self, script, file_name, log, timeout=5.0):
        super().__init__(name='Script Runner')
        self.log=log
        self.script=script
        self.file_name=file_name
        self.timeout=timeout

    def run(self):
        if not os.path.exists(self.script):
            self.log.warning(f'Script {self.script} does not exist')
            return
        start_time = time()

        try:
            with Popen(self.script.split() + [self.file_name], stdout=PIPE, stderr=PIPE, text=True) as self.proc:
                try:
                    outs, errs = self.proc.communicate(timeout=self.timeout)
                except TimeoutExpired:
                    self.proc.kill()
                    outs, errs = self.proc.communicate()
                    self.log.warning('Script did not finish before timeout finished')
                    self.log.debug('    script stdout:\n        '+
                                    outs.strip().replace('\n', '\n        '))
                    self.log.debug('    script stderr:\n        '+
                                errs.strip().replace('\n', '\n        '))
                else:
                    if self.proc.returncode > 0:
                        self.log.warning(f'Script returned exit code {self.proc.returncode}')
                        self.log.debug('    script stdout:\n'+
                                        outs.strip().replace('\n', '\n        '))
                        self.log.debug('    script stderr:\n'+
                                    errs.strip().replace('\n', '\n        '))
                    else:
                        self.log.debug(f'Script finished normally after {time()-start_time:.2f}s\n'+
                                    outs.strip().replace('\n', '\n    '))

        except Exception:
            self.log.error(f'Failed to run script {self.script}', exc_info=True)


class AutoreduceHandler(DataSinkHandler):
    ordering: int = 99

    def end(self):
        """
        In addition to standard SinqExperiment behavior, run the autoreduction as background process.
        """
        if self.dataset.counter == 0 or len(self.dataset.filepaths) < 1:
            return
        if self.sink._runner_thread:
            self.sink._runner_thread.join()
            self.sink._runner_thread=None
        if self.sink.script != '':
            self.sink._runner_thread = ScriptRunnerThread(self.sink.script,self.dataset.filepaths[0], self.log)
            self.sink._runner_thread.start()

class AutoreduceSink(FileSink):
    """
    Adds a feature to run auto-reduction script after each run.
    The script is an executable path that can be user-configure.
    """
    parameters = {
        'script': Param('Dictionary of tomography parameters',
                             type=str,
                             mandatory=False,
                             default='',
                             settable=True,
                             userparam=True),
        }

    handlerclass = AutoreduceHandler
    _runner_thread = None
