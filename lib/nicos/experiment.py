#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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

__version__ = "$Revision$"

import os
import time
import datetime
from os import path
from uuid import uuid1

try:
    import MySQLdb
except ImportError:
    MySQLdb = None

from nicos import session
from nicos.data import NeedsDatapath, Dataset
from nicos.utils import listof, nonemptylistof, ensureDirectory, usermethod
from nicos.device import Device, Measurable, Readable, Param
from nicos.errors import ConfigurationError, UsageError
from nicos.loggers import ELogHandler


class ProposalDB(object):
    def __init__(self,credentials):
        try:
            self.user, hostdb = credentials.split('@')
            self.host, self.db = hostdb.split(':')
        except ValueError:
            raise ConfigurationError('%r is an invalid credentials string '
                                     '(user "user@host:dbname")' % credentials)
        if MySQLdb is None:
            raise ConfigurationError('MySQL adapter is not installed')

    def __enter__(self):
        self.conn = MySQLdb.connect(host=self.host, user=self.user, db=self.db)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, *exc):
        self.cursor.close()
        self.conn.close()


def queryCycle(credentials):
    """Query the FRM-II proposal database for the current cycle."""
    today = datetime.date.today()
    with ProposalDB(credentials) as cur:
        cur.execute('''
            SELECT value, xname FROM Cycles, Cycles_members, Cycles_values
            WHERE mname = "_CM_START" AND value <= %s
            AND Cycles_values._mid = Cycles_members.mid
            AND Cycles_values._xid = Cycles.xid
            ORDER BY xid DESC LIMIT 1''', (today,))
        row = cur.fetchone()
        startdate = datetime.datetime.strptime(row[0], '%Y-%m-%d').date()
        cycle = row[1]
    return cycle, startdate


def queryProposal(credentials, pnumber):
    """Query the FRM-II proposal database for information about the given
    proposal number.
    """
    if not isinstance(pnumber, (int, long)):
        raise UsageError('proposal number must be an integer')
    if session.instrument is None:
        raise UsageError('cannot query proposals, no instrument configured')
    with ProposalDB(credentials) as cur:
        # get proposal title and properties
        cur.execute('''
            SELECT xname, mname, value
            FROM Proposal, Proposal_members, Proposal_values
            WHERE xid = %s AND xid = _xid AND mid = _mid
            ORDER BY abs(mid-4.8) ASC''', (pnumber,))
        rows = cur.fetchall()
        # get user info
        cur.execute('''
            SELECT name, user_email, institute1 FROM nuke_users, Proposal
            WHERE user_id = _uid AND xid = %s''', (pnumber,))
        userrow = cur.fetchone()
    if not rows or len(rows) < 3:
        raise UsageError('proposal %s does not exist in database' % pnumber)
    if not userrow:
        raise UsageError('user does not exist in database')
    # structure of returned data: (title, user, prop_name, prop_value)
    info = {
        'title': rows[0][0],
        'user': userrow[0],
        'user_email': userrow[1],
        'affiliation': userrow[2],
    }
    for row in rows:
        # extract the property name in a form usable as dictionary key
        key = row[1][4:].lower().replace('-', '_')
        value = row[2]
        if key == 'instrument':
            if value[4:].lower() != session.instrument.instrument.lower():
                raise UsageError('proposal %s is not a proposal for this '
                                 'instrument, but %s' % (pnumber, value[4:]))
        if value:
            info[key] = value
    return info


class Sample(Device):
    """A special device to represent a sample."""

    parameters = {
        'samplename':  Param('Sample name', type=str, settable=True),
    }

    def doWriteSamplename(self, name):
        if name:
            session.elog_event('sample', name)


class Experiment(Device):
    """A special singleton device to represent the experiment."""

    parameters = {
        'title':     Param('Experiment title', type=str, settable=True,
                           category='experiment'),
        'proposal':  Param('Proposal number or proposal string',
                           type=str, settable=True, category='experiment'),
        'users':     Param('User names', type=listof(str), settable=True,
                           category='experiment'),
        'remark':    Param('Current remark about experiment configuration',
                           type=str, settable=True, category='experiment'),
        'datapath':  Param('List of paths where data files should be stored',
                           type=nonemptylistof(str), default=['.'],
                           mandatory=True, settable=True,
                           category='experiment'),
        'detlist':   Param('List of default detectors', type=listof(str),
                           settable=True),
        'envlist':   Param('List of default environment devices to read '
                           'at every scan point', type=listof(str),
                           settable=True),
        'scriptdir': Param('Standard script directory', type=str,
                           default='.', settable=True),
        'propdb':    Param('user@host:dbname credentials for proposal DB',
                           type=str, default='', userparam=False),
    }

    attached_devices = {
        'sample': Sample,
    }

    def doInit(self):
        self._last_datasets = []
        ensureDirectory(path.join(self.datapath[0], 'logbook'))
        instname = session.instrument and session.instrument.instrument or ''
        session.elog_event('directory', (self.datapath[0],
                                         instname, self.proposal))
        self._eloghandler = ELogHandler()
        # only enable in master mode, see below
        self._eloghandler.disabled = session.mode != 'master'
        session.addLogHandler(self._eloghandler)

    @usermethod
    def new(self, proposal, title=None, **kwds):
        # Individual instruments should override this to change datapath
        # according to instrument policy, and maybe call _fillProposal
        # to get info from the proposal database
        if isinstance(proposal, (int, long)):
            proposal = str(proposal)
        self.proposal = proposal
        self.title = title or ''
        # reset everything else to defaults
        self.remark = ''
        self.users = []
        self.sample.samplename = ''
        #self.envlist = []
        #self.detlist = []
        session.elog_event('newexperiment', (proposal, title))
        session.elog_event('setup', list(session.explicit_setups))

    def _setMode(self, mode):
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
        if info.get('title') and self.title == '':
            self.title = info['title']
            what.append('title')
        if info.get('substance'):
            self.sample.samplename = info['substance']
            what.append('sample name')
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
        if what:
            self.log.info('Filled in %s from proposal database' %
                           ', '.join(what))

    @usermethod
    def addUser(self, name, email, affiliation=None):
        user = '%s <%s>' % (name, email)
        if affiliation is not None:
            user += ', ' + affiliation
        self.users = self.users + [user]
        self.log.info('User "%s" added' % self.users[-1])

    def finish(self):
        pass

    def doWriteRemark(self, remark):
        if remark:
            session.elog_event('remark', remark)

    def doWriteDatapath(self, paths):
        for datapath in paths:
            if not path.isdir(datapath):
                os.makedirs(datapath)
        ensureDirectory(path.join(paths[0], 'logbook'))
        instname = session.instrument and session.instrument.instrument or ''
        session.elog_event('directory', (paths[0], instname, self.proposal))
        for dev in session.devices.itervalues():
            if isinstance(dev, NeedsDatapath):
                dev.datapath = paths

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
        return self._detlist

    def setDetectors(self, detectors):
        dlist = []
        for det in detectors:
            if isinstance(det, Device):
                det = det.name
            dlist.append(det)
        self.detlist = dlist
        session.elog_event('detectors', dlist)

    def doUpdateDetlist(self, detectors):
        detlist = []
        for detname in detectors:
            try:
                det = session.getDevice(detname)
            except Exception:
                self.log.exception('could not create %r detector device' %
                                   detname)
            else:
                if not isinstance(det, Measurable):
                    raise UsageError(self, 'cannot use device %r as a detector:'
                                     ' it is not a Measurable' % det)
                detlist.append(det)
        self._detlist = detlist

    @property
    def sampleenv(self):
        return self._envlist

    def setEnvironment(self, devices):
        dlist = []
        for dev in devices:
            if isinstance(dev, Device):
                dev = dev.name
            dlist.append(dev)
        self.envlist = dlist
        session.elog_event('environment', dlist)

    def doUpdateEnvlist(self, devices):
        devlist = []
        for devname in devices:
            try:
                dev = session.getDevice(devname)
            except Exception:
                self.log.exception('could not create %r environment device' %
                                   devname)
            else:
                if not isinstance(dev, Readable):
                    raise UsageError(self, 'cannot use device %r as environment:'
                                     ' it is not a Readable' % dev)
                devlist.append(dev)
        self._envlist = devlist
