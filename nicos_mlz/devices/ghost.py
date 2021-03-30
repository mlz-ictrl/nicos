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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""NICOS FRM II specific authentication and proposal DB utilities
using the new GhOST proposal database.
"""

from datetime import date, datetime, time, timedelta

import ghostapi.errors
import ghostapi.rest

from nicos import session
from nicos.core import USER, Param, User, dictof, nonemptystring
from nicos.services.daemon.auth import AuthenticationError, \
    Authenticator as BaseAuthenticator
from nicos.services.daemon.auth.params import UserLevelAuthEntry

DTFORMAT = '%Y-%m-%d %H:%M:%S'


class GhostWrapper(ghostapi.rest.GhostRestAPI):
    """Wraps the GhOST REST client to provide the queries we need for NICOS."""

    is_local_contact = False

    def login(self, instr, email, password, strict):
        """Log in to GhOST with the given account (email address).

        If strict is true, and the current experiment is a "user experiment",
        the user must either be a local contact for the instrument or a user
        assigned to the experiment.
        """
        self.ghost_instrument = instr
        # first, login to GhOST
        error = None
        try:
            self.checkCredentials(email, password)
        except ghostapi.errors.GhostApiException as err:
            # this avoids leaking authentication details via tracebacks
            error = str(err)
        if error:
            raise AuthenticationError('login failed: %s' % error)

        # check local contact status
        try:
            instrs = self.getLCInstruments(email)
            self.is_local_contact = any(i['name'] == instr for i in instrs)
        except ghostapi.errors.GhostApiException:
            # no access means: we are not local contact
            pass
        self.log.debug('user is local contact? %s', self.is_local_contact)
        # we are a normal user => if configured, check that a proposal
        # is scheduled for us today
        if not self.is_local_contact and strict:
            self.strictUserCheck(email)
        # get user's real name for display in daemon
        userdata = self.getUserData(email)
        return userdata['firstname'] + ' ' + userdata['lastname']

    def strictUserCheck(self, email):
        """Check if user may log in considering the current proposal:

        * during user experiments, any user of that proposal may log in
        * during service/other, any user may log in whose experiment is
          scheduled for the current date

        Raises AuthenticationError if access denied.
        """
        sessions = self.getTodaysSessions()
        if session.experiment.proptype == 'user':
            if not any(ses['proposal_number'] == session.experiment.proposal
                       for ses in sessions):
                raise AuthenticationError('user is neither local contact '
                                          'nor member of current proposal')
        elif not sessions:
            raise AuthenticationError('user is neither local contact '
                                      'nor has a proposal scheduled today')

    def keepalive(self):
        """Called every now and then to refresh our session timeout."""
        self.isAuthenticated()

    def isLocalContact(self):
        """Check if current user is local contact."""
        return self.is_local_contact

    def getTodaysSessions(self):
        today = datetime.combine(date.today(), time.min)
        delta = timedelta(days=1)
        sessions = self.getExpSessionsForInstrument(self.ghost_instrument,
                                                    today, today + delta)
        return [ses for ses in sessions if ses['number']]

    def canStartProposal(self, proposal):
        """Check if current user may start this proposal."""
        if self.is_local_contact:
            return True
        try:
            return any(ses['proposal_number'] == proposal
                       for ses in self.getTodaysSessions())
        except Exception:
            session.log.warning('error querying proposals', exc=1)
            return False

    def queryProposals(self, proposal=None):
        """Query info about the experiments that this user can start.

        If *proposal* is None, looks for all proposals with experimental
        sessions planned today.  If *proposal* is given, only this proposal is
        queried for experimental sessions.

        If no matching proposal is found, nothing is returned.
        """
        result = []
        sessions = []
        try:
            sessions = self.getTodaysSessions()
        except Exception:
            if not self.is_local_contact:
                session.log.warning("error querying today's sessions from GhOST",
                                exc=1)
                return []
        if proposal is not None:
            sessions = [ses for ses in sessions
                        if ses['proposal_number'] == proposal]
        if not sessions and proposal and self.is_local_contact:
            session.log.debug('querying all exps for proposal %r', proposal)
            try:
                sessions = self.getExperimentsForProposal(proposal)
            except Exception:
                session.log.warning('error querying sessions for proposal '
                                    'from GhOST', exc=1)
                return []
        for ses in sessions:
            session.log.debug('candidate session: %r', ses)
            if ses['number'] is None:
                # experiment is not scheduled/permitted
                continue
            try:
                res = self.queryExperiment(ses['number'])
            except Exception:
                session.log.warning("error querying session %s", ses['number'],
                                    exc=1)
            else:
                result.append(res)

        return result

    def queryExperiment(self, sessid):
        """Query info about a single experiment and return it in the format
        NICOS needs for the propinfo dict.
        """
        sessinfo = self.getExperiment(sessid, details=True)
        samples = self.getSessionSamples(sessid)
        session.log.debug('session data: %r', sessinfo)
        session.log.debug('sample data: %r', samples)

        info = {}
        info['proposal'] = sessinfo['proposal']
        info['session'] = sessinfo['number']
        info['title'] = sessinfo['title']
        info['cycle'] = sessinfo['reactorcycle']
        info['instrument'] = sessinfo['instrument']
        info['startdate'] = datetime.strptime(sessinfo['start'], DTFORMAT)
        info['enddate'] = datetime.strptime(sessinfo['end'], DTFORMAT)
        if samples['basesamples']:
            info['default_sample'] = samples['basesamples'][0]['substance']
        info['users'] = []
        for user in sessinfo['userdetails']['sessionteam']:
            info['users'].append({
                'name': user['name'],
                'email': user['email'],
                'affiliation': user['affilation'],
            })
        info['localcontacts'] = [{
            'name': sessinfo['localcontact'],
            'email': sessinfo['localcontact_email'],
        }]
        info['samples'] = samples['registeredsamples']
        info['data_emails'] = [user['email'] for user in info['users']]
        info['notif_emails'] = [user['email'] for user in info['users']] + \
            [c['email'] for c in info['localcontacts']]
        return info


class Authenticator(BaseAuthenticator):
    """Authenticates against the GhOST REST API.

    The resulting user object carries around the GhOST wrapper object as
    metadata, so that further queries can be made with it while the user
    is logged in.
    """

    parameters = {
        'ghosthost':  Param('Host of the GhOST system to authenticate against',
                            type=nonemptystring, mandatory=True),
        'instrument': Param('Name of the instrument in GhOST', type=str),
        'checkexp':   Param('If true, check that users are either affiliated '
                            'with the current experiment, or registered '
                            'local contacts for the instrument', type=bool,
                            default=True),
        'aliases':    Param('Map of short user names to GhOST email addresses '
                            'and their desired user level',
                            type=dictof(nonemptystring, UserLevelAuthEntry)),
    }

    def authenticate(self, username, password):
        if username in self.aliases:
            email, level = self.aliases[username]
        else:
            email, level = username, USER
        ghost = GhostWrapper('https://' + self.ghosthost, self.log)
        try:
            realname = ghost.login(self.instrument, email, password,
                                   strict=self.checkexp)
        except ghostapi.errors.GhostAccessError:
            self.log.exception('during authentication')
            raise AuthenticationError('unknown user or wrong password') \
                from None
        except AuthenticationError:
            self.log.exception('during authentication')
            raise
        except Exception as err:
            self.log.exception('during authentication')
            raise AuthenticationError('exception during authenticate(): %s'
                                      % err) from None
        if email == username:
            # try to extract the user's real name from the user data
            username = realname
        return User(username, level, {'ghost': ghost,
                                      'keepalive': ghost.keepalive})
