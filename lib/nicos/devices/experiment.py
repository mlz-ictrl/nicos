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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""NICOS Experiment devices."""

import os
import re
import time
import shutil
import zipfile
from os import path
from uuid import uuid1

from nicos import session
from nicos.core import listof, nonemptylistof, oneof, control_path_relative, \
     none_or, mailaddress, usermethod, Device, Measurable, Readable, Param, \
     Dataset, NicosError
from nicos.core.scan import DevStatistics
from nicos.utils import ensureDirectory, expandTemplate, disableDirectory, \
     enableDirectory
from nicos.utils.loggers import ELogHandler
from nicos.commands.basic import run
from nicos.devices.datasinks import NeedsDatapath


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
        'title':        Param('Experiment title', type=str, settable=True,
                              category='experiment'),
        'proposal':     Param('Current proposal number or proposal string',
                              type=str, settable=True, category='experiment'),
        'proptype':     Param('Current proposal type', settable=True,
                              type=oneof('service', 'user', 'other')),
        'propprefix':   Param('Prefix of the proposal if is a number', type=str,
                              settable=True, default=''),
        'users':        Param('User names and emails for the proposal',
                              type=str, settable=True, category='experiment'),
        'localcontact': Param('Local contact for current experiment',
                              type=str, settable=True, category='experiment'),
        'remark':       Param('Current remark about experiment configuration',
                              type=str, settable=True, category='experiment'),
        'dataroot':     Param('Root data path under which all proposal specific'
                              ' paths are created', type=control_path_relative,
                              default='.', mandatory=True),
        'proposaldir':  Param('Directory for proposal specific files',
                              settable=True, type=str),
        'scriptdir':    Param('Standard script directory',
                              settable=True, type=str),
        'datapath':     Param('List of paths where data files should be stored',
                              type=nonemptylistof(str), settable=True),
        'detlist':      Param('List of default detector device names',
                              type=listof(str), settable=True),
        'envlist':      Param('List of default environment device names to read'
                              ' at every scan point', type=listof(str),
                              settable=True),
        'elog':         Param('True if the electronig logbook should be '
                              'enabled', type=bool, default=True),
        'scripts':      Param('Currently executed scripts',
                              type=listof(str), settable=True),
        'remember':     Param('List of messages to remember for next experiment'
                              ' start', type=listof(str), settable=True),
        'templatedir':  Param('Name of the directory with script templates '
                              '(relative to dataroot)', type=str, default=''),
        'managerights': Param('Whether to manage access rights on proposal '
                              'directories on proposal change', type=bool,
                              settable=True),
        'zipdata':      Param('Whether to zip up experiment data after '
                              'experiment finishes', type=bool, default=True),
        'sendmail':     Param('Whether to send proposal data via email after '
                              'experiment finishes', type=bool, default=False),
        'mailserver':   Param('Mail server name', type=str, settable=True),
        'mailsender':   Param('Mail sender address', type=none_or(mailaddress),
                              settable=True),
        'mailtemplate': Param('Mail template file name (in templatedir)',
                              type=str, default='mailtext.txt'),
        'serviceexp':   Param('Name of proposal to switch to after user '
                              'experiment', type=str),
        'servicescript': Param('Script to run for service time', type=str,
                               default='', settable=True),
        'pausecount':   Param('Reason for pausing the count loop', type=str,
                              settable=True),
    }

    attached_devices = {
        'sample': (Sample, 'The device object representing the sample'),
    }

    def doInit(self, mode):
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
    def new(self, proposal, title=None, localcontact=None, user=None, **kwds):
        """Called by `.NewExperiment`."""
        # determine real proposal number some instruments assign a prefix to
        # numeric proposals
        if isinstance(proposal, (int, long)):
            proposal = '%s%d' % (self.propprefix, proposal)
        self.log.debug('new proposal real name is %s' % proposal)

        # check proposal type (can raise)
        proptype = self._getProposalType(proposal)
        self.log.debug('new proposal type is %s' % proptype)

        # check if we should finish the experiment first
        if self.serviceexp and proptype == self.proptype == 'user':
            self.log.error('cannot switch directly to new user experiment, '
                           'please use FinishExperiment first')
            return

        symlink = self._getProposalSymlink()

        # remove access rights to old proposal if wanted
        if self.managerights and self.proptype == 'user':
            try:
                disableDirectory(self.proposaldir)
            except Exception:
                self.log.warning('could not remove permissions for old '
                                 'experiment directory', exc=1)
            else:
                self.log.debug('disabled directory %s' % self.proposaldir)
        # remove old symlink to current experiment
        if symlink and path.islink(symlink):
            os.unlink(symlink)

        # reset all experiment dependent parameters and values to defaults
        self.remark = ''
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

        # set new experiment properties given by caller
        self.proposal = proposal
        self.proptype = proptype
        # allow instruments to override (e.g. from proposal DB)
        if title:
            kwds['title'] = title
        if user:
            kwds['user'] = user
        if localcontact:
            kwds['localcontact'] = localcontact
        kwds = self._newPropertiesHook(proposal, kwds)
        self.title = kwds.get('title', '')
        self.users = kwds.get('user', '')
        self.localcontact = kwds.get('localcontact', '')
        self.sample.samplename = kwds.get('sample', '')

        # create new data path and expand templates
        new_proposaldir = self._getProposalDir(proposal)
        ensureDirectory(new_proposaldir)
        if self.managerights:
            enableDirectory(new_proposaldir)
            self.log.debug('enabled directory %s' % new_proposaldir)
        if symlink and hasattr(os, 'symlink'):
            self.log.debug('setting symlink %s to %s' %
                           (symlink, path.abspath(new_proposaldir)))
            os.symlink(path.abspath(new_proposaldir), symlink)
        self.proposaldir = new_proposaldir
        self.log.info('experiment directory set to %s' % new_proposaldir)

        new_scriptdir = path.join(self.proposaldir, 'scripts')
        ensureDirectory(new_scriptdir)
        self.scriptdir = new_scriptdir
        self.log.info('script directory set to %s' % new_scriptdir)

        new_datapath = self._getDatapath(proposal)
        for entry in new_datapath:
            ensureDirectory(entry)
        self.datapath = new_datapath
        self.log.info('data directory set to %s' % new_datapath[0])

        # notify logbook
        session.elog_event('newexperiment', (proposal, title))
        session.elog_event('setup', list(session.explicit_setups))

        # expand templates
        if proptype != 'service':
            if self.templatedir:
                kwds['proposal'] = self.proposal
                self._handleTemplates(proposal, kwds)
            self.log.info('New experiment %s started' % proposal)
        else:
            if self.servicescript:
                run(self.servicescript)
            else:
                self.log.debug('not running service script, none configured')
            self.log.info('Maintenance time started')

        self._afterNewHook()

    def _getProposalType(self, proposal):
        if self.serviceexp and proposal == self.serviceexp:
            return 'service'
        if self.propprefix:
            if proposal.startswith(self.propprefix):
                return 'user'
            return 'service'
        try:
            if int(proposal) == 0:
                return 'service'
            return 'user'
        except ValueError:
            return 'service'

    def _getProposalDir(self, proposal):
        return path.join(self.dataroot, time.strftime('%Y'), proposal)

    def _getProposalSymlink(self):
        return path.join(self.dataroot, 'current')

    def _getDatapath(self, proposal):
        return [path.join(self.dataroot, time.strftime('%Y'), proposal, 'data')]

    def _newPropertiesHook(self, proposal, kwds):
        return kwds

    def _afterNewHook(self):
        pass

    def _handleTemplates(self, proposal, kwargs):
        tmpldir = path.join(self.dataroot, self.templatedir)
        filelist = os.listdir(tmpldir)
        try:
            # and sort it (start_....py should be first!)
            filelist.remove('start_{{proposal}}.py.template')
            filelist.insert(0, 'start_{{proposal}}.py.template')
        except Exception:
            pass # file not in templates, no need to sort towards the end
        # second: loop through all the files
        for fn in filelist:
            # translate '.template' files
            if self.mailtemplate and fn.endswith(self.mailtemplate):
                continue # neither copy nor translate the mailtemplate
            if not fn.endswith('.template'):
                if self.mailtemplate and fn.endswith(self.mailtemplate):
                    continue # neither copy nor translate mailtemplate...
                if path.isfile(path.join(self.scriptdir, fn)):
                    self.log.info('file %s already exists, not overwriting' %
                                  fn)
                    continue
                shutil.copyfile(path.join(tmpldir, fn),
                                path.join(self.scriptdir, fn))
                self.log.debug('ignoring file %s' % fn)
                continue
            try:
                newfn = fn[:-9] # strip ".template" from the name
                # now also translate templates in the filename
                newfn, _, _ = expandTemplate(newfn, kwargs)
                self.log.debug('%s -> %s' % (fn, newfn))
                # now read and translate template if file does not already exist
                if path.isfile(path.join(self.scriptdir, newfn)):
                    self.log.info('file %s already exists, not overwriting' %
                                  newfn)
                    continue
                with open(path.join(tmpldir, fn)) as fp:
                    content = fp.read()
                newcontent, defaulted, missing = expandTemplate(content, kwargs)
                if missing:
                    self.log.info('missing keyword argument(s):\n')
                    self.log.info('%12s (%s) %-s\n' %
                                  ('keyword', 'default', 'description'))
                    for entry in missing:
                        self.log.info('%12s (%s)\t%-s\n' %
                            (entry['key'], entry['default'], entry['description']))
                    raise NicosError('some keywords are missing')
                if defaulted:
                    self.log.info('the following keyword argument(s) were taken'
                                  ' from defaults:')
                    self.log.info('%12s (%s) %-s' %
                                  ('keyword', 'default', 'description'))
                    for entry in defaulted:
                        self.log.info('%12s (%s)\t%-s' %
                            (entry['key'], entry['default'], entry['description']))
                # ok, both filename and filecontent are ok and translated ->
                # save (if not already existing)
                with open(path.join(self.scriptdir, newfn), 'w') as fp:
                    fp.write(newcontent)
            except Exception:
                self.log.warning('could not translate template file %s' % fn,
                                 exc=1)

    def _setMode(self, mode):
        if self.elog:
            self._eloghandler.disabled = mode != 'master'
        Device._setMode(self, mode)

    @usermethod
    def addUser(self, name, email=None, affiliation=None):
        """Called by `.AddUser`."""
        if email:
            user = '%s <%s>' % (name, email)
        else:
            user = name
        if affiliation is not None:
            user += ' (' + affiliation + ')'
        if not self.users:
            self.users = user
        else:
            self.users = self.users + ', ' + user
        self.log.info('User "%s" added' % user)

    @usermethod
    def newSample(self, name, parameters):
        """Called by `.NewSample`."""
        self.sample.samplename = name
        for param, value in parameters.iteritems():
            setattr(self.sample, param, value)

    def _zip(self):
        """Zip all files in the current experiment folder into a .zip file."""
        self.log.info('zipping experiment data, please wait...')
        try:
            zipname = self.proposaldir.rstrip('/') + '.zip'
            zf = zipfile.ZipFile(zipname, 'w', zipfile.ZIP_DEFLATED, True)
            nfiles = 0
            try:
                for root, _dirs, files in os.walk(self.proposaldir):
                    xroot = root[len(self.proposaldir):].strip('/') + '/'
                    for fn in files:
                        zf.write(path.join(root, fn), xroot + fn)
                        nfiles += 1
                        if nfiles % 500 == 0:
                            self.log.info('%5d files processed' % nfiles)
            finally:
                zf.close()
        except Exception:
            self.log.warning('could not zip up experiment data', exc=1)
            return None
        else:
            self.log.info('done: stored as ' + zipname)
            return zipname

    def _mail(self, receivers, zipname):
        import smtplib
        from email.mime.application import MIMEApplication
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        # check parameters
        if not self.mailserver:
            raise NicosError('%s.mailserver parameter is not set' % self)
        if not self.mailsender:
            raise NicosError('%s.mailsender parameter is not set' % self)
        if receivers.lower() not in ['none', 'stats'] and '@' not in receivers:
            raise NicosError('need full email address (\'@\' missing!)')

        # get start of proposal from cache history
        hist, d = [], 7
        while not hist and d < 60:
            hist = self.history('proposal', -d*24)
            d += 7
        if hist:
            from_time = hist[-1][0]
        to_time = time.time()
        from_date = time.strftime('%a, %d. %b %Y', time.localtime(from_time))
        to_date = time.strftime('%a, %d. %b %Y', time.localtime(to_time))

        # check number of (scan) data files
        numscans = 0
        firstscan = 99999999
        lastscan = 0
        scanfilepattern = re.compile(r'%s_(\d{8})\.dat$' % self.proposal)
        for fn in os.listdir(self.datapath[0]):
            m = scanfilepattern.match(fn)
            if m:
                firstscan = min(firstscan, int(m.group(1)))
                lastscan = max(lastscan, int(m.group(1)))
                numscans += 1

        # read and translate mailbody template
        try:
            with open(path.join(self.dataroot, self.templatedir,
                                self.mailtemplate)) as fp:
                textfiletext = fp.read()
        except IOError:
            self.log.warning('reading mail template %s failed' %
                             self.mailtemplate, exc=1)
            textfiletext = 'See data in attachment.'
        textfiletext, _, _ = expandTemplate(textfiletext, {
            'proposal':  self.proposal,
            'from_date': from_date,
            'to_date':   to_date,
            'firstscan': '%08d' % firstscan,
            'lastscan':  '%08d' % lastscan,
            'numscans':  str(numscans),
            'title':     self.title,
            'localcontact': self.localcontact,
        })

        if receivers.lower() == 'stats':
            for line in textfiletext.splitlines():
                self.log.info(line)
            return

        # now we would send the file, so prepare everything; construct msg
        # according to
        # http://docs.python.org/library/email-examples.html#email-examples
        receiverlist = receivers.replace(',', ' ').split()
        receivers = ', '.join(receiverlist)
        msg = MIMEMultipart()
        instname = session.instrument and session.instrument.instrument or '?'
        msg['Subject'] = 'Your recent experiment %s on %s from %s to %s' % \
            (self.proposal, instname, from_date, to_date)
        msg['From'] = self.mailsender
        msg['To'] = receivers
        msg.attach(MIMEText(textfiletext))

        # now attach the zipfile
        with open(zipname, 'rb') as fp:
            filedata = fp.read()

        attachment = MIMEApplication(filedata, 'x-zip')
        attachment['Content-Disposition'] = 'ATTACHMENT; filename="%s"' % \
            path.basename(zipname)
        msg.attach(attachment)

        # now comes the final part: send the mail
        mailer = smtplib.SMTP(self.mailserver)
        if self.loglevel == 'debug':
            mailer.set_debuglevel(1)
        self.log.info('Sending data files via eMail to %s' % receivers)
        mailer.sendmail(self.mailsender, receiverlist + [self.mailsender],
                        msg.as_string())
        mailer.quit()

        # "hide" compressed file by moving it into the proposal directory
        self.log.info('moving compressed file to ' + self.proposaldir)
        try:
            os.rename(zipname,
                      path.join(self.proposaldir, path.basename(zipname)))
        except Exception:
            self.log.warning('moving compressed file into proposal dir failed',
                             exc=1)
            # at least withdraw the access rights
            os.chmod(zipname, 0)

    @usermethod
    def finish(self, *args, **kwds):
        """Called by `.FinishExperiment`."""
        # zip up the experiment data if wanted
        if self.proptype == 'user':
            zipname = None
            if self.zipdata or self.sendmail:
                zipname = self._zip()
            if self.sendmail and zipname:
                receivers = None
                if args:
                    receivers = args[0]
                receivers = kwds.get('receivers', kwds.get('email', receivers))
                try:
                    if receivers:
                        self._mail(receivers, zipname)
                except Exception:
                    self.log.warning('could not send the data via email',
                                     exc=1)

        self._afterFinishHook()

        # switch to service experiment (will hide old data if configured)
        if self.serviceexp:
            self.new(self.serviceexp)
        else:
            self.log.debug('no service experiment configured, cannot switch')

        # have to remember things?
        if self.remember:
            self.log.warning('Please remember:')
            for message in self.remember:
                self.log.info(message)
            self.remember = []

    def _afterFinishHook(self):
        pass

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
                det = session.getDevice(detname, source=self)
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
                    dev = session.getDevice(devname, source=self)
                    dev = DevStatistics.subclasses[stat](dev)
                else:
                    dev = session.getDevice(devname, source=self)
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
