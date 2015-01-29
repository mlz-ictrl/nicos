#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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

"""NICOS FRM II specific authentication and proposal DB utilities."""


from os import path
import datetime

try:
    import mysql.connector as DB  # pylint: disable=F0401
except ImportError:
    try:
        import MySQLdb as DB
    except ImportError:
        DB = None

from nicos import session
from nicos.core import ConfigurationError, InvalidValueError, USER, User
from nicos.utils import readFile
from nicos.pycompat import integer_types, text_type
from nicos.services.daemon.auth import AuthenticationError, \
    Authenticator as BaseAuthenticator


class ProposalDB(object):
    def __init__(self):
        try:
            if not session.experiment or not session.experiment.propdb:
                credpath = path.join(path.expanduser('~'), '.nicos',
                                     'credentials')
                credentials = readFile(credpath)
            else:
                credentials = readFile(session.experiment.propdb)
        except IOError as e:
            raise ConfigurationError('Can\'t read credentials '
                                     'for propdb-access from file: %s' % e)
        credentials = credentials[0]
        try:
            self.user, hostdb = credentials.split('@')
            self.host, self.db = hostdb.split(':')
        except ValueError:
            raise ConfigurationError('%r is an invalid credentials string '
                                     '("user@host:dbname")' % credentials)
        if DB is None:
            raise ConfigurationError('MySQL adapter is not installed')

    def __enter__(self):
        self.conn = DB.connect(host=self.host, user=self.user, db=self.db,
                               charset='utf8')
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, *exc):
        self.cursor.close()
        self.conn.close()


def queryCycle():
    """Query the FRM-II proposal database for the current cycle."""
    today = datetime.date.today()
    with ProposalDB() as cur:
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


def queryProposal(pnumber, instrument=None):
    """Query the FRM-II proposal database for information about the given
    proposal number.
    """
    if not isinstance(pnumber, integer_types):
        raise InvalidValueError('proposal number must be an integer')
    # check still needed?
    if session.instrument is None:
        raise InvalidValueError('cannot query proposals, no instrument '
                                'configured')

    with ProposalDB() as cur:
        # get proposal title and properties
        cur.execute('''
            SELECT xname, mname, value
            FROM Proposal, Proposal_members, Proposal_values
            WHERE xid = %s AND xid = _xid AND mid = _mid
            ORDER BY abs(mid-4.8) ASC''', (pnumber,))
        rows = cur.fetchall()
        # get real instrument name
        cur.execute('''
            SELECT name
            FROM Proposal, Proposal_members, Proposal_values, instruments
            WHERE xid = %s AND xid = _xid AND mid = _mid
                AND mname = '_CM_INSTRUMENT' and db_name = value
            ''', (pnumber,))
        instrname = cur.fetchone()[0]
        # get user info
        cur.execute('''
            SELECT name, user_email, institute1 FROM nuke_users, Proposal
            WHERE user_id = _uid AND xid = %s''', (pnumber,))
        userrow = cur.fetchone()
        # get security and radiation permissions
        cur.execute('''
            SELECT sec_ok, rad_ok FROM frm2_survey_comments
            WHERE _pid =  %s''', (pnumber,))
        permissions = cur.fetchone()
    if not rows or len(rows) < 3:
        raise InvalidValueError('proposal %s does not exist in database' %
                                pnumber)
    if not userrow:
        raise InvalidValueError('user does not exist in database')
    if not permissions:
        raise InvalidValueError('no permissions entry in database')
    if instrname == 'POLI-HEIDI':
        instrname = 'POLI'
    if instrument is not None and instrname.lower() != instrument.lower():
        session.log.error('proposal %s is not a proposal for '
                          '%s, but for %s, cannot use proposal information' %
                          (pnumber, instrument, instrname))
        return instrname, {'wrong_instrument': instrname}  # avoid data leakage
    # structure of returned data: (title, user, prop_name, prop_value)
    info = {
        'instrument': instrname,
        'title': rows[0][0],
        'user': userrow[0],
        'user_email': userrow[1],
        'affiliation': userrow[2],
        'permission_security': ['no', 'yes'][permissions[0]],
        'permission_radiation_protection': ['no', 'yes'][permissions[1]],
    }
    for row in rows:
        # extract the property name in a form usable as dictionary key
        key = row[1][4:].lower().replace('-', '_')
        value = row[2]
        if value and key not in info:
            info[key] = value
    # convert all values to utf-8
    for k in info:
        info[k] = text_type(info[k]).encode('utf-8')
    return info.pop('instrument', 'None'), info


def queryUser(user):
    """Query the FRM-II proposal database for the user ID and password hash."""
    with ProposalDB() as cur:
        count = cur.execute('''
            SELECT user_id, user_password FROM nuke_users WHERE username=%s
            ''', (user,))
        if count == 0:
            raise InvalidValueError('user %s does not exist in the user office '
                                    'database' % (user,))
        row = cur.fetchone()
    uid = int(row[0])
    passwd = row[1]
    return uid, passwd


class Authenticator(BaseAuthenticator):
    """
    Authenticates against the FRM-II user office database.
    """

    def pw_hashing(self):
        return 'md5'

    def authenticate(self, username, password):
        try:
            _uid, passwd = queryUser(username)
            if passwd != password:
                raise AuthenticationError('wrong password')
            return User(username, USER)
        except AuthenticationError:
            raise
        except Exception as err:
            raise AuthenticationError('exception during authenticate(): %s'
                                      % err)
