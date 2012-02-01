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
from nicos.utils import disableDirectory, enableDirectory, ensureDirectory, expandTemplate
from nicos.experiment import Experiment
from nicos.utils.proposaldb import queryCycle
from nicos.commands.basic import Run


class PandaExperiment(Experiment):

    parameters = {
        'cycle': Param('Current reactor cycle', type=str, settable=True),
    }

    def _expdir(self, suffix):
        return '/data/exp/' + suffix

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
                self._fillProposal(propnumber)

        # create new data path and expand templates
        exp_datapath = self._expdir(proposal)
        ensureDirectory(exp_datapath)
        enableDirectory(exp_datapath)
        os.symlink(proposal, self._expdir('current'))

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
            Run( 'start_service.py' )
        else:
            self._start_editor()
            
    def _start_editor(self):
        filelist=[k for k in os.listdir( path.join(self._expdir( 'current' ), 'scripts') ) if k.endswith('.py')]
        # sort filelist to have the start_*.py as the last file
        for f in filelist:
            if f.startswith('start_'):
                filelist.remove(f)
                filelist.append(f)
        # block signals
        def sigblock():
            import signal
            signal.signal( signal.SIGINT, signal.SIG_IGN) # block CTRL-C
            os.chdir(path.join(self._expdir('current'), 'scripts'))
        s=subprocess.Popen( 
            ['scite']+filelist, 
            close_fds=True, 	
            stdin=subprocess.PIPE, 
            stdout=os.tmpfile(), 
            stderr=subprocess.STDOUT, 
            preexec_fn=sigblock
        ) # start it and forget it
        def checker():
            while None==s.returncode:
                time.sleep(1)
                s.poll()
        thread=threading.Thread(target=checker,name='Scite Editor')	# somebody needs to check the return value, if the process ends
        thread.setDaemon(True) # don't block on closing python if the editor is still running...
        thread.start()

    def _handleTemplates(self, proposal, kwargs):
        kwargs['proposal'] = proposal
        filelist = os.listdir(self._expdir( 'template' ))
        try:
            filelist.remove('start_{{proposal}}.py')	#and sort it (start_....py should be first!)
            filelist.insert(0, 'start_{{proposal}}.py')
        except Exception:
            pass	# file not in templates, no need to sort towards the end.
        # second: loop through all the files
        for files in filelist:
            if not files.endswith(('.py','.m')) : # translate '.py'-files (and '.m' files (reading routines for matlab)
                self.log.info('ignoring file %s' % files)
                continue
            try:
                # translate filename first
                newfile, _ = expandTemplate(files, kwargs)
                self.log.debug('%s -> %s' % (files, newfile))
                # now read and translate template if file does not already exist....
                if path.isfile(path.join(self._expdir(proposal), 'scripts', newfile)):
                    self.log.info('file %s already exists, not overwriting' % newfile)
                    continue
                with open(path.join(self._expdir('template'), files)) as fp:
                    content = fp.read()
                newcontent, defaulted = expandTemplate(content, kwargs)
                if defaulted:
                    self.log.info('the following keyword argument(s) were taken from defaults:')
                    self.log.info('%12s (%s) %-s' % ('keyword','default','Description'))
                    for entry in defaulted:
                        self.log.info('%12s (%s)\t%-s' % (entry['key'], entry['default'], entry['description']))
                # check for startupfile and insert our own call to save all the values in the beginning
                # therefore -> the startupfile needs to be the last one! (so all maybe missing keywords were found already...)
                #~ if files=='start_{{proposal}}.py': # disabled by request of Astrid
                #~ template="#~ NewExperiment( '"+pnops+"',\n\t#~ %s )\n"%(',\n\t#~ '.join(['%s=\'%s\''%(k,v) for k,v in kwargs.items()]))+template
                # ok, both filename and filecontent are ok and translated -> save (if not already existing)
                with open(path.join(self._expdir(proposal), 'scripts', newfile), 'w') as fp:
                    fp.write(newcontent)
                    fp.flush()
            except Exception:
                self.log.warning('could not translate template file %s' % files, exc=1)

    def finish(self, receivers=None):
        ''' zips all files in the current experiment-folder into a .tgz and sends them via mail to a given emailadress
        @param receivers Comma-separated string of email adresses of receivers, or 'none' to only create the .tgz
        '''
        import smtplib
        from email.mime.application import MIMEApplication
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        # check parameters
        if receivers==None:
            raise NicosError('need an email adress to work...' )
        if not receivers.lower() in ['none','stats'] and receivers.find('@') == -1:
            raise NicosError('need full email address (\'@\' missing!)')
        # checking done, make the file
        propdir=self._expdir(self.proposal)
        self.log.info('Making %s.tgz out of %s'%(self.proposal,propdir))
        #~ subprocess.call( ('tar', 'zcf', propdir+'.tgz', '-C', propdir, '.' ), close_fds=True, stderr=subprocess.STDOUT )
        try:
            subprocess.Popen( ('tar', 'zcf', propdir+'.tgz', '-C', propdir, '.' ), close_fds=True ).wait()
        except Exception:
            pass
        self.log.info('done')
        #~ if receivers.lower()=='none' or pnops[0]!='p': return # zip, but dont mail...   # removed as requested by Astrid
        if receivers.lower()=='none':
            return # zip, but dont mail...

        # figure out statistics: number of scans, first and last scannumber, min and max date/time
        numscans=0L
        firstscan=99999999
        lastscan=0
        from_time=2**63
        to_time=0
        scanfilepattern=re.compile('^%s_(\d{8,8})\\.dat$'%self.proposal)
        for files in os.listdir( path.join(propdir, 'data' )):
            m=scanfilepattern.findall( files )	# check if datafile and extract scan-number
            if not m:
                continue		# no match -> check next file
            firstscan=min(firstscan,long(m[0]))
            lastscan=max(lastscan,long(m[0]))
            s=os.stat( path.join(propdir, 'data', files))
            from_time=min( from_time, s.st_ctime ) # only evaluate creation time
            to_time=max( to_time, s.st_ctime )
            numscans+=1

        # now reformat some time information (for codes see http://docs.python.org/library/time.html#time.strftime )
        from_date=time.strftime( '%a, %d. %b %Y', time.localtime( from_time ) )
        to_date=time.strftime( '%a, %d. %b %Y', time.localtime( to_time ) )

        # read and translate mailbody-template
        with open( path.join(self._expdir( 'template'),'mailtext.txt' ),'r') as fp:
            textfiletext = fp.read()
        textfiletext, _ = expandTemplate(textfiletext, {
                'proposal': self.proposal,
                'from_date':from_date,
                'to_date':to_date, 
                'firstscan':'%08d'%firstscan,
                'lastscan':'%08d'%lastscan,
                'numscans':'%d'%numscans})
                
        if receivers.lower() == 'stats':
            for line in textfiletext.splitlines():
                self.log.info(line)
            return
        
        # now we would send the file, so prepare everything
        mailserver='mailhost.frm2.tum.de'	# TODO: should be put someplace else (config)

        # construct msg according to http://docs.python.org/library/email-examples.html#email-examples
        receivers=', '.join( receivers.replace( ',', ' ' ).split() )
        mailsender='PANDA@frm2.tum.de'
        msg=MIMEMultipart()
        msg['Subject'] = 'Your recent Experiment %s on PANDA from %s to %s'%(self.proposal, from_date, to_date)
        msg['From'] = mailsender
        msg['To'] = receivers

        msg.attach( MIMEText( textfiletext ) )

        # now attach the tarfile
        with open( propdir+'.tgz', 'rb' ) as fp:
            tarfiledata=fp.read()

        attachment=MIMEApplication( tarfiledata, 'x-gtar' )
        attachment['Content-Disposition']='ATTACHMENT; filename="%s.tgz"'%self.proposal

        msg.attach( attachment )

        # now comes the final part: send the mail
        mailer=smtplib.SMTP( mailserver )
        #~ mailer.set_debuglevel(1)
        self.log.info('Sending Data files via eMail to %s'%receivers)
        mailer.sendmail( mailsender, receivers.replace( ',', ' ' ).split() + [ mailsender ], msg.as_string() )
        mailer.quit()

        # now we are deleting the (old) datafiles (only the version in the user directory, we still have them in the cycle_../dir and in the tarfile)
        #for files in os.listdir( _expdir( pnops ) ):
        #       m=scanfilepattern.findall( files )	# check if datafile and extract scan-number
        #       if not(m): continue		# no match -> check next file
        #       NicmPrint(PM_STANDARD,'Would delete %s'%files) # not deleting yet, since we are still TESTING IT
        #       #os.remove( _expdir( pnops, files ) )

        self.log.info('hiding tarfile')
        try:
            os.rename(propdir + '.tgz', path.join(propdir, self.proposal + '.tgz'))
        except Exception:
            self.log.warning('WARNING: moving of tarfile failed!', exc=1)
            os.chmod(propdir+'.tgz' , 000) # at least withdraw the access rights....

        self.new('service')
