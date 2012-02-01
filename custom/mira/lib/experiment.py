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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""NICOS MIRA Experiment."""

__version__ = "$Revision$"

import os
import time
import zipfile
from os import path

from nicos.utils import ensureDirectory
from nicos.experiment import Experiment


class MiraExperiment(Experiment):

    def new(self, proposal, title=None, **kwds):
        if not isinstance(proposal, (int, long)):
            proposal = int(proposal)
        new_datapath = '/data/%s/%s' % (time.strftime('%Y'), proposal)
        self.datapath = [new_datapath]
        if proposal == 0 and title is None:
            title = 'Maintenance'
        Experiment.new(self, proposal, title)
        if proposal != 0:
            self._fillProposal(proposal)

        ensureDirectory(path.join(new_datapath, 'scripts'))
        self.scriptdir = path.join(new_datapath, 'scripts')

        if proposal != 0:
            self.log.info('New experiment %s started' % proposal)
        else:
            self.log.info('Maintenance time started')
        self.log.info('Data directory set to %s' % new_datapath)

    def finish(self, **kwds):
        if kwds.get('zip', True):
            try:
                self.log.info('zipping experiment data, please wait...')
                zipname = self.datapath[0].rstrip('/') + '.zip'
                zf = zipfile.ZipFile(zipname, 'w', zipfile.ZIP_DEFLATED, True)
                nfiles = 0
                try:
                    for root, dirs, files in os.walk(self.datapath[0]):
                        xroot = root[len(self.datapath[0]):].strip('/') + '/'
                        for fn in files:
                            zf.write(path.join(root, fn), xroot + fn)
                            nfiles += 1
                            if nfiles % 500 == 0:
                                self.log.info('%5d files processed' % nfiles)
                finally:
                    zf.close()
            except Exception:
                self.log.warning('could not zip up experiment data', exc=1)
            else:
                self.log.info('done: ' + zipname)
        self.new(0)
