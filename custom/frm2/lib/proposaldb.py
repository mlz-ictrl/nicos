#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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

"""FRM-II proposal DB utilities."""

import os
import datetime

try:
    import MySQLdb
except ImportError:
    MySQLdb = None

from nicos import session
from nicos.core import ConfigurationError, InvalidValueError
from nicos.utils import readFile


class ProposalDB(object):
    def __init__(self):
        try:
            if not session.experiment or not session.experiment.propdb:
                credentials = readFile(os.getenv('HOME') +
                                       '/.nicos/credentials')
            else:
                credentials = readFile(session.experiment.propdb)
        except IOError, e:
            raise ConfigurationError('Can\'t read credentials '
                                     'for propdb-access from file: %s' % e)
        credentials = credentials[0]
        try:
            self.user, hostdb = credentials.split('@')
            self.host, self.db = hostdb.split(':')
        except ValueError:
            raise ConfigurationError('%r is an invalid credentials string '
                                     '("user@host:dbname")' % credentials)
        if MySQLdb is None:
            raise ConfigurationError('MySQL adapter is not installed')

    def __enter__(self):
        self.conn = MySQLdb.connect(host=self.host, user=self.user, db=self.db)
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


def queryProposal(pnumber):
    """Query the FRM-II proposal database for information about the given
    proposal number.
    """
    if not isinstance(pnumber, (int, long)):
        raise InvalidValueError('proposal number must be an integer')
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
        # get user info
        cur.execute('''
            SELECT name, user_email, institute1 FROM nuke_users, Proposal
            WHERE user_id = _uid AND xid = %s''', (pnumber,))
        userrow = cur.fetchone()
    if not rows or len(rows) < 3:
        raise InvalidValueError('proposal %s does not exist in database' %
                                pnumber)
    if not userrow:
        raise InvalidValueError('user does not exist in database')
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
                raise InvalidValueError('proposal %s is not a proposal for '
                    'this instrument, but %s' % (pnumber, value[4:]))
        if value:
            info[key] = value
    return info

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
