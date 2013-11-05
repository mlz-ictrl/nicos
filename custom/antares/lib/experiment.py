#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************


"""NICOS Antares Experiment."""

import time
import os
from os import path

from nicos.core import Param, Override, UsageError, usermethod
from nicos.utils import ensureDirectory, enableDirectory
from frm2.experiment import Experiment as FRM2Experiment  # pylint: disable=F0401


class Experiment(FRM2Experiment):

    parameters = dict(
        # Params are settable as we have to set them via _updatePaths
        darkimagepath = Param('Current storage path for dark images', type=str,
                              settable=True, mandatory=False, default='',
                              userparam=False),
        openbeampath  = Param('Current storage path for open beam images',
                              type=str, settable=True, mandatory=False,
                              default='', userparam=False),
        photopath     = Param('Current storage path for photographs', type=str,
                              settable=True, mandatory=False, default='',
                              userparam=False),
        lastdarkimage = Param('Last dark image', type=str, settable=False,
                              mandatory=False, default='', category='general',
                              chatty=True),
        lastopenbeamimage = Param('Last open beam image', type=str,
                              settable=False, mandatory=False, default='',
                              category='general', chatty=True),
    )

    parameter_overrides = {
        'propprefix':    Override(default='p'),
        'templatedir':   Override(default='templates'),
        'servicescript': Override(default='start_service.py'),
        'dataroot':      Override(default='/data/FRM-II'),
    }

    @usermethod
    def newSample(self, name, parameters):
        """Called by `.NewSample`."""
        FRM2Experiment.newSample(self, name, parameters)
        self._updatePaths(self.proposaldir, name)

    def _updatePaths(self, proposaldir, samplename=''):
        """
        Update paths for open beam, dark, and normal images to fit
        the specifications of ANTARES.
        """

        self.log.debug('update path configuration for new sample (%s):'
                       % samplename)

        replaced = False
        for badchar in '/\\*\000': # more needed?
            if samplename.find(badchar) != -1:
                replaced = True
                samplename.replace(badchar, '_')
        if replaced:
            self.log.warning('Sample name contained illegal characters, '
                             'which were replaced.')
            self.log.info('New sample name is %r' % samplename)

        sampledir = path.join(proposaldir, samplename)
        ensureDirectory(sampledir)
        if self.managerights:
            enableDirectory(sampledir, **self.managerights)

        self.log.debug('new sample dir: %s' % sampledir)

        self.datapath = [path.join(sampledir, 'data')]
        ensureDirectory(self.datapath[0])
        if self.managerights:
            enableDirectory(self.datapath[0], **self.managerights)

        self.log.debug('new data path: %s' % self.datapath[0])

        if samplename:
            ensureDirectory(path.join(sampledir, 'eval', 'recon'))

            if self.managerights:
                enableDirectory(path.join(sampledir, 'eval', 'recon'), **self.managerights)

        # manage a current symlink inside the proposaldir pointing to the
        # currently selected sample
        symname = path.join(proposaldir, 'current')
        if hasattr(os, 'symlink'):
            self.log.debug('setting symlink %s to %s' %
                           (symname, sampledir))
            if os.path.islink(symname):
                self.log.debug('remove old symlink (%s)'
                               % os.path.realpath(symname))
                os.remove(symname)

            self.log.debug('set new symlink to (%s)' % sampledir)
            os.symlink(sampledir, symname)

        self.darkimagepath = path.join(self.datapath[0], 'di')
        ensureDirectory(self.darkimagepath)
        if self.managerights:
            enableDirectory(self.darkimagepath, **self.managerights)
        self.log.debug('new dark image path: %s' % self.darkimagepath)

        self.openbeampath = path.join(self.datapath[0], 'ob')
        ensureDirectory(self.openbeampath)
        if self.managerights:
            enableDirectory(self.openbeampath, **self.managerights)
        self.log.debug('new open beam image path: %s' % self.openbeampath)

        self.photopath = path.join(sampledir, 'photos')
        ensureDirectory(self.photopath)
        if self.managerights:
            enableDirectory(self.photopath, **self.managerights)
        self.log.debug('new measurement image path: %s' % self.openbeampath)

    def _getProposalDir(self, proposal):
        """Return current proposaldir and create a fancy symlink."""
        propdir = path.join(self.dataroot, time.strftime('%Y'), proposal)
        self._updatePaths(propdir)
        # figue out fancy symname
        u = self.users

        for c in ',(<':
            u = u.split(c, 1)[0]

        if not u:
            u = 'default'
        symname = path.join('%s_%s_%s'%(time.strftime('%F'), u, proposal))
        try:
            os.symlink(propdir, path.join(propdir, '..', symname))
        except OSError:
            self.log.debug('creation of symlink failed, already existing???')
        return propdir

    def _newPropertiesHook(self, proposal, kwds):
        kwds['sample'] = ''       # ALWAYS start without samplename
        if 'user' not in kwds:
            kwds['user'] = 'Somebody'
            self.log.error('No Users specified in Proposal and no keyword '
                           'argument given. '
                           'continuing with default user....')
        if self.proptype == 'user':
            self._fillProposal(int(proposal[len(self.propprefix):]), kwds)
        return kwds

    def _getProposalSymlink(self):
        return path.join(self.dataroot, 'current')

    def _getDatapath(self, proposal):
        return self.datapath # updated by _update_paths()

    def _getProposalType(self, proposal):
        if proposal in ('template', 'current'):
            raise UsageError(self, 'The proposal names "template" and "current"'
                             ' are reserved and cannot be used')
        return FRM2Experiment._getProposalType(self, proposal)
