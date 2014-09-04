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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************


"""NICOS Antares Experiment."""

import time
import os
from os import path

from nicos.core import Param, Override, usermethod
from nicos.frm2.experiment import Experiment as FRM2Experiment


class Experiment(FRM2Experiment):
    """
    The Antares specific experiment devices makes the last open beam and dark
    images accessible via parameters.

    For internal usage: It also provides darkimagedir, openbeamdir, photodir,
    extradirs and samplesymlink as properties.
    """

    parameters = dict(
        # for display purposes....
        lastdarkimage = Param('Last dark image', type=str, settable=False,
                               mandatory=False, default='', category='general'),
        lastopenbeamimage = Param('Last Open Beam image', type=str, settable=False,
                               mandatory=False, default='', category='general'),
    )

    parameter_overrides = {
        'propprefix':    Override(default='p'),
        'templates':   Override(default='templates'),
        'servicescript': Override(default='start_service.py'),
        'dataroot':      Override(default='/data/FRM-II'),
    }

    @property
    def scriptpath(self):
        """path to the scripts of the current experiment"""
        return path.join(self.proposalpath, 'scripts')

    @property
    def darkimagedir(self):
        return path.join(self.datapath, 'di')

    @property
    def openbeamdir(self):
        return path.join(self.datapath, 'ob')

    @property
    def photodir(self):
        return path.join(self.samplepath, 'photos')

    @property
    def extradirs(self):
        extradirs = [self.darkimagedir, self.openbeamdir, self.photodir]
        if self.sampledir:
            extradirs.append(path.join(self.samplepath, 'eval', 'recon'))
        return extradirs

    @property
    def samplesymlink(self):
        return path.join(self.proposalpath, 'current')

    @usermethod
    def new(self, proposal, title=None, localcontact=None, user=None, **kwds):
        FRM2Experiment.new(self, proposal, title=title, localcontact=localcontact,
                           user=user, **kwds)

        u = self.users
        for c in ',(<@':
            u = u.split(c, 1)[0]
        if not u:
            u = 'default'
        u = u.replace(' ', '_')

        symname = path.join(self.proposalpath, '..', '%s_%s_%s_%s' %
                            (time.strftime('%F').replace('-', '_'), proposal, u, title))
        try:
            self.log.debug('create symlink %r -> %r' %
                           (symname, self.proposalpath))
            os.symlink(os.path.basename(self.proposalpath), symname)
            self.log.info('Symlink %r -> %r created' %
                           (symname, self.proposalpath))
        except OSError:
            self.log.warning('creation of symlink failed, already existing???')

        # clear state info
        self._setROParam('lastdarkimage','')
        self._setROParam('lastopenbeamimage','')


    @usermethod
    def newSample(self, name, parameters):
        """Called by `.NewSample`. and `.NewExperiment`."""

        sampledir = name
        replaced = False
        for badchar in '/\\*\000\t': # more needed?
            if sampledir.find(badchar) != -1:
                replaced = True
                sampledir.replace(badchar, '_')
        sampledir.replace(' ', '_') # also avoid spaces in filenames
        if replaced:
            self.log.warning('Samplename contained illegal characters, '
                             'which got replaced.')
            self.log.info('New Samplename is %r' % sampledir)

        # setting self.sampledir also maintains the symlink if needed
        self.sampledir = sampledir
        FRM2Experiment.newSample(self, name, parameters)

        self.log.debug('new sample path: %s' % self.samplepath)
        self.log.debug('new data path: %s' % self.datapath)
        self.log.debug('new dark image path: %s' % self.darkimagedir)
        self.log.debug('new open beam image path: %s' % self.openbeamdir)
        self.log.debug('new measurement image path: %s' % self.photodir)

    def _newPropertiesHook(self, proposal, kwds):
        kwds = FRM2Experiment._newPropertiesHook(self, proposal, kwds)
        kwds['sample'] = ''       # ALWAYS start without samplename
        if 'user' not in kwds:
            kwds['user'] = 'Somebody'
            self.log.error('No Users specified in Proposal and no keyword '
                           'argument given. '
                           'continuing with default user....')
        return kwds
