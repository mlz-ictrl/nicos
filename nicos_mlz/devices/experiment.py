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
#   Georg Brandl <g.brandl@fz-juelich.de>
#   Jens Krüger <jens.krueger@frm2.tum.de>
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

"""NICOS FRM II experiment classes."""

import re
import time
from os import path

from nicos import session
from nicos.core import NicosError, Override, Param, UsageError, oneof
from nicos.devices.experiment import Experiment as BaseExperiment, \
    ImagingExperiment as BaseImagingExperiment
from nicos.utils import expandTemplate, safeName

PROPOSAL_RE = re.compile(r'P\d+-\d+$')


class Experiment(BaseExperiment):
    """Typical experiment at the FRM II facility.

    Allows access to the GhOST user office database -- if the user has
    logged into NICOS using its credentials -- to query proposal details.
    Also controls access to proposals based on this.
    """

    parameters = {
        'reporttemplate': Param('File name of experimental report template '
                                '(in templates)',
                                type=str, default='experimental_report.rtf'),
    }

    parameter_overrides = {
        'propprefix': Override(default=''),
        'mailserver': Override(default='mailhost.frm2.tum.de'),
        'strictservice': Override(default=True),
    }

    @property
    def ghost(self):
        """Return the GhOST API proxy if the current user was authenticated
        against GhOST, else None.
        """
        return session.getExecutingUser().data.get('ghost')

    def getProposalType(self, proposal):
        if proposal in ('template', 'current'):
            raise UsageError(self, 'The proposal names "template" and "current"'
                             ' are reserved and cannot be used')
        if PROPOSAL_RE.match(proposal):
            return 'user'
        if proposal == self.serviceexp:
            return 'service'
        return 'other' if self.strictservice else 'service'

    def _newCheckHook(self, proptype, proposal):
        # check if user may start this proposal
        if self.ghost is None:
            return  # no way to check
        if proptype == 'user':
            if not self.ghost.canStartProposal(proposal):
                raise NicosError(self, 'Current user may not start this '
                                 'proposal')
        elif proptype == 'other':
            if not self.ghost.isLocalContact():
                raise NicosError(self, 'Current user may not start a '
                                 'non-user proposal')

    def _newPropertiesHook(self, proposal, kwds):
        if 'cycle' not in kwds:
            # for compatibility with templates expecting a cycle number
            kwds['cycle'] = 'unknown_cycle'
        if self.proptype == 'user':
            if self.ghost is not None:
                self._fillProposal(proposal, kwds)
        return kwds

    def _newSetupHook(self):
        # TODO: set up datacloud access here
        pass

    def _canQueryProposals(self):
        return 'ghost' in session.getExecutingUser().data

    def _queryProposals(self, proposal=None, kwds=None):
        if self.ghost is None:
            raise NicosError('cannot query proposals for logged-in user')
        res = self.ghost.queryProposals(proposal)
        if kwds:
            for prop in res:
                res[prop].update(kwds)
        return res

    def _fillProposal(self, proposal, kwds):
        try:
            res = self.ghost.queryProposals(proposal)[0]
        except Exception:
            self.log.warning('could not query proposal info to '
                             'fill metadata', exc=1)
            return
        for key in res:
            if key not in kwds:
                kwds[key] = res[key]

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

        with open(path.join(self.proposalpath, newfn), 'w',
                  encoding='utf-8') as fp:
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
