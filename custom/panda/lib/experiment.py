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
#
# *****************************************************************************

"""NICOS PANDA Experiment."""

from __future__ import with_statement

__version__ = "$Revision$"

import os
import re
import time
import threading
import subprocess
from os import path

from nicos.core import Param, UsageError, NicosError
from nicos.utils import disableDirectory, enableDirectory, ensureDirectory, \
     expandTemplate
from nicos.experiment import Experiment
from nicos.utils.proposaldb import queryCycle
from nicos.commands.basic import Run


class PandaExperiment(Experiment):

    parameters = {
        'cycle': Param('Current reactor cycle', type=str, settable=True),
    }

    def _expdir(self, suffix, *parts):
        return path.join('/data/exp', suffix, *parts)

    def new(self, proposal, title=None, **kwds):
        # panda-specific handling of proposal number
        if isinstance(proposal, int):
            proposal = 'p%s' % proposal
        if proposal in ('template', 'current'):
            raise UsageError(self, 'The proposal names "template" and "current"'
                             ' are reserved and cannot be used')

        try:
            old_proposal = os.readlink(self._expdir('current'))
        except Exception:
            if path.exists(self._expdir('current')):
                self.log.error('"current" link to old experiment dir exists '
                                'but cannot be read', exc=1)
            else:
                self.log.warning('no old experiment dir is currently set',
                                  exc=1)
        else:
            if old_proposal.startswith('p'):
                disableDirectory(self._expdir(old_proposal))
            os.unlink(self._expdir('current'))

        # query new cycle
        if 'cycle' not in kwds:
            if self.propdb:
                cycle, started = queryCycle(self.propdb)
                kwds['cycle'] = cycle
            else:
                self.log.error('cannot query reactor cycle, please give a '
                                '"cycle" keyword to this function')
        self.cycle = kwds['cycle']

        # checks are done, set the new experiment
        Experiment.new(self, proposal, title)

        # fill proposal info from database
        if proposal.startswith('p'):
            try:
                propnumber = int(proposal[1:])
            except ValueError:
                pass
            else:
                new_kwds = self._fillProposal(propnumber)
                kwds.update(new_kwds)

        # create new data path and expand templates
        exp_datapath = self._expdir(proposal)
        ensureDirectory(exp_datapath)
        enableDirectory(exp_datapath)
        os.symlink(proposal, self._expdir('current'))

        self.proposaldir = exp_datapath

        ensureDirectory(path.join(exp_datapath, 'scripts'))
        self.scriptdir = path.join(exp_datapath, 'scripts')

        ensureDirectory(path.join(exp_datapath, 'data'))

        if proposal != 'service':
            self._handleTemplates(proposal, kwds)

        self.datapath = [
            path.join(exp_datapath, 'data'),
            '/data/%s/cycle_%s' % (time.strftime('%Y'), self.cycle),
        ]

        if proposal == 'service':
            Run('start_service.py')
        else:
            self._start_editor()

    def _start_editor(self):
        """Open all existing script files in an editor."""
        filelist = [fn for fn in os.listdir(self._expdir('current', 'scripts'))
                    if fn.endswith('.py')]
        # sort filelist to have the start_*.py as the last file
        for fn in filelist:
            if fn.startswith('start_'):
                filelist.remove(fn)
                filelist.append(fn)
                break
        def preexec():
            os.setpgrp()  # create new process group -> doesn't get Ctrl-C
            os.chdir(self._expdir('current', 'scripts'))
        # start it and forget it
        s = subprocess.Popen(['scite'] + filelist,
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
        thread = threading.Thread(target=checker, name='Scite Editor')
        # don't block on closing python if the editor is still running...
        thread.setDaemon(True)
        thread.start()

    def _handleTemplates(self, proposal, kwargs):
        kwargs['proposal'] = proposal
        filelist = os.listdir(self._expdir('template'))
        try:
            # and sort it (start_....py should be first!)
            filelist.remove('start_{{proposal}}.py')
            filelist.insert(0, 'start_{{proposal}}.py')
        except Exception:
            pass # file not in templates, no need to sort towards the end.
        # second: loop through all the files
        for fn in filelist:
            # translate '.py' and '.m' files (reading routines for matlab)
            if not fn.endswith(('.py','.m')):
                self.log.debug('ignoring file %s' % fn)
                continue
            try:
                # translate filename first
                newfn, _, _ = expandTemplate(fn, kwargs)
                self.log.debug('%s -> %s' % (fn, newfn))
                # now read and translate template if file does not already exist
                if path.isfile(self._expdir(proposal, 'scripts', newfn)):
                    self.log.info('file %s already exists, not overwriting'
                                  % newfn)
                    continue
                with open(self._expdir('template', fn)) as fp:
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
                with open(self._expdir(proposal, 'scripts', newfn), 'w') as fp:
                    fp.write(newcontent)
            except Exception:
                self.log.warning('could not translate template file %s' % fn,
                                 exc=1)

    def finish(self, receivers=None):
        """Zip all files in the current experiment folder into a .tgz and send
        them via mail to a given emailadress

        :param receivers: comma-separated string of email adresses of receivers,
            or 'none' to only create the .tgz
        """
        import smtplib
        from email.mime.application import MIMEApplication
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        # check parameters
        if receivers is None:
            raise NicosError('need an email address to work...' )
        if receivers.lower() not in ['none', 'stats'] and '@' not in receivers:
            raise NicosError('need full email address (\'@\' missing!)')
        # checking done, make the file
        propdir = self.proposaldir
        self.log.info('Making %s.tgz out of %s ' % (self.proposal, propdir))
        try:
            subprocess.Popen(['tar', 'zcf', propdir+'.tgz', '-C', propdir, '.'],
                             close_fds=True).wait()
        except Exception:
            self.log.warning('failed')
        else:
            self.log.info('done')
        if receivers.lower() == 'none':
            return # zip, but dont mail...

        # figure out statistics: number of scans, first and last scannumber, min
        # and max date/time
        numscans = 0
        firstscan = 99999999
        lastscan = 0
        from_time = 2**63
        to_time = 0
        scanfilepattern = re.compile(r'%s_(\d{8})\.dat$' % self.proposal)
        for fn in os.listdir(path.join(propdir, 'data')):
            # check if datafile and extract scan-number
            m = scanfilepattern.match(fn)
            if not m:
                continue   # no match -> check next file
            firstscan = min(firstscan, int(m.group(1)))
            lastscan = max(lastscan, int(m.group(1)))
            s = os.stat(path.join(propdir, 'data', fn))
            from_time = min(from_time, s.st_ctime) # only evaluate creation time
            to_time = max(to_time, s.st_ctime)
            numscans += 1

        # now reformat some time information (for codes see
        # http://docs.python.org/library/time.html#time.strftime)
        from_date = time.strftime('%a, %d. %b %Y', time.localtime(from_time))
        to_date = time.strftime('%a, %d. %b %Y', time.localtime(to_time))

        # read and translate mailbody template
        with open(self._expdir('template', 'mailtext.txt')) as fp:
            textfiletext = fp.read()
        textfiletext, _, _ = expandTemplate(textfiletext, {
            'proposal':  self.proposal,
            'from_date': from_date,
            'to_date':   to_date,
            'firstscan': '%08d' % firstscan,
            'lastscan':  '%08d' % lastscan,
            'numscans':  str(numscans)})

        if receivers.lower() == 'stats':
            for line in textfiletext.splitlines():
                self.log.info(line)
            return

        # now we would send the file, so prepare everything
        # TODO: should be put someplace else (config)
        mailserver = 'mailhost.frm2.tum.de'

        # construct msg according to
        # http://docs.python.org/library/email-examples.html#email-examples
        receiverlist = receivers.replace(',', ' ').split()
        receivers = ', '.join(receiverlist)
        mailsender = 'PANDA@frm2.tum.de'
        msg = MIMEMultipart()
        msg['Subject'] = 'Your recent Experiment %s on PANDA from %s to %s' % \
            (self.proposal, from_date, to_date)
        msg['From'] = mailsender
        msg['To'] = receivers
        msg.attach(MIMEText(textfiletext))

        # now attach the tarfile
        with open(propdir + '.tgz', 'rb') as fp:
            tarfiledata = fp.read()

        attachment = MIMEApplication(tarfiledata, 'x-gtar')
        attachment['Content-Disposition'] = \
            'ATTACHMENT; filename="%s.tgz"' % self.proposal
        msg.attach(attachment)

        # now comes the final part: send the mail
        mailer = smtplib.SMTP(mailserver)
        if self.loglevel == 'debug':
            mailer.set_debuglevel(1)
        self.log.info('Sending data files via eMail to %s' % receivers)
        mailer.sendmail(mailsender, receiverlist + [mailsender], msg.as_string())
        mailer.quit()

        # now we are deleting the (old) datafiles (only the version in the user
        # directory, we still have them in the cycle_../dir and in the tarfile)

        #for fn in os.listdir(self._expdir(self.proposal, 'data')):
        #    m = scanfilepattern.match(fn)
        #    if not m: continue   # no match -> check next file
        #    self.log.info('would delete %s' % fn)
        #    #os.remove(self._expdir(self.proposal, 'data', files))

        self.log.info('hiding tarfile')
        try:
            os.rename(propdir + '.tgz',
                      path.join(propdir, self.proposal + '.tgz'))
        except Exception:
            self.log.warning('WARNING: moving of tarfile failed!', exc=1)
            os.chmod(propdir+'.tgz' , 000) # at least withdraw the access rights

        # switch to service experiment
        self.new('service')
