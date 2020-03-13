#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

"""NICOS FRM II experiment classes."""

import re
import time
from os import path

from nicos import session
from nicos.core import Override, Param, oneof
from nicos.devices.experiment import Experiment as BaseExperiment, \
    ImagingExperiment as BaseImagingExperiment
from nicos.utils import expandTemplate, safeName


def queryCycle():
    raise NotImplementedError


def queryProposal(prop, instr):
    raise NotImplementedError


class Experiment(BaseExperiment):
    """Typical experiment at the FRM II facility.

    With access to the user office proposal database information the experiment
    related information could be take over without any human interaction except
    the knowledge of the proposal number.
    """

    parameters = {
        'cycle':   Param('Current reactor cycle', type=str, settable=True),
        'propdb':  Param('Filename with credentials string for proposal DB',
                         type=str, default='', userparam=False),
        'reporttemplate': Param('File name of experimental report template '
                                '(in templates)',
                                type=str, default='experimental_report.rtf'),
    }

    parameter_overrides = {
        'mailserver':  Override(default='mailhost.frm2.tum.de'),
    }

    def _newPropertiesHook(self, proposal, kwds):
        if 'cycle' not in kwds:
            if self.propdb:
                try:
                    cycle, _started = queryCycle()
                    kwds['cycle'] = cycle
                except Exception:
                    self.log.warning('cannot query reactor cycle', exc=1)
                    kwds['cycle'] = 'unknown_cycle'
            else:
                self.log.warning('cannot query reactor cycle, please give a '
                                 '"cycle" keyword to this function')
                kwds['cycle'] = 'unknown_cycle'
        self.cycle = kwds['cycle']
        if self.proptype == 'user':
            upd = self._fillProposal(int(proposal[len(self.propprefix):]), kwds)
            if isinstance(upd, dict):
                kwds.update(upd)
        return kwds

    def _canQueryProposals(self):
        return bool(self.propdb)

    def _queryProposals(self, proposal=None, kwds=None):
        res = self._fillProposal(proposal, kwds or {})
        return [] if res is None else [res]

    # pylint: disable=inconsistent-return-statements
    def _fillProposal(self, proposal, kwds):
        """Fill proposal info from proposal database."""
        if not self.propdb:
            return
        try:
            instrument, info = queryProposal(proposal,
                                             session.instrument.instrument)
        except Exception:
            self.log.warning('unable to query proposal info', exc=1)
            return

        if info.get('wrong_instrument'):
            return

        # check permissions
        if info.get('permission_security', 'no') != 'yes':
            self.log.error('No permission for this experiment from '
                           'security!  Please call 12699 (929-142).')
        if info.get('permission_radiation_protection', 'no') != 'yes':
            self.log.error('No permission for this experiment from '
                           'radiation protection! Please call 14955 '
                           '(14739/929-090).')

        kwds['permission_security'] = info.get('permission_security', 'no')
        kwds['permission_radiation_protection'] = \
            info.get('permission_radiation_protection', 'no')

        what = []
        info['instrument'] = instrument
        # Extract NEW information
        if info.get('title') and not kwds.get('title'):
            what.append('title')
            kwds['title'] = info['title']
        if info.get('substance') and not kwds.get('sample'):
            what.append('sample name')
            kwds['sample'] = info['substance']
            formula = info.get('formula')
            if formula:
                kwds['sample'] += ' / ' + formula
        if info.get('user') and not kwds.get('user'):
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
        # requested/assigned local contact
        # if info.get('local_contact', '-1') != '-1' \
        #         and not kwds.get('localcontact'):
        #     kwds['localcontact'] = info['local_contact'].replace('.', ' ')
        #     what.append('local contact')
        # requested sample environment
        v = []
        for k in 'cryo furnace magnet pressure'.split():
            if info.get(k):
                v.append("%s = %s" % (k, info.get(k)))
        if v:
            what.append('requested sample environment')
            kwds['se'] = ', '.join(v)
        # include supplementary stuff to make it easier to fill in exp.
        # report templates
        kwds['affiliation'] = info.get('affiliation', '')
        kwds['user_email'] = info.get('user_email', '')
        # display info about values we got.
        if what:
            self.log.info('Filled in %s from proposal database',
                          ', '.join(what))
        # make sure we can relay on certain fields to be set, even if they are
        # not in the DB
        kwds.setdefault('se', 'none specified')
        kwds.setdefault('user', 'main proposer')
        kwds.setdefault('title', 'title of experiment p%s' % proposal)
        kwds.setdefault('sample', 'sample of experiment p%s' % proposal)
        kwds.setdefault('localcontact', session.instrument.responsible)
        kwds.setdefault('user_name', info.get('user'))
        kwds.setdefault('affiliation', 'MLZ Garching; Lichtenbergstr. 1; '
                        '85748 Garching; Germany')
        return kwds

    def doFinish(self):
        try:
            self._generateExpReport()
        except Exception:
            self.log.warning('could not generate experimental report',
                             exc=1)

    def _generateExpReport(self):
        if not self.reporttemplate:
            return
        # read and translate ExpReport template
        self.log.debug('looking for template in %r', self.templatepath)
        try:
            data = self.getTemplate(self.reporttemplate)
        except IOError:
            self.log.warning('reading experimental report template %s failed, '
                             'please fetch a copy from the User Office',
                             self.reporttemplate)
            return  # nothing to do about it.

        # prepare template....
        # can not do this directly in rtf as {} have special meaning....
        # KEEP IN SYNC WHEN CHANGING THE TEMPLATE!
        # reminder: format is {{key:default#description}},
        # always specify default here !
        #
        # first clean up template
        data = data.replace('\\par Please replace the place holder in the upper'
                            ' part (brackets <>) by the appropriate values.', '')
        data = data.replace('\\par Description', '\\par\n\\par '
                            'Please check all pre-filled values carefully! '
                            'They were partially read from the proposal and '
                            'might need correction.\n'
                            '\\par\n'
                            '\\par Description')
        # replace placeholders with templating markup
        # TODO: change placeholders
        data = data.replace('<your title as mentioned in the submission form>',
                            '"{{title:The title of your proposed experiment}}"')
        data = data.replace('<proposal No.>', 'Proposal {{proposal:0815}}')
        data = data.replace('<your name> ', '{{users:A. Guy, A. N. Otherone}}')
        data = data.replace('<coauthor, same affilation> ', 'and coworkers')
        data = data.replace('<other coauthor> ', 'S. T. Ranger')
        data = data.replace('<your affiliation>, }',
                            '{{affiliation:affiliation of main proposer and '
                            'coworkers}}, }\n\\par ')
        data = data.replace('<other affiliation>', 'affiliation of coproposers '
                            'other than 1')
        data = data.replace('<Instrument used>',
                            '{{instrument:<The Instrument used>}}')
        data = data.replace('<date of experiment>', '{{from_date:01.01.1970}} '
                            '- {{to_date:12.03.2038}}')
        data = data.replace('<local contact>', '{{localcontact:L. Contact '
                            '<l.contact@frm2.tum.de>}}')

        # collect info
        stats = self._statistics()
        # encode all text that may be Unicode into RTF \u escapes
        for key in stats:
            if isinstance(stats[key], str):
                stats[key] = stats[key].encode('rtfunicode')

        # template data
        newcontent, _, _ = expandTemplate(data, stats)
        newfn, _, _ = expandTemplate(self.reporttemplate, stats)

        with open(path.join(self.proposalpath, newfn), 'w') as fp:
            fp.write(newcontent)
        self.log.info('An experimental report template was created at %r for '
                      'your convenience.', path.join(self.proposalpath, newfn))


class ImagingExperiment(Experiment, BaseImagingExperiment):
    """FRM II specific imaging experiment which provides all imaging experiment
    functionalities plus all the FRM II specific features.
    """

    parameters = {
        'curimgtype': Param('Type of current/next image',
                            type=oneof('dark', 'openbeam', 'standard'),
                            mandatory=False, default='standard',
                            settable=True),
    }

    parameter_overrides = {
        'dataroot':      Override(default='/data/FRM-II'),
    }

    @property
    def elogpath(self):
        """path to the eLogbook of the current experiment/sample"""
        return path.join(self.proposalpath, 'logbook')

    @property
    def extrapaths(self):
        paths = set(Experiment.extrapaths.fget(self))
        paths.update(BaseImagingExperiment.extrapaths.fget(self))
        if self.sampledir:
            paths.add(path.join(self.samplepath, 'eval', 'recon'))

        return tuple(paths)

    @property
    def customproposalsymlink(self):
        if self.proptype == 'service':
            return None

        # construct user name
        user = re.split('[,(<@]', self.users)[0].strip()
        user = user if user else 'Unknown User'

        date = time.strftime('%F').replace('-', '_')
        return path.join(self.proposalpath, '..',
                         safeName('%s-%s-%s-%s' %
                                  (date, user, self.proposal, self.title)))

    def newSample(self, parameters):
        name = parameters['name']
        self.sampledir = safeName(name)

        Experiment.newSample(self, parameters)

        self.log.debug('new sample path: %s', self.samplepath)
        self.log.debug('new data path: %s', self.datapath)
        self.log.debug('new dark image path: %s', self.darkimagedir)
        self.log.debug('new open beam image path: %s', self.openbeamdir)
        self.log.debug('new measurement image path: %s', self.photodir)
