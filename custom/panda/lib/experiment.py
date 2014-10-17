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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""NICOS PANDA Experiment."""

import os
import time
import subprocess
from os import path

from nicos.core import Override, Param
from nicos.utils import createThread
from nicos.frm2.experiment import Experiment


class PandaExperiment(Experiment):
    parameters = {
        'editor' : Param('User editor for new scripts', type=str,
                         settable=True, default='Scite'),
    }

    parameter_overrides = {
        'propprefix':    Override(default='p'),
        'templates':   Override(default='exp/template'),
        'servicescript': Override(default='start_service.py'),
    }

    @property
    def proposaldir(self):
        """deviating from default of <dataroot>/<year>/<proposal>"""
        return path.join(self.dataroot, 'exp', self.proposal)

    @property
    def proposalsymlink(self):
        """deviating from default of <dataroot>/current"""
        return path.join(self.dataroot, 'exp', 'current')

    def _afterNewHook(self):
        if self.editor:
            self._start_editor()

    def _start_editor(self):
        """Open all existing script files in an editor."""
        filelist = [fn for fn in os.listdir(self.scriptpath)
                    if fn.endswith('.py')]
        # sort filelist to have the start_*.py as the last file
        for fn in filelist:
            if fn.startswith('start_'):
                filelist.remove(fn)
                filelist.append(fn)
                break
        def preexec():
            os.setpgrp()  # create new process group -> doesn't get Ctrl-C
            os.chdir(self.scriptpath)
        # start it and forget it
        s = subprocess.Popen([self.editor] + filelist,
            close_fds=True,
            stdin=subprocess.PIPE,
            stdout=os.tmpfile(),
            stderr=subprocess.STDOUT,
            preexec_fn=preexec,
        )
        def checker():
            while s.returncode is None:
                time.sleep(1)
                s.poll()
        # something needs to check the return value, if the process ends
        createThread('Checking Editor', checker)
