#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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
#   Lydia Fleischhauer-Fuss <l.fleischhauer-fuss@fz-juelich.de>
#   Alexander Steffens <a.steffens@fz-juelich.de>
#
# *****************************************************************************

"""NICOS sample device with support of IFF sample database."""

from __future__ import absolute_import, division, print_function

from requests import post

from nicos import session
from nicos.utils.credentials.keystore import nicoskeystore

from nicos_mlz.devices.sample import Sample as MLZSample

DUMMY_SAMPLE_ID = 218  # 498
# TODO: check if IDs are the same in the actual sample DB
MEASUREMENT_ACTION_ID = {
    'fourcircle': 32,
    'galaxi': 25,
}
NICOS_USER_ID = 45
GETPUT_REQUEST_OK = 200
POST_REQUEST_OK = 201


class Sample(MLZSample):
    """Sample device that validates the given sample ID in the IFF sample
    database before setting the parameter.
    """

    def doWriteSampleid(self, value):
        new_id = DUMMY_SAMPLE_ID
        # check whether given ID belongs to a sample by trying to add a
        # measurement entry to the sample database
        if value is not None and 'ldap_id' in session.getExecutingUser().data:
            bot = session.experiment.sampledb_botname
            r = post(
                session.experiment.sampledb_url + 'objects/',
                auth=(bot, nicoskeystore.getCredential(bot, 'iffsampledb')),
                json={
                    'action_id': MEASUREMENT_ACTION_ID[
                        session.instrument.name.lower()],
                    'data': {'sample': {'_type': 'sample', 'object_id': value}}
                }
            )
            if r.status_code != POST_REQUEST_OK:
                session.log.error(
                    'validating sample ID failed (invalid credentials for bot '
                    'user %r specified in the NICOS keystore?): %s', bot,
                    r.text,
                )
            elif '(at sample)' in r.json()['message']:
                session.log.warning('given ID (%d) does not represent a '
                                    'sample', value)
            else:
                new_id = value
        return new_id
