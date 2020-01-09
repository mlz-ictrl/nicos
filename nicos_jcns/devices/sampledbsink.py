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

"""IFF sample database sink and its handler."""

from __future__ import absolute_import, division, print_function

from base64 import b64encode
from os import path
from re import compile as re_compile
from time import localtime, strftime

from requests import post, put

from nicos import session
from nicos.core.constants import POINT
from nicos.core.data.sink import DataSink as BaseDataSink, \
    DataSinkHandler as BaseDataSinkHandler
from nicos.utils.credentials.keystore import nicoskeystore

from nicos_jcns.devices.sample import DUMMY_SAMPLE_ID, GETPUT_REQUEST_OK, \
    MEASUREMENT_ACTION_ID, NICOS_USER_ID, POST_REQUEST_OK

# match file names that end with '.dat' (typically created by ascii file sink)
DAT_FILE_REGEX = re_compile(r'^.*\.dat$')


class DataSinkHandler(BaseDataSinkHandler):
    """Sink handler that creates a new 'measurement' entry for every scan with
    its metadata in the IFF sample database.

    In case the NICOS scan was started by a non-ldap user (e.g. guest) and no
    valid ID was set, the metadata will **not** be stored in the database as it
    will be assumed that it was not intended to do so.
    """

    def __init__(self, sink, dataset, detector):
        BaseDataSinkHandler.__init__(self, sink, dataset, detector)
        bot = session.experiment.sampledb_botname
        self._bot_auth = (bot, nicoskeystore.getCredential(bot, 'iffsampledb'))
        self._measurement_id = None
        self._user_id = NICOS_USER_ID

    def addSubset(self, point):
        self._user_id = session.getExecutingUser().data.get('ldap_id',
                                                            NICOS_USER_ID)
        if point.settype != POINT or point.number != 1:
            return
        sample_id = session.experiment.sample.sampleid
        if self._user_id == NICOS_USER_ID and sample_id == DUMMY_SAMPLE_ID:
            # if both IDs were not set, it will be assumed that the measurement
            # was not intended to be stored in the database
            return
        r = post(
            session.experiment.sampledb_url + 'objects/',
            auth=self._bot_auth,
            json={
                'action_id': MEASUREMENT_ACTION_ID[
                    session.instrument.name.lower()],
                'data': {
                    'name': {
                        'text': '{}-{:d}'.format(
                            session.instrument.name.upper(),
                            self.dataset.counter
                        ),
                        '_type': 'text',
                    },
                    'proposal_name': {
                        'text': session.experiment.proposal,
                        '_type': 'text',
                    },
                    'sample': {
                        '_type': 'sample',
                        'object_id': sample_id,
                    },
                    'created': {
                        '_type': 'datetime',
                        'utc_datetime': strftime(
                            '%Y-%m-%d %H:%M:%S',
                            localtime(self.dataset.started)
                        ),
                    },
                    'detector_z': {
                        '_type': 'quantity',
                        'magnitude_in_base_units': float(
                            session.getDevice('detz').read()) / 1000,
                        'dimensionality': '[length]',
                        'units': 'mm',
                    },
                    'sample_detector_distance': {
                        '_type': 'quantity',
                        'magnitude_in_base_units': float(
                            session.getDevice('detdistance').read()) / 1000,
                        'dimensionality': '[length]',
                        'units': 'mm',
                    },
                },
            },
        )
        if r.status_code != POST_REQUEST_OK:
            self._measurement_id = None
            session.log.error(
                'storing metadata of scan #%d in IFF sample database failed: '
                '%s', self.dataset.counter, r.text,
            )
        else:
            try:
                self._measurement_id = int(r.headers['Location'].split('/')[7])
            except ValueError:
                self.log.error('measurement ID could not be determined from '
                               '"%s"', r.headers['Location'])
            if self._user_id == NICOS_USER_ID:
                session.log.warning(
                    'you were logged in as an anonymous user: please ask an '
                    'instrument responsible how to view and set the correct '
                    'permissions for your measurement with the IFF sample '
                    'database ID %d', self._measurement_id
                )
            else:
                r = put(
                    '{}objects/{}/permissions/users/{}'.format(
                        session.experiment.sampledb_url, self._measurement_id,
                        self._user_id,
                    ), auth=self._bot_auth, json='grant',
                )
                if r.status_code != GETPUT_REQUEST_OK:
                    session.log.error(
                        'setting "grant" permission to user "%s" for scan #%d '
                        'failed: %s', session.getExecutingUser().name,
                        self.dataset.counter, r.text,
                    )
            if sample_id == DUMMY_SAMPLE_ID:
                session.log.warning(
                    'no valid sample ID was defined for the measurement with '
                    'IFF sample database ID %d: please change it manually '
                    'using the web interface', self._measurement_id
                )

    def end(self):
        if self._measurement_id is not None:
            meta_file = path.join(
                session.experiment.datapath,
                filter(DAT_FILE_REGEX.match, self.dataset.filenames)[0],
            )
            with open(meta_file, 'rb') as mf:
                r = post(
                    '{}objects/{}/files/'.format(
                        session.experiment.sampledb_url, self._measurement_id),
                    auth=self._bot_auth, allow_redirects=False,
                    json={
                        'storage': 'local',
                        'original_file_name': self.dataset.filenames[0],
                        'base64_content': b64encode(mf.read()).decode('utf8'),
                    },
                )
                if r.status_code != POST_REQUEST_OK:
                    session.log.error(
                        'uploading "%s" to IFF sample database failed: %s',
                        self.dataset.filenames[0], r.text,
                    )
        self._measurement_id = None


class DataSink(BaseDataSink):
    """Data sink that uses the IFF sample database sink handler.
    """

    handlerclass = DataSinkHandler
