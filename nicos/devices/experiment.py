# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#   Christian Felder <c.felder@fz-juelich.de>
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

"""NICOS Experiment devices."""

import os
import re
import time
from os import path
from textwrap import dedent

from nicos import config, session
# import for side-effects
from nicos._vendor import rtfunicode  # pylint: disable=unused-import
from nicos.core import MASTER, SIMULATION, Attach, ConfigurationError, \
    Device, Measurable, NicosError, Param, Readable, UsageError, anytype, \
    dictof, listof, mailaddress, none_or, oneof, usermethod
from nicos.core.acquire import DevStatistics
from nicos.core.data import DataManager
from nicos.core.params import expanded_path, nonemptystring, subdir
from nicos.devices.sample import Sample
from nicos.utils import DEFAULT_FILE_MODE, createThread, disableDirectory, \
    enableDirectory, ensureDirectory, expandTemplate, grp, lazy_property, \
    printTable, pwd, safeName
from nicos.utils.compression import zipFiles
from nicos.utils.emails import sendMail
from nicos.utils.ftp import ftpUpload
from nicos.utils.loggers import ELogHandler


class Experiment(Device):
    """A special singleton device to represent the experiment.

    This class is normally subclassed for specific instruments to e.g. select
    the data paths according to instrument standards.

    Several parameters configure special behavior:

    * `detlist` and `envlist` are lists of names of the currently selected
      standard detector and sample environment devices, respectively.  The
      Experiment object has `detectors` and `sampleenv` properties that return
      lists of the actual devices.
    * `scripts` is managed by the session and should contain a stack of code of
      user scripts currently executed.

    The experiment singleton is available at runtime as
    `nicos.session.experiment`.

    If mailuser is specified, password should be stored in the nicos keyring
    (domain: nicos) using the *mailserver_password* as identifier.
    """

    parameters = {
        'proposal':       Param('Current proposal number or proposal string',
                                type=str, category='experiment'),
        'proptype':       Param('Current proposal type', internal=True,
                                type=oneof('service', 'user', 'other')),
        'propprefix':     Param('Prefix of the proposal if is a number',
                                type=str, settable=True, default='p'),
        # The next three are formed from propinfo on read access.
        'title':          Param('Experiment title', type=str, volatile=True,
                                category='experiment'),
        'users':          Param('User names and emails for the proposal',
                                type=str, volatile=True, category='experiment'),
        'localcontact':   Param('Local contacts for current experiment',
                                type=str, volatile=True, category='experiment'),
        'remark':         Param('Current remark about experiment configuration',
                                type=str, settable=True, category='experiment'),
        'dataroot':       Param('Root data path under which all proposal '
                                'specific paths are created', mandatory=True,
                                type=expanded_path),
        'forcescandata':  Param('If true, force scan datasets to be created '
                                'also for single counts', type=bool,
                                default=False),
        'detlist':        Param('List of default detector device names',
                                type=listof(str), settable=True,
                                internal=True),
        'envlist':        Param('List of default environment device names to '
                                'read at every scan point', type=listof(str),
                                settable=True, internal=True),
        'elog':           Param('True if the electronic logbook should be '
                                'enabled', type=bool, default=True),
        'elog_hidden':    Param('True if the events sent to the electronic '
                                'logbook should be hidden by default',
                                type=bool, default=False, settable=True),
        'scripts':        Param('Currently executed scripts', type=listof(str),
                                settable=True, internal=True,
                                no_sim_restore=True),
        'templates':      Param('Name of the directory with script templates '
                                '(relative to dataroot)', type=str),
        'managerights':   Param('A dict of en/disableDir/FileMode to manage '
                                'access rights of data dirs on proposal change',
                                mandatory=False, settable=False, default={},
                                type=dictof(oneof('owner', 'group',
                                                  'enableOwner',
                                                  'enableGroup',
                                                  'disableOwner',
                                                  'disableGroup',
                                                  'enableDirMode',
                                                  'enableFileMode',
                                                  'disableDirMode',
                                                  'disableFileMode'),
                                            anytype),
                                userparam=False),
        'zipdata':        Param('Whether to zip up experiment data after '
                                'experiment finishes', type=bool, default=True),
        'sendmail':       Param('Whether to send proposal data via email after '
                                'experiment finishes', type=bool,
                                default=False),
        'mailserver':     Param('Mail server name', type=str, settable=True,
                                userparam=False),
        'mailsender':     Param('Mail sender address', settable=True,
                                type=none_or(mailaddress)),
        'mailtemplate':   Param('Mail template file name (in templates)',
                                type=str, default='mailtext.txt'),
        'mailsecurity':   Param('Used encryption layer for smtp communication',
                                type=oneof('none', 'tls', 'ssl'),
                                default='none', settable=True),
        'mailuser':       Param('Username used to login to SMTP server',
                                type=none_or(nonemptystring), default=None,
                                settable=True),
        'serviceexp':     Param('Name of proposal to switch to after user '
                                'experiment', type=nonemptystring,
                                default='service'),
        'servicescript':  Param('Script to run for service time', type=str,
                                default='', settable=True),
        'strictservice':  Param('Only the configured service experiment is '
                                'considered "service"', type=bool,
                                default=False, settable=False),
        'pausecount':     Param('Reason for pausing the count loop', type=str,
                                settable=True, internal=True,
                                no_sim_restore=True),
        'propinfo':       Param('Dict of info for the current proposal',
                                type=dict, default={}, internal=True),
        'proposalpath':   Param('Proposal prefix upon creation of experiment',
                                type=str, internal=True, settable=True),
        'sampledir':      Param('Current sample-specific subdir', type=subdir,
                                default='', internal=True, settable=True),
        'counterfile':    Param('Name of the file with data counters in '
                                'dataroot and datapath', default='counters',
                                userparam=False, type=subdir),
        'errorbehavior':  Param('Behavior on unhandled errors in commands',
                                type=oneof('abort', 'report'), settable=True,
                                default='report'),
        'lastscan':       Param('Last used value of the scan counter - '
                                'ONLY for display purposes', type=int,
                                internal=True),
        'lastpoint':      Param('Last used value of the point counter - '
                                'ONLY for display purposes', type=int,
                                internal=True),
    }

    attached_devices = {
        'sample': Attach('The device object representing the sample', Sample),
    }

    # Selects which class is used for `self.data`, the data manager.
    # Can be overridden in subclasses, but should always be a subclass of the
    # core DataManager.
    datamanager_class = DataManager

    _proposal_thds = {}  # mapping of proposal => FinishExperiment thread

    def doPreinit(self, mode):
        self.__dict__['data'] = self.datamanager_class()

    def doShutdown(self):
        self.data.reset()

    #
    # hooks: may be overriden in derived classes to enhance functionality
    #

    def proposalpath_of(self, proposal):
        """Proposal path of a given proposal.

        Defaults to ``<dataroot>/<year>/<proposal>``, last component MUST be
        the *proposal*.
        """
        return path.join(self.dataroot, time.strftime('%Y'), proposal)

    @property
    def samplepath(self):
        """Path to current active sample, if used, defaults to proposalpath."""
        if self.sampledir:
            return path.join(self.proposalpath, self.sampledir)
        return self.proposalpath

    @property
    def scriptpath(self):
        """Path to the scripts of the current experiment/sample."""
        return path.join(self.samplepath, 'scripts')

    @property
    def elogpath(self):
        """Path to the eLogbook of the current experiment/sample."""
        return path.join(self.samplepath, 'logbook')

    @property
    def datapath(self):
        """Path to the data storage of the current experiment/sample.

        Here scanfiles and images of image-type detectors will be stored.
        """
        return path.join(self.samplepath, 'data')

    @property
    def extrapaths(self):
        """If derived classes need more automatically created dirs, they can
        be put here.
        """
        return tuple()

    @property
    def allpaths(self):
        """Return a list of all autocreated paths.

        Needed to keep track of directory structure upon proposal change.
        """
        return [self.proposalpath, self.datapath,
                self.scriptpath, self.elogpath] + list(self.extrapaths)

    @property
    def templatepath(self):
        """Paths where all template files are stored."""
        return [path.abspath(path.join(self.dataroot, self.templates))] + \
            [path.join(config.setup_package_path, p.strip(), 'template')
             for p in config.setup_subdirs]

    @property
    def proposalsymlink(self):
        """Dataroot based location of 'current' experiment symlink to maintain,
        or empty string.
        """
        return path.join(self.dataroot, 'current')

    @property
    def customproposalsymlink(self):
        """Path of a custom proposal symlink or empty string.
        If a path was specified, the symlink will be created automatically.
        """
        return ''

    @property
    def samplesymlink(self):
        """Dataroot based location of 'current' sample symlink to maintain,
        or empty string.
        """
        return self.proposalsymlink if self.sampledir else ''

    @lazy_property
    def skiptemplates(self):
        """List of template filenames which are to be ignored upon creating
        a new experiment.
        """
        return []

    def getProposalType(self, proposal):
        """Determine proposaltype of a given proposalstring."""
        if proposal in ('template', 'current'):
            raise UsageError(self, 'The proposal names "template" and "current"'
                             ' are reserved and cannot be used')
        # check for defines service 'proposal'
        if proposal == self.serviceexp:
            return 'service'
        # all proposals starting with the defined prefix are user-type,
        # all others are service
        if self.propprefix:
            if proposal.startswith(self.propprefix):
                return 'user'
            return 'other' if self.strictservice else 'service'
        # if we have no prefix, all number-like proposals >0 are usertype,
        # else service
        try:
            if int(proposal) == 0:
                return 'service'
            return 'user'
        except ValueError:
            return 'other' if self.strictservice else 'service'

    #
    # hooks called during new(), can be overridden in subclasses
    #

    def _newCheckHook(self, proptype, proposal):
        """Hook for checking if the given proposal type and name.

        Can raise an exception if e.g. the current user may not open the
        given proposal.
        """

    def _newPropertiesHook(self, proposal, kwds):
        """Hook for querying a database for proposal related data.

        Should return an updated kwds dictionary.
        """
        return kwds

    def _newSetupHook(self):
        """Hook for doing additional setup work on new experiments,
        after everything has been set up.
        """

    #
    # connection to a proposal management system
    #
    def _canQueryProposals(self):
        """Return true if this Experiment can query a proposal management
        system for information.

        This is not a parameter since it may depend for example on the
        currently logged in user.
        """
        return False

    def _queryProposals(self, proposal=None, kwds=None):
        """Query the proposal management system.

        Should only be called if `_canQueryProposals` returns True.

        If *proposal* is not None, it specifies a proposal ID to query.  If it
        is None, query all allowable proposals -- this can take into account
        any restrictions that make sense: e.g. current date, logged in user
        (see `session.getExecutingUser()`) or instrument parameters.

        Must return a list of dictionaries, one per valid proposal, with
        information about the proposal.

        Additional *kwds*, if a dictionary, are merged into each proposal
        information dictionary.

        The following keys are defined, only "proposal" must be present.
        Lists and dictionaries can be empty.  Other keys can be added and
        processed by site-specific implementations.

        * proposal: proposal ID, string
        * session: experiment ID, string (optional)
        * title: string (optional, default is the proposal ID)
        * instrument: string (optional)
        * startdate: datetime (optional)
        * enddate: datetime (optional)
        * default_sample: string (optional), if given must be a name of one
          of the samples in the `samples` dict
        * users: list of dicts with:
          * name: string
          * email: string
          * affiliation: string (optional)
        * localcontacts: list of dicts, with keys same as users
        * samples: optional list of dicts:
          * name: string
        * data_emails: list of addresses to send the data/link to the data to
          (this should be initially set to the user email addresses, but can
          be changed afterwards from GUI/commands)
        * notif_emails: list of addresses to send notifications to
          (this should be initially set to the user and local contact email
          addresses, but can be changed afterwards from GUI/commands)
        * errors: list of problems with this proposal that should be shown
          to the user and prevent using it
        * warnings: list of problems with this proposal that should be shown
          to the user, but not prevent using it

        The data from a chosen proposal is then used as the base for the
        `propinfo` parameter.
        """
        raise NotImplementedError

    #
    # don't override any method defined below in derived classes!
    #

    #
    # other path handling stuff
    #

    def doWriteProposalpath(self, newproposalpath):
        # handle current symlink
        self._set_symlink(self.proposalsymlink, path.relpath(
            newproposalpath, path.dirname(self.proposalsymlink)))
        # HACK: we need the getters to provide the right values....
        self._setROParam('proposalpath', newproposalpath)
        # create all needed subdirs...
        for _dir in self.allpaths:
            ensureDirectory(_dir, **self.managerights)

        # tell elog
        instname = session._instrument and session.instrument.instrument or ''
        session.elogEvent('directory', (newproposalpath, instname,
                                        path.basename(newproposalpath)),
                          store=True)

    def doWriteSampledir(self, newsampledir):
        # handle current symlink
        self._set_symlink(self.samplesymlink,
                          path.join(self.proposalpath, newsampledir))

        # HACK: we need the getters to provide the right values....
        self._setROParam('sampledir', newsampledir)
        # create all needed subdirs...
        for _dir in self.allpaths:
            ensureDirectory(_dir, **self.managerights)

    def _set_symlink(self, location, target):
        if not target or not location:
            return
        if hasattr(os, 'symlink'):
            if path.islink(location):
                self.log.debug('removing symlink %s', location)
                os.unlink(location)
            ensureDirectory(path.join(path.dirname(location), target),
                            **self.managerights)
            self.log.debug('setting symlink %s to %s', location, target)
            os.symlink(target, location)

    #
    # datafile stuff
    #

    def getDataDir(self, *subdirs):
        """Returns the current path for the data directory in subdir
        structure subdirs.

        Returned directory is created if it did not exist.
        """
        dirname = path.abspath(path.join(self.datapath, *subdirs))
        if self._mode != SIMULATION:
            ensureDirectory(dirname, **self.managerights)
        return dirname

    def getDataFilename(self, filepath, *subdirs):
        """Prepends the current data directory to given filepath in subdir
        structure subdirs.

        If filename is an absolute path, ignore the subdirs and start at
        dataroot returned filename is usable 'as-is', i.e. the required
        directory structure is already created.
        """
        if path.isabs(filepath):
            fullname = path.join(self.dataroot, filepath[1:])
        else:
            fullname = path.abspath(path.join(self.datapath,
                                              *(subdirs + (filepath,))))
        dirname = path.dirname(fullname)
        if self._mode != SIMULATION:
            ensureDirectory(dirname, **self.managerights)
        return fullname

    #
    # NICOS interface
    #

    def doInit(self, mode):
        # need to keep a local cache to avoid recursing cache calls when
        # querying
        self._elog_enabled = self.elog

        # check that service proposal is actually resolved as service
        if self.propprefix:
            try:
                int(self.serviceexp)
            except ValueError:
                pass
            else:
                raise ConfigurationError(self, 'the serviceexp parameter '
                                         'must be set to %r, not just %r'
                                         % (self.propprefix + self.serviceexp,
                                            self.serviceexp))

        instname = session._instrument and session.instrument.instrument or ''
        if self._attached_sample.name != 'Sample':
            raise ConfigurationError(self, 'the sample device must now be '
                                     'named "Sample", please fix your system '
                                     'setup')
        if mode != SIMULATION:
            if not self.proposalpath:
                self.log.warning('Proposalpath was not set, initiating a '
                                 'service experiment.')
                self._setROParam('proposalpath',
                                 self.proposalpath_of(self.serviceexp))
                self._setROParam('proptype', 'service')
            if self.elog:
                ensureDirectory(path.join(self.proposalpath, 'logbook'),
                                **self.managerights)
                self._eloghandler = ELogHandler()
                # only enable in master mode, see below
                self._eloghandler.disabled = session.mode != MASTER
                session.addLogHandler(self._eloghandler)
            session.elogEvent('directory', (self.proposalpath,
                                            instname, self.proposal),
                              store=True)
        if not self.templates:
            self._setROParam('templates',
                             path.abspath(path.join(config.nicos_root,
                                                    'template')))

    def doReadTitle(self):
        return self.propinfo.get('title', 'Unknown')

    def doReadUsers(self):
        res = []
        for user in self.propinfo.get('users', []):
            userstr = user['name']
            if user.get('affiliation'):
                userstr += ' (%s)' % user['affiliation']
            res.append(userstr)
        return ', '.join(res)

    def doReadLocalcontact(self):
        if not self.propinfo.get('localcontacts'):
            if session._instrument:
                return session.instrument.responsible

        res = []
        for user in self.propinfo.get('localcontacts', []):
            userstr = user['name']
            if user.get('email'):
                userstr += ' <%s>' % user['email']
            res.append(userstr)
        return ', '.join(res)

    def doUpdateManagerights(self, mrinfo):
        """Check the managerights dict into values used later."""
        if pwd and self._mode != SIMULATION:
            for key, lookup in [('owner', pwd.getpwnam),
                                ('enableOwner', pwd.getpwnam),
                                ('disableOwner', pwd.getpwnam),
                                ('group', grp.getgrnam),
                                ('enableGroup', grp.getgrnam),
                                ('disableGroup', grp.getgrnam)]:
                value = mrinfo.get(key)
                if isinstance(value, str):
                    try:
                        lookup(value)
                    except Exception as e:
                        self.log.warning('managerights: illegal value for key '
                                         '%r: %r (%s)', key, value, e)
        for key in ['enableDirMode', 'enableFileMode',
                    'disableDirMode', 'disableFileMode']:
            value = mrinfo.get(key)
            if value is not None and not isinstance(value, int):
                raise ConfigurationError(
                    self, 'managerights: illegal value for key '
                    '%r: not an integer' % key, exc=1)

    def doUpdateElog(self, on):
        self._elog_enabled = on

    #
    # Experiment handling: New&Finish
    #

    @property
    def mustFinish(self):
        """Return True if the current experiment must be finished before
        starting a new one.
        """
        return self.proptype == 'user'

    def isProposalFinishThreadAlive(self, proposal=None):
        """Return True if the **proposal** is currently finishing. If no
        proposal is provided this method checks for the current proposal.

        """
        if not proposal:
            proposal = self.proposal
        if proposal in self._proposal_thds:
            if self._proposal_thds[proposal].is_alive():
                return True
        return False

    def _cleanupProposalFinishThreads(self):
        """Cleanup already finished threads for proposals
        ``FinishExperiment``.

        """
        for iproposal, thd in list(self._proposal_thds.items()):
            if not thd.is_alive():
                del self._proposal_thds[iproposal]
                self.log.debug('delete reference on closed thread for '
                               'proposal %s', iproposal)

    def hasProposalFinishThreads(self):
        """Cleanup already finished threads for proposals ``FinishExperiment``
        call and return True if any proposal threads exist.

        """
        self._cleanupProposalFinishThreads()
        return bool(self._proposal_thds)

    @usermethod
    def new(self, proposal, title=None, localcontact=None, user=None, **kwds):
        """Called by `.NewExperiment`."""
        if self._mode == SIMULATION:
            raise UsageError('Simulating switching experiments is not '
                             'supported!')

        try:
            # if proposal can be converted to a number, use the canonical form
            # and prepend prefix
            proposal = '%s%d' % (self.propprefix, int(proposal))
        except ValueError:
            pass
        self.log.debug('new proposal real name is %s', proposal)

        if not proposal:
            raise UsageError('Proposal name/number cannot be empty')

        # check proposal type (can raise)
        proptype = self.getProposalType(proposal)
        self.log.debug('new proposal type is %s', proptype)

        # check if we may create this proposal (e.g. check user permissions)
        self._newCheckHook(proptype, proposal)

        # check if we should finish the experiment first
        if proptype == 'user' and self.mustFinish:
            self.log.error('cannot switch directly to new user experiment, '
                           'please use "FinishExperiment" first')
            return

        # combine all arguments into the keywords dict
        if title:
            kwds['title'] = title

        # note: parameter names are singular for backwards compatibility
        if user:
            if isinstance(user, list):
                kwds['users'] = user
            else:
                kwds.setdefault('users', []).append({'name': user})
        if localcontact:
            if isinstance(localcontact, list):
                kwds['localcontacts'] = localcontact
            else:
                kwds.setdefault('localcontacts', []).append(
                    {'name': localcontact}
                )
        kwds['proposal'] = proposal

        # check whether this proposal is finished - a thread is alive
        if self.isProposalFinishThreadAlive(proposal):
            raise NicosError('cannot switch to proposal %s as this is '
                             'currently closing.' % proposal)

        # clean up
        self._cleanupProposalFinishThreads()

        # need to enable before checking templated files...
        # if next proposal is of type 'user'
        if self.managerights and proptype == 'user':
            self.log.debug('managerights: %s', self.managerights)
            self.log.debug('enableDirectory: %s',
                           self.proposalpath_of(proposal))
            enableDirectory(self.proposalpath_of(proposal),
                            logger=self.log, **self.managerights)

        if proptype != 'service':
            if self.templates:
                try:
                    self.checkTemplates(proposal, kwds)  # may raise
                except Exception:
                    # restore previous state completely, thus disabling
                    if self.managerights:
                        disableDirectory(self.proposalpath_of(proposal),
                                         logger=self.log, **self.managerights)
                    raise

        # reset all experiment dependent parameters and values to defaults
        self.remark = ''
        self.elog_hidden = False
        try:
            self.sample.clear()
        except Exception:
            self.sample.log.warning('could not clear sample info', exc=1)
        self.envlist = []
        for notifier in session.notifiers:
            try:
                notifier.reset()
            except Exception:
                notifier.log.warning('could not clear notifier info', exc=1)
        try:
            session.experiment.data.reset_all()
        except Exception:
            self.log.warning('could not clear data manager info', exc=1)

        # set new experiment properties given by caller
        self._setROParam('proptype', proptype)

        # give an opportunity to check proposal database etc.
        propinfo = self._newPropertiesHook(proposal, kwds)
        self._setROParam('propinfo', propinfo)
        # Update cached values of the volatile parameters
        self._pollParam('title')
        self._pollParam('users')
        self._pollParam('localcontact')

        # assignment to proposalpath/sampledir adjusts possible symlinks
        self._setROParam('proposal', proposal)
        # change proposalpath to new value
        self.proposalpath = self.proposalpath_of(proposal)
        # newSample also (re-)creates all needed dirs
        # TODO: apply more properties from the sample if present
        self.sample.new({'name': propinfo.get('default_sample', '')})

        # debug output
        self.log.info('experiment directory is now %s', self.proposalpath)
        self.log.info('script directory is now %s', self.scriptpath)
        self.log.info('data directory is now %s', self.datapath)

        # notify logbook
        session.elogEvent('newexperiment', (proposal, self.title))
        session.elogEvent('setup', list(session.explicit_setups))

        # run hook
        self._newSetupHook()

        # send 'experiment' change event before the last hooks
        # maybe better after the last hook?
        session.experimentCallback(self.proposal, proptype)

        # expand templates
        if proptype != 'service':
            if self.templates:
                self.handleTemplates(proposal, propinfo)
            self.log.info('New experiment %s started', proposal)
        else:
            if self.servicescript:
                from nicos.commands.basic import run
                run(self.servicescript)
            else:
                self.log.debug('not running service script, none configured')
            self.log.info('Maintenance time started')

        self._createCustomProposalSymlink()

    @usermethod
    def update(self, title=None, users=None, localcontacts=None):
        """Update experiment properties.

        This is also called from the GUI panel when changing experiment
        properties.
        """
        propinfo = dict(self.propinfo)
        if title is not None:
            propinfo['title'] = title
        if users is not None:
            propinfo['users'] = users
        if localcontacts is not None:
            propinfo['localcontacts'] = localcontacts
        self._setROParam('propinfo', propinfo)
        # Update cached values of the volatile parameters
        self._pollParam('title')
        self._pollParam('users')
        self._pollParam('localcontact')

    @usermethod
    def finish(self):
        """Called by `.FinishExperiment`. Returns the `FinishExperiment`
        Thread if applicable otherwise `None`.

        Default implementation is to finish the experiment, which means to save
        the data, set the access rights, zipping data, sending email to the
        user, and to call :meth:`doFinish` if present.

        .. method:: doFinish()

           This method is called as part of finish() before the data will be
           packed and/or send via email.
        """
        thd = None

        # zip up the experiment data if wanted
        if self.proptype == 'user':
            if self._mode != SIMULATION:
                if hasattr(self, 'doFinish'):
                    self.doFinish()
                pzip = None
                receivers = None
                if self.sendmail:
                    receivers = self.propinfo.get('data_emails', [])
                if self.zipdata or self.sendmail:
                    pzip = path.join(self.proposalpath, '..', self.proposal +
                                     '.zip')
                try:
                    stats = self._statistics()
                except Exception:
                    self.log.exception('could not gather experiment statistics')
                    stats = self.propinfo.copy()
                # start separate thread for zipping and disabling old proposal
                self.log.debug('starting separate thread for zipping and '
                               'disabling proposal')
                if self.isProposalFinishThreadAlive(self.proposal):
                    self.log.error(
                        'Proposal %s is already finishing. Please report '
                        'this incident as this should not happen.',
                        self.proposal
                    )
                    # XXX: or raise ProgrammingError ?
                    return self._proposal_thds[self.proposal]

                thd = createThread('FinishExperiment ' + self.proposal,
                                   target=self._finish,
                                   args=(pzip, self.proposalpath,
                                         self.proposal, self.proptype, stats,
                                         receivers),
                                   daemon=False)
                # wait up to 5 seconds
                thd.join(5)
                if thd.is_alive():
                    self.log.info('continuing finishing of proposal %s in '
                                  'background', self.proposal)
                    self._proposal_thds[self.proposal] = thd
                else:
                    thd = None

        # switch to service experiment (will hide old data if configured)
        self.new(self.serviceexp)
        return thd

    #
    # template stuff
    #
    def getTemplate(self, tmplname):
        """returns the content of the requested template"""
        for tmpldir in self.templatepath:
            if path.isfile(path.join(tmpldir, tmplname)):
                with open(path.join(tmpldir, tmplname), 'r',
                          encoding='utf-8') as f:
                    return f.read()
        raise OSError('no such template found')

    def iterTemplates(self, only_dot_template=True):
        """iterator of all templates (and their content)..."""
        for tmpldir in self.templatepath[::-1]:  # reversed to keep priority
            if not path.isdir(tmpldir):
                continue
            filelist = os.listdir(tmpldir)
            for fn in filelist:
                if fn == 'README':
                    continue
                if self.mailtemplate and fn.startswith(self.mailtemplate):
                    continue
                if fn in self.skiptemplates:
                    continue
                if only_dot_template and not fn.endswith('.template'):
                    continue
                yield (fn, self.getTemplate(fn))

    def checkTemplates(self, proposal, kwargs):
        """try to fill in all templates to see if some keywords are missing"""
        if self._mode == SIMULATION:
            return  # dont touch fs if in simulation!
        allmissing = []
        alldefaulted = []
        for fn, content in self.iterTemplates(only_dot_template=True):
            newfn = fn[:-9]  # strip ".template" from the name
            newfn, _, _ = expandTemplate(newfn, kwargs)

            finalname = path.join(self.proposalpath_of(proposal), self.sampledir,
                                  'scripts', newfn)

            if path.isfile(finalname):
                self.log.debug('skipping already translated file %r', newfn)
                continue

            self.log.debug('checking template %r', fn)
            _, defaulted, missing = expandTemplate(content, kwargs)
            if missing:
                allmissing.extend(missing)
            if defaulted:
                alldefaulted.extend(defaulted)

        if not allmissing and not alldefaulted:
            return

        # format nicely
        headers = ['missing keyword', 'defaultvalue', 'description']
        errkwds = [item['key'] for item in allmissing]

        items = [[item['key'], item['default'] or '', item['description'] or '']
                 for item in allmissing + alldefaulted]

        def myprintfunc(what):
            if what.strip().split(' ')[0] in errkwds:
                self.log.error(what)
            else:
                self.log.warning(what)

        printTable(headers, items, myprintfunc)
        if allmissing:
            raise NicosError('some keywords are missing, please provide them as '
                             'keyword arguments to `NewExperiment`')

    def handleTemplates(self, proposal, kwargs):
        if self._mode == SIMULATION:
            return  # dont touch fs if in simulation!
        for fn, content in self.iterTemplates(only_dot_template=False):
            istemplate = fn.endswith('.template')
            newfn = fn
            if istemplate:
                newfn = fn[:-9]  # remove '.template' at end
                newfn, _, _ = expandTemplate(newfn, kwargs)
                self.log.debug('%s -> %s', fn, newfn)
            else:
                self.log.debug('%s is no template, just copy it.', fn)

            finalname = path.join(self.scriptpath, newfn)
            if path.isfile(finalname):
                self.log.info('not overwriting existing file %s', newfn)
                continue

            if istemplate:
                self.log.debug('templating file content of %r', fn)
                try:
                    content, _, _ = expandTemplate(content, kwargs)
                except Exception:
                    self.log.warning('could not translate template file %s',
                                     fn, exc=1)
            # save result
            with open(finalname, 'w', encoding='utf-8') as fp:
                fp.write(content)
            os.chmod(finalname, self.managerights.get('enableFileMode',
                                                      DEFAULT_FILE_MODE))

    #
    # various helpers
    #
    def _zip(self, pzip, proposalpath):
        """Zip all files in `proposalpath` folder into `pzip` (.zip) file."""
        self.log.info('zipping experiment data, please wait...')
        zipname = zipFiles(pzip, proposalpath, logger=self.log)
        self.log.info('zipping done: stored as %s', zipname)
        return zipname

    def _upload(self, pzip):
        """Uploads the file `pzip` and returns additional mailbody content."""
        url = ftpUpload(pzip, logger=self.log)
        mailbody = dedent("""
        =====
        Due to size limitations, the attachment has been copied to a temporary
        storage where it will be kept for four weeks.

        Please download the data from:
        %s
        within the next four weeks.
        """) % url
        return mailbody

    def _mail(self, proposal, stats, receivers, zipname,
              maxAttachmentSize=10000000):
        """Send a mail with the experiment data"""

        if self._mode == SIMULATION:
            return  # dont touch fs if in simulation!
        # check parameters
        if not self.mailserver:
            raise NicosError('%s.mailserver parameter is not set' % self)
        if not self.mailsender:
            raise NicosError('%s.mailsender parameter is not set' % self)
        for email in receivers:
            try:
                mailaddress(email)
            except ValueError:
                raise NicosError('need valid email address(es)') from None

        # read and translate mailbody template
        self.log.debug('looking for template in %r', self.templatepath)
        try:
            mailbody = self.getTemplate(self.mailtemplate)
        except OSError:
            self.log.warning('reading mail template %s failed',
                             self.mailtemplate, exc=1)
            mailbody = 'See data in attachment.'

        mailbody, _, _ = expandTemplate(mailbody, stats)

        instname = session._instrument and session.instrument.instrument or '?'
        topic = 'Your recent experiment %s on %s from %s to %s' % \
                (proposal, instname, stats.get('from_date'), stats.get('to_date'))

        self.log.info('Sending data files via eMail to %s', receivers)
        attach_files = []
        if os.stat(zipname).st_size < maxAttachmentSize:
            # small enough -> send directly
            attach_files = [zipname]
        else:
            # not small enough -> upload and send link
            self.log.info('Zipfile is too big to send via email and will be '
                          'uploaded to a temporary storage for download.')
            mailbody += self._upload(zipname)
        sendMail(self.mailserver, receivers, self.mailsender, topic, mailbody,
                 attach_files, self.loglevel == 'debug',
                 security=self.security, username=self.mailuser)

    def _finish(self, pzip, proposalpath, proposal, proptype, stats, receivers):
        if pzip:
            try:
                pzipfile = self._zip(pzip, proposalpath)
            except Exception:
                self.log.warning('could not zip up experiment data', exc=1)
            else:
                if receivers:
                    try:
                        self._mail(proposal, stats, receivers, pzipfile)
                    except Exception:
                        self.log.warning('could not send the data via email',
                                         exc=1)
                # "hide" compressed file by moving it into the
                # proposal directory
                self.log.info('moving compressed file to %s', proposalpath)
                try:
                    os.rename(pzipfile, path.join(proposalpath,
                                                  path.basename(pzipfile)))
                except Exception:
                    self.log.warning('moving compressed file into proposal '
                                     'dir failed', exc=1)
                    # at least withdraw the access rights
                    os.chmod(pzipfile,
                             self.managerights.get('disableFileMode',
                                                   0o400))
        # remove access rights to old proposal if wanted
        if self.managerights and proptype == 'user':
            disableDirectory(proposalpath, logger=self.log,
                             **self.managerights)
            self.log.debug('disabled directory %s', proposalpath)

    def _setMode(self, mode):
        if self.elog:
            self._eloghandler.disabled = mode != MASTER
        Device._setMode(self, mode)

    def _createCustomProposalSymlink(self):
        if not self.customproposalsymlink:
            return

        # create symlink
        ensureDirectory(path.dirname(self.customproposalsymlink),
                        **self.managerights)
        try:
            self.log.debug('create custom proposal symlink %r -> %r',
                           self.customproposalsymlink, self.proposalpath)
            os.symlink(os.path.basename(self.proposalpath),
                       self.customproposalsymlink)
        except OSError:
            self.log.warning('creation of custom proposal symlink failed, '
                             'already existing?')

    @usermethod
    def addUser(self, name, email=None, affiliation=None):
        """Called by `.AddUser`."""
        propinfo = dict(self.propinfo)
        users = list(propinfo.get('users', []))
        users.append({
            'name': name,
            'email': email or '',
            'affiliation': affiliation or '',
        })
        propinfo['users'] = users
        self._setROParam('propinfo', propinfo)
        self.log.info('User "%s" added', name)

    def newSample(self, parameters):
        """Hook called by the sample object to notify of new sample name.

        By default, (re-) creates all needed (sub)dirs that might change
        depending on the sample name/number.
        """
        for _dir in self.allpaths:
            ensureDirectory(_dir, **self.managerights)

    def _statistics(self):
        """Return some statistics about the current experiment in a dict.
        May need improvements.
        """

        # get start of proposal from cache history
        hist, d = [], 7
        # default to 'exp not yet started times'
        to_time = from_time = time.time()
        while not hist and d < 60:
            hist = self.history('proposal', -d * 24)
            d += 7
        if hist:
            from_time = hist[-1][0]
        from_date = time.strftime('%a, %d. %b %Y', time.localtime(from_time))
        to_date = time.strftime('%a, %d. %b %Y', time.localtime(to_time))

        # check number of (scan) data files
        # maybe this should be live collected in propinfo and not
        # after the experiment by scanning the filesystem.
        numscans = 0
        firstscan = 99999999
        lastscan = 0
        scanfilepattern = re.compile(r'%s_(\d{8})\.dat$' % self.proposal)
        for fn in os.listdir(self.datapath):
            m = scanfilepattern.match(fn)
            if m:
                firstscan = min(firstscan, int(m.group(1)))
                lastscan = max(lastscan, int(m.group(1)))
                numscans += 1

        d = {
            'proposal':     self.proposal,
            'from_date':    from_date,
            'to_date':      to_date,
            'firstfile':    '%08d' % firstscan,
            'lastfile':     '%08d' % lastscan,
            'numscans':     str(numscans),
            'title':        self.title,
            'users':        self.users,
            'samplename':   self.sample.samplename,
            'localcontact': self.localcontact,
            'instrument':   session._instrument and session.instrument.instrument or '',
        }
        d.update(self.propinfo)
        return d

    def doWriteRemark(self, remark):
        if remark:
            session.elogEvent('remark', remark)

    def doWriteElog_Hidden(self, hidden):
        session.elogEvent('hidden', hidden, store=True)

    @property
    def sample(self):
        return self._attached_sample

    #
    # Detectorlist
    #
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
                self.log.warning('could not create %r detector device',
                                 detname, exc=1)
                all_created = False
            else:
                if not isinstance(det, Measurable):
                    self.log.warning('cannot use device %r as a '
                                     'detector: it is not a Measurable', det)
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
        # try to create them right now
        self.detectors  # pylint: disable=pointless-statement
        session.elogEvent('detectors', dlist)

    def doUpdateDetlist(self, detectors):
        self._detlist = None  # clear list of actual devices

    #
    # Environment devicelist
    #
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
                self.log.warning('could not create %r environment device',
                                 devname, exc=1)
                all_created = False
            else:
                if not isinstance(dev, (Readable, DevStatistics)):
                    self.log.warning('cannot use device %r as '
                                     'environment: it is not a Readable', dev)
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
        # try to create them right now
        self.sampleenv  # pylint: disable=pointless-statement
        session.elogEvent('environment', dlist)

    def doUpdateEnvlist(self, devices):
        self._envlist = None  # clear list of actual devices

    def _scrubDetEnvLists(self):
        """Remove devices from detlist and envlist that don't exist anymore
        after a setup change.
        """
        newlist = []
        for devname in self.detlist:
            if devname not in session.configured_devices:
                self.log.warning('removing device %r from detector list, it '
                                 'does not exist in any loaded setup', devname)
            else:
                newlist.append(devname)
        self.detlist = newlist
        newlist = []
        for entry in self.envlist:
            devname = entry.split(':')[0]
            if devname not in session.configured_devices:
                self.log.warning('removing device %r from environment, it '
                                 'does not exist in any loaded setup', devname)
            else:
                newlist.append(entry)
        self.envlist = newlist


class ImagingExperiment(Experiment):
    """General experiment device for all imaging instruments.

    This specific experiment takes care about some common data
    (dark images, open beam images) and behaviour for imaging instruments.
    """

    parameters = {
        # for display purposes....
        'lastdarkimage':     Param('Last dark image', type=str, settable=False,
                                   default='', category='general'),
        'lastopenbeamimage': Param('Last Open Beam image', type=str,
                                   settable=False, default='',
                                   category='general'),
        'curimgtype': Param('Type of current/next image',
                            type=oneof('dark', 'openbeam', 'standard'),
                            mandatory=False, default='standard',
                            settable=True),
    }

    @property
    def darkimagedir(self):
        return path.join(self.datapath, 'di')

    @property
    def openbeamdir(self):
        return path.join(self.datapath, 'ob')

    @property
    def photodir(self):
        return path.join(self.proposalpath, 'photos')

    @property
    def extrapaths(self):
        paths = set(Experiment.extrapaths.fget(self))

        paths.add(self.darkimagedir)
        paths.add(self.openbeamdir)
        paths.add(self.photodir)

        return tuple(paths)

    def _clearImgPaths(self):
        # clear state info
        self._setROParam('lastdarkimage', '')
        self._setROParam('lastopenbeamimage', '')

    def new(self, *args, **kwargs):  # pylint: disable=signature-differs
        Experiment.new(self, *args, **kwargs)
        self._clearImgPaths()

    def newSample(self, parameters):
        self.sampledir = safeName(parameters.get('name', ''))
        Experiment.newSample(self, parameters)

        self.log.debug('new sample path: %s', self.samplepath)
        self.log.debug('new data path: %s', self.datapath)
        self.log.debug('new dark image path: %s', self.darkimagedir)
        self.log.debug('new open beam image path: %s', self.openbeamdir)
        self.log.debug('new measurement image path: %s', self.photodir)


class SXTalExperiment(Experiment):
    parameters = {
        'centeredrefs': Param('List of centered reflections',
                              type=list, settable=True,
                              category='experiment'),
        'checkrefs':    Param('List of reflections to re-check regularly',
                              type=list, settable=True,
                              category='experiment'),
    }
