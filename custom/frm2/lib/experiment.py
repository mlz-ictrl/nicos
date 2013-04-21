#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""NICOS FRM II Experiment."""

from __future__ import with_statement

import os
import time
import threading
import subprocess

from nicos.core import Param, Override
from nicos.frm2.proposaldb import queryCycle, queryProposal
from nicos.devices.experiment import Experiment as BaseExperiment


class Experiment(BaseExperiment):

    parameters = {
        'cycle':   Param('Current reactor cycle', type=str, settable=True),
        'editor':  Param('User editor for new scripts', type=str,
                         settable=True),
        'propdb':  Param('Filename with credentials string for proposal DB',
                         type=str, default='', userparam=False),
    }

    parameter_overrides = {
        'mailserver':  Override(default='mailhost.frm2.tum.de'),
    }

    def _newPropertiesHook(self, proposal, kwds):
        if 'cycle' not in kwds:
            if self.propdb:
                try:
                    cycle, started = queryCycle()
                    kwds['cycle'] = cycle
                except Exception:
                    self.log.error('cannot query reactor cycle', exc=1)
            else:
                self.log.error('cannot query reactor cycle, please give a '
                               '"cycle" keyword to this function')
        self.cycle = kwds['cycle']
        if self.proptype == 'user':
            self._fillProposal(int(proposal[len(self.propprefix):]), kwds)
        return kwds

    def _afterNewHook(self):
        if self.editor:
            self._start_editor()

    def _fillProposal(self, proposal, kwds):
        """Fill proposal info from proposal database."""
        if not self.propdb:
            return
        try:
            info = queryProposal(proposal)
        except Exception:
            self.log.warning('unable to query proposal info', exc=1)
            return
        what = []
        if info.get('title') and not kwds.get('title'):
            what.append('title')
            kwds['title'] = info['title']
        if info.get('substance'):
            what.append('sample name')
            kwds['sample'] = info['substance']
        if info.get('user'):
            newuser = info['user']
            email = info.get('user_email', '')
            if email:
                newuser += ' <%s>' % email
            if info.get('affiliation'):
                newuser += ' (%s)' % info['affiliation']
            kwds['user'] = newuser
            what.append('user')
        if info.get('co_proposer'):
            proplist = []
            for coproposer in info['co_proposer'].splitlines():
                coproposer = coproposer.strip()
                if coproposer:
                    proplist.append(coproposer)
            if proplist:
                kwds['user'] += ', ' + ', '.join(proplist)
                what.append('co-proposers')
        if what:
            self.log.info('Filled in %s from proposal database' %
                           ', '.join(what))

    def _start_editor(self):
        """Open all existing script files in an editor."""
        filelist = [fn for fn in os.listdir(self.scriptdir)
                    if fn.endswith('.py')]
        # sort filelist to have the start_*.py as the last file
        for fn in filelist:
            if fn.startswith('start_'):
                filelist.remove(fn)
                filelist.append(fn)
                break
        def preexec():
            os.setpgrp()  # create new process group -> doesn't get Ctrl-C
            os.chdir(self.scriptdir)
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
        thread = threading.Thread(target=checker, name='Checking Editor')
        # don't block on closing python if the editor is still running...
        thread.setDaemon(True)
        thread.start()
