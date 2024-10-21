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
#   Petr Cermak <cermak@mag.mff.cuni.cz>
#
# *****************************************************************************

"""NICOS MGML experiment classes."""

from datetime import datetime
from json import loads as parsejson
from math import isnan
from time import time

from requests_oauthlib import OAuth2Session

from nicos import session
from nicos.commands.output import printinfo
from nicos.core import ADMIN, USER, Attach, Param, UsageError
from nicos.core.params import dictof, none_or
from nicos.core.utils import usermethod
from nicos.devices.experiment import Experiment as BaseExperiment

from nicos_mgml.devices.cryostat import Cryostat


class Experiment(BaseExperiment):
    """User experiment at the MGML.

    With access to the MGML dashboard information the experiment
    related information could be take over without any human interaction except
    the knowledge of the proposal number.
    """

    parameters = {
        'dashboardurl': Param(
            '', type=str, default='https://user.mgml.eu', userparam=False
        ),
        'consumed': Param(
            'List of consumed resources',
            type=dictof(str, float),
            internal=True,
            chatty=True,
            userparam=True,
        ),
        'started': Param(
            'Time when experiment started (sec since epoch), none if not started.',
            type=none_or(float),
            userparam=False,
            internal=True,
            default=None,
        ),
    }

    def _newPropertiesHook(self, proposal, kwds):
        if self.proptype == 'user' and self._canQueryProposals():
            upd = self._queryProposals(proposal, kwds)
            if isinstance(upd, dict):
                kwds.update(upd)
        return kwds

    def _canQueryProposals(self):
        """Return true if this Experiment can query user Dashboard."""

        loggedUser = session.getExecutingUser()
        return 'token' in loggedUser[2]

    def _queryProposals(self, proposal=None, kwds=None):
        try:
            userInfo = session.getExecutingUser()[2]
        except Exception:
            self.log.warning('oAuth token missing for current user.', exc=1)
            return []

        dashboard = OAuth2Session(userInfo['clientid'], token=userInfo['token'])
        r = dashboard.get(self.dashboardurl + '/rest/activeproposals/')
        proposals = parsejson(r.content)
        for p in proposals:
            emails = set([])
            for u in p.get('users', []) + p.get('localcontacts', []):
                emails.add(u['email'])
            p['notif_emails'] = emails
            p['data_emails'] = emails
        if proposal:
            return next(([p] for p in proposals if p['proposal'] == proposal), [])
        return proposals

    def getProposalType(self, proposal):
        """Determine proposaltype of a given proposalstring."""
        if proposal in ('template', 'current'):
            raise UsageError(
                self,
                'The proposal names "template" and "current"'
                ' are reserved and cannot be used',
            )
        # check for defines service 'proposal'
        if proposal == self.serviceexp:
            return 'service'

        if self._canQueryProposals():
            allowed = [p['proposal'] for p in self._queryProposals()]
            if proposal in allowed:
                return 'user'
            # not user office propsal
            if session.checkUserLevel(ADMIN):
                return 'other'
            raise UsageError(self, 'You are not allowed to start this experiment!')
        else:
            if session.checkUserLevel(USER):
                return 'user'
            raise UsageError(self, 'You are not allowed to start experiment!')

    @usermethod
    def new(self, proposal, title=None, localcontact=None, user=None, **kwds):
        self.log.debug('Starting mgml exp')
        super().new(proposal, title, localcontact, user, **kwds)
        self._setROParam('started', time())

    @usermethod
    def finish(self):
        """Submit data to the user dashboard"""

        try:
            userInfo = session.getExecutingUser()[2]
        except Exception:
            self.log.warning('oAuth token missing for current user.', exc=1)
            super().finish()
            return

        if userInfo:
            dashboard = OAuth2Session(userInfo['clientid'], token=userInfo['token'])
            uset = []
            for k, v in self.consumed.items():
                uset.append({'resource': k, 'amount': v})
            postdata = {
                'start': datetime.fromtimestamp(self.started).strftime(
                    '%Y-%m-%dT%H:%M:%S.%f'
                ),
                'end': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f'),
                'instrument': 3,  # TODO
                'localcontact': self.propinfo['localcontacts'][0]['id'],
                # 'creator': session.getExecutingUser().name,
                'proposal': self.proposal,
                'usage_set': uset,
            }
            self.log.debug(postdata)
            response = dashboard.post(
                self.dashboardurl + '/rest/createlog/', json=postdata
            )
            self.log.debug(response.text)
        super().finish()


class HeliumExperiment(Experiment):
    """User experiment at the MGML with tracking of Helium consumption."""

    attached_devices = {
        'cryostat': Attach('Where to get the helium level', Cryostat),
    }

    _heliumlevelstart = 0

    def _setStartLevel(self):
        self._heliumlevelstart = self._attached_cryostat.read(0)

    def _addConsumedHelium(self):
        c = (
            self._attached_cryostat._level2l(self._heliumlevelstart)
            - self._attached_cryostat._level2l()
        )
        c *= self._attached_cryostat.lastcoeff
        if isnan(c):
            self.log.info('Cant add nan consumed helium.')
            c = 0
        if c < 0:
            self.log.info('Cant add negative consumed helium.')
            c = 0
        printinfo(f'[Experiment] Adding {c:.2f}l to the experiment He consumption.')
        consumedDict = dict(self.consumed)
        if 'helium' in consumedDict:
            consumedDict['helium'] += c
        else:
            consumedDict['helium'] = c
        self._setROParam('consumed', consumedDict)
        self._setStartLevel()

    @usermethod
    def new(self, proposal, title=None, localcontact=None, user=None, **kwds):
        self.log.debug('Starting he exp')
        super().new(proposal, title, localcontact, user, **kwds)
        self._setROParam('consumed', {'helium': 0.0})
        self._setStartLevel()

    @usermethod
    def finish(self):
        self._addConsumedHelium()
        super().finish()
