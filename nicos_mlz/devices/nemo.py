# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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
#   Björn Pedersen <bjoern.pedersen@frm2.tum.de>
#
# *****************************************************************************
"""NICOS FRM II specific authentication and proposal DB utilities
using the new NEMO scheduling system
"""

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from nemoapi.connector import NemoConnector

from nicos import session
from nicos.core import USER, Param, User, dictof, nonemptystring
from nicos.services.daemon.auth import AuthenticationError, \
    Authenticator as BaseAuthenticator
from nicos.services.daemon.auth.params import UserPassLevelAuthEntry

DTFORMAT = '%Y-%m-%d %H:%M:%S'


def NemoAliasEntry(val=None):
    """Provide a 2 or 3-tuple of user and level and local contact status

        * user: string
        * level: oneof(ACCESS_LEVELS)
           currently: GUEST, USER, ADMIN
        * localcontactstatus: bool
    """
    if val is not None and (not isinstance(val, tuple) or  len(val) not in [2, 3]):
        raise ValueError('NemoAliasEntry entry needs to be a 2/3-tuple '
                         '(name, accesslevel, isLocalContact(optional))')
    # pylint: disable=unbalanced-tuple-unpacking
    localcontactstatus = bool(val[2]) if len(val) == 3 else False
    user, _p, level = UserPassLevelAuthEntry((val[0], '', val[1]))
    return tuple((user, level, localcontactstatus))


class NemoWrapper(NemoConnector):
    """Wraps the NEMO REST client to provide the queries we need for NICOS."""

    is_local_contact = False

    def __init__(self, nemourl, log, is_lc=False):
        NemoConnector.__init__(self, base_url=nemourl, token=None)
        self.log = log
        self.is_local_contact = is_lc

    def login(self, instr, username, password, strict):
        """Log in to NEMO with the given account (email address).

        If strict is true, and the current experiment is a "user experiment",
        the user must either be a local contact for the instrument or a user
        assigned to the experiment.
        """
        self.nemo_instrument = instr
        # first, login to NEMO
        error = None
        try:
            res = self.authenticate({
                'username': username,
                'password': password
            })
            if not res:
                error = 'NEMO: Authentication failed:%r' % res
        except Exception as err:
            # this avoids leaking authentication details via tracebacks
            error = 'NEMO: ' + str(err)
        if error:
            raise AuthenticationError('login failed: %s' % error)

        # TODO: check local contact status
        # self.is_local_contact = ????
        self.log.debug('user is local contact? %s', self.is_local_contact)
        # we are a normal user => if configured, check that a proposal
        # is scheduled for us today
        if not self.is_local_contact and strict:
            self.strictUserCheck(username)
        # get user's real name for display in daemon
        userdata = self.getUserData(username)
        return userdata['firstname'] + ' ' + userdata['lastname']

    def getUserData(self, username):

        try:
            data = self.get_users_by_username(username)[0]
        except Exception as e:
            self.log.error('%r', e)
            return {
                'firstname': 'first_name',
                'lastname': 'last_name',
            }

        userdata = {
            'firstname': data['first_name'],
            'lastname': data['last_name'],
            'username': data['username'],
            'email': data['email'],
        }
        return userdata

    def strictUserCheck(self, email):
        """Check if user may log in considering the current proposal:

        * during user experiments, any user of that proposal may log in
        * during service/other, any user may log in whose experiment is
          scheduled for the current date

        Raises AuthenticationError if access denied.
        """
        sessions = self.getTodaysSessions()
        if session.experiment.proptype == 'user':
            if not any(ses['id'] == session.experiment.proposal
                       for ses in sessions):
                raise AuthenticationError(
                    'user is neither local contact nor member of current proposal'
                )
        elif not sessions:
            raise AuthenticationError(
                'user is neither local contact nor has a proposal scheduled today'
            )

    def keepalive(self):
        """Called every now and then to refresh our session timeout.

        kept for api compat with ghost, but as the token does not expire not needed.
        """

    def isLocalContact(self):
        """Check if current user is local contact."""
        return self.is_local_contact

    def getTodaysSessions(self):
        tz = ZoneInfo(
            'Europe/Berlin')  # make it configurable if used outside MLZ
        today = datetime.combine(date.today(), time.min, tz)
        delta = timedelta(days=1)

        # filter all reservations where start is < today+1 day
        # (so starting on or before the current day)
        # and end is > today (so ending today or later)
        sessions = self.get_reservations(tool_id=self.nemo_instrument,
                                         dt_start_before=today + delta,
                                         dt_end_after=today)
        return sessions

    def canStartProposal(self, proposal):
        """Check if current user may start this proposal."""
        if self.is_local_contact:
            return True
        try:
            return any(ses['id'] == proposal
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
                session.log.warning(
                    "error querying today's sessions from NEMO", exc=1)
                return []
        if proposal is not None:
            sessions = [ses for ses in sessions if ses['id'] == int(proposal)]
        for ses in sessions:
            try:
                res = self.queryExperiment(ses['id'], sessions)
            except Exception:
                session.log.warning('error querying session %s',
                                    ses['id'],
                                    exc=1)
            else:
                result.append(res)

        return result

    def queryExperiment(self, sessid, sessions=None):
        """Query info about a single experiment and return it in the format
        NICOS needs for the propinfo dict.
        """
        if sessions is None:
            sessions = self.getTodaysSessions()
        sessinfo = [s for s in self.getTodaysSessions()
                    if s['id'] == sessid][0]
        self.log.info('session data: %r', sessinfo)

        info = {}
        info['proposal'] = str(sessinfo['id'])
        info['session'] = str(sessinfo['id'])
        info['title'] = sessinfo['title']
        info['cycle'] = ''
        info['instrument'] = sessinfo['tool']['name']
        info['startdate'] = datetime.fromisoformat(sessinfo['start'])
        info['enddate'] = datetime.fromisoformat(sessinfo['end'])
        qd = sessinfo.get('question_data')
        if qd and qd.get('si_sampleinfo'):
            info['default_sample'] = qd.get('si_sampleinfo').get(
                'user_input', 'unset')

        # note: NEMO only has a single user per session
        info['users'] = []
        user = sessinfo.get('user')
        info['users'].append({
            'name': f'{user["first_name"]} {user["last_name"]}',
            'email': user['email'],
            'affiliation': user.get('domain', 'external'),
        })
        # we don't get local contacts
        info['localcontacts'] = []
        # no detailed sample info currently
        info['samples'] = []
        info['data_emails'] = [
            user['email'],
        ]
        info['notif_emails'] = [
            user['email'],
        ]
        return info


class Authenticator(BaseAuthenticator):
    """Authenticates against the NEMO REST API.

    The resulting user object carries around the NEMO wrapper object as
    metadata, so that further queries can be made with it while the user
    is logged in.
    """

    parameters = {
        'nemourl':
        Param(
            'URL of NEMO system to authenticate against',
            type=nonemptystring,
            mandatory=True,
        ),
        'instrument':
        Param('ID of the instrument in  NEMO', type=int),
        'checkexp':
        Param(
            'If true, check that users are either affiliated '
            'with the current experiment, or registered '
            'local contacts for the instrument',
            type=bool,
            default=True,
        ),
        'aliases':
        Param(
            'Map of short user names to NEMO usernames'
            ' and their desired user level and local contact status',
            type=dictof(nonemptystring, NemoAliasEntry),
        ),
    }

    def authenticate(self, username, password):
        if username in self.aliases:
            username, level, is_lc = self.aliases[username]
        else:
            level, is_lc = USER, False
        nemo = NemoWrapper(self.nemourl, self.log, is_lc)
        try:
            realname = nemo.login(self.instrument,
                                  username,
                                  password,
                                  strict=self.checkexp)
        except AuthenticationError:
            self.log.exception('during authentication')
            raise
        except Exception as err:
            self.log.exception('during authentication')
            raise AuthenticationError('exception during authenticate(): %s' %
                                      err) from None
        return User(realname, level, {
            'proposal_system': nemo,
            'keepalive': nemo.keepalive
        })
