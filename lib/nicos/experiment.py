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

"""NICOS Experiment devices."""

from __future__ import with_statement

__version__ = "$Revision$"

import os
import time
from os import path
from uuid import uuid1

from nicos import session
from nicos.core import listof, nonemptylistof, control_path_relative, \
     usermethod, Device, Measurable, Readable, Param, Dataset
from nicos.data import NeedsDatapath
from nicos.scan import DevStatistics
from nicos.utils import ensureDirectory
from nicos.utils.loggers import ELogHandler
from nicos.utils.proposaldb import queryProposal


class Sample(Device):
    """A special device to represent a sample.

    An instance of this class is used as the *sample* attached device of the
    `Experiment` object.  It can be subclassed to add special sample properties,
    such as lattice and orientation calculations, or more parameters describing
    the sample.
    """

    parameters = {
        'samplename':  Param('Sample name', type=str, settable=True,
                             category='sample'),
    }

    def reset(self):
        """Reset experiment-specific information."""
        self.samplename = ''

    def doWriteSamplename(self, name):
        if name:
            session.elog_event('sample', name)


class Experiment(Device):
    """A special singleton device to represent the experiment.

    This class is normally subclassed for specific instruments to e.g. select
    the data paths according to instrument standards.

    Several parameters configure special behavior:

    * `datapath` (usually set proposal-specific by the `new` method) is a list
      of paths where raw data files are stored.  If there is more than one entry
      in the list, the data files are created in the first path and hardlinked
      in the others.
    * `detlist` and `envlist` are lists of names of the currently selected
      standard detector and sample environment devices, respectively.  The
      Experiment object has `detectors` and `sampleenv` properties that return
      lists of the actual devices.
    * `scripts` is managed by the session and should contain a stack of code of
      user scripts currently executed.

    The experiment singleton is available at runtime as
    `nicos.session.experiment`.
    """

    parameters = {
        'title':     Param('Experiment title', type=str, settable=True,
                           category='experiment'),
        'proposal':  Param('Current proposal number or proposal string',
                           type=str, settable=True, category='experiment'),
        # XXX: this results in unfriendly entries in the data file
        # users : ['user a', 'user b']
        'users':     Param('User names and affiliations for the proposal',
                           type=listof(str), settable=True,
                           category='experiment'),
        'localcontact': Param('Local contact for current experiment',
                              type=str, settable=True, category='experiment'),
        'remark':    Param('Current remark about experiment configuration',
                           type=str, settable=True, category='experiment'),
        'dataroot':  Param('Root data path under which all proposal specific '
                           'paths are created', type=control_path_relative,
                           default='.', mandatory=True),
        'proposaldir':   Param('Directory for proposal specific files',
                           settable=True, type=str),
        'scriptdir': Param('Standard script directory',
                           settable=True, type=str),
        'datapath':  Param('List of paths where data files should be stored',
                           type=nonemptylistof(str), settable=True),
        'detlist':   Param('List of default detector device names',
                           type=listof(str), settable=True),
        'envlist':   Param('List of default environment device names to read '
                           'at every scan point', type=listof(str),
                           settable=True),
        'elog':      Param('True if the electronig logbook should be enabled',
                           type=bool, default=True),
        'propdb':    Param('user@host:dbname credentials for proposal DB',
                           type=str, default='', userparam=False),
        'scripts':   Param('Currently executed scripts',
                           type=listof(str), settable=True),
        'remember':  Param('List of messages to remember for next experiment '
                           'start', type=listof(str), settable=True),
    }

    attached_devices = {
        'sample': (Sample, 'The device object representing the sample'),
    }

    def doInit(self):
        self._last_datasets = []
        instname = session.instrument and session.instrument.instrument or ''
        if self.elog:
            ensureDirectory(path.join(self.proposaldir, 'logbook'))
            session.elog_event('directory', (self.proposaldir,
                                             instname, self.proposal))
            self._eloghandler = ELogHandler()
            # only enable in master mode, see below
            self._eloghandler.disabled = session.mode != 'master'
            session.addLogHandler(self._eloghandler)

    @usermethod
    def new(self, proposal, title=None, localcontact=None, **kwds):
        """Called by `.NewExperiment`."""
        # Individual instruments should override this to change datapath
        # according to instrument policy, and maybe call _fillProposal
        # to get info from the proposal database
        if isinstance(proposal, (int, long)):
            proposal = str(proposal)
        self.proposal = proposal
        self.title = title or ''
        self.localcontact = localcontact or ''
        # reset everything else to defaults
        self.remark = ''
        self.users = []
        self.sample.reset()
        self.envlist = []
        #self.detlist = []
        if self.remember:
            self.log.warning('Please remember:')
            for message in self.remember:
                self.log.info(message)
        self.remember = []
        for notifier in session.notifiers:
            notifier.reset()
        self._last_datasets = []
        session.elog_event('newexperiment', (proposal, title))
        session.elog_event('setup', list(session.explicit_setups))

    def _setMode(self, mode):
        if self.elog:
            self._eloghandler.disabled = mode != 'master'
        Device._setMode(self, mode)

    def _fillProposal(self, proposal):
        """Fill proposal info from proposal database."""
        if not self.propdb:
            return
        try:
            info = queryProposal(self.propdb, proposal)
        except Exception:
            self.log.warning('unable to query proposal info', exc=1)
            return
        what = []
        kwds = {}
        if info.get('title') and self.title == '':
            self.title = info['title']
            what.append('title')
            kwds['title'] = info['title']
        if info.get('substance'):
            self.sample.samplename = info['substance']
            what.append('sample name')
            kwds['sample'] = info['substance']
        if info.get('user'):
            email = info.get('user_email', '')
            self.addUser(info['user'], email, info.get('affiliation'))
            what.append('user')
        if info.get('co_proposer'):
            proplist = []
            for coproposer in info['co_proposer'].splitlines():
                coproposer = coproposer.strip()
                if coproposer:
                    proplist.append(coproposer)
            if proplist:
                self.users = self.users + proplist
                what.append('co-proposers')
        if self.users:
            kwds['users'] = ', '.join(self.users)
        if what:
            self.log.info('Filled in %s from proposal database' %
                           ', '.join(what))
        return kwds

    @usermethod
    def addUser(self, name, email=None, affiliation=None):
        """Called by `.AddUser`."""
        if email:
            user = '%s <%s>' % (name, email)
        else:
            user = name
        if affiliation is not None:
            user += ' (' + affiliation + ')'
        self.users = self.users + [user]
        self.log.info('User "%s" added' % self.users[-1])

    @usermethod
    def finish(self, *args, **kwargs):
        """Called by `.FinishExperiment`.  Does nothing by default."""
        if self.remember:
            self.log.warning('Please remember:')
            for message in self.remember:
                self.log.info(message)

    def doWriteRemark(self, remark):
        if remark:
            session.elog_event('remark', remark)

    def doReadDatapath(self):
        # default for datapath is just all in one directory under dataroot
        return [self.dataroot]

    def doWriteDatapath(self, dirs):
        for datadir in dirs:
            if not path.isdir(datadir):
                os.makedirs(datadir)
        for dev in session.devices.itervalues():
            if isinstance(dev, NeedsDatapath):
                dev.datapath = dirs

    def doReadProposaldir(self):
        # default for proposal dir is just dataroot
        return self.dataroot

    def doWriteProposaldir(self, newdir):
        if not self.elog:
            return
        ensureDirectory(path.join(newdir, 'logbook'))
        instname = session.instrument and session.instrument.instrument or ''
        session.elog_event('directory', (newdir, instname, self.proposal))

    def doReadScriptdir(self):
        # default for script dir is just dataroot
        return self.dataroot

    def createDataset(self, scantype=None):
        dataset = Dataset()
        dataset.uid = str(uuid1())
        dataset.sinks = [sink for sink in session.datasinks
                         if sink.isActive(scantype)]
        dataset.started = time.localtime()
        return dataset

    @property
    def sample(self):
        return self._adevs['sample']

    @property
    def detectors(self):
        if self._detlist is not None:
            return self._detlist[:]
        detlist = []
        all_created = True
        for detname in self.detlist:
            try:
                det = session.getDevice(detname)
            except Exception:
                self.log.warning('could not create %r detector device' %
                                 detname, exc=1)
                all_created = False
            else:
                if not isinstance(det, Measurable):
                    self.log.warning('cannot use device %r as a '
                                     'detector: it is not a Measurable' % det)
                    all_created = False
                else:
                    detlist.append(det)
        if all_created:
            self._detlist = detlist
        return detlist[:]

    def setDetectors(self, detectors):
        dlist = []
        for det in detectors:
            if isinstance(det, Device):
                det = det.name
            if det not in dlist:
                dlist.append(det)
        self.detlist = dlist
        dummy = self.detectors  # try to create them right now
        session.elog_event('detectors', dlist)

    def doUpdateDetlist(self, detectors):
        self._detlist = None  # clear list of actual devices

    @property
    def sampleenv(self):
        if self._envlist is not None:
            return self._envlist[:]
        devlist = []
        all_created = True
        for devname in self.envlist:
            try:
                if ':' in devname:
                    devname, stat = devname.split(':')
                    dev = session.getDevice(devname)
                    dev = DevStatistics.subclasses[stat](dev)
                else:
                    dev = session.getDevice(devname)
            except Exception:
                self.log.warning('could not create %r environment device' %
                                 devname, exc=1)
                all_created = False
            else:
                if not isinstance(dev, (Readable, DevStatistics)):
                    self.log.warning('cannot use device %r as '
                                     'environment: it is not a Readable' % dev)
                    all_created = False
                else:
                    devlist.append(dev)
        if all_created:
            self._envlist = devlist
        return devlist[:]

    def setEnvironment(self, devices):
        dlist = []
        for dev in devices:
            if isinstance(dev, Device):
                dev = dev.name
            elif isinstance(dev, DevStatistics):
                dev = str(dev)
            if dev not in dlist:
                dlist.append(dev)
        self.envlist = dlist
        dummy = self.sampleenv  # try to create them right now
        session.elog_event('environment', dlist)

    def doUpdateEnvlist(self, devices):
        self._envlist = None  # clear list of actual devices
