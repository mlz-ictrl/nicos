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
#   Matt Clarke <matt.clarke@ess.eu>
#
# *****************************************************************************

"""ESS Experiment device."""

import os
import time

from yuos_query.exceptions import BaseYuosException
from yuos_query.yuos_client import YuosClient

from nicos.core import Override, Param
from nicos.devices.experiment import Experiment
from nicos.utils import createThread


class EssExperiment(Experiment):
    parameters = {
        'server_url': Param('URL of the proposal system',
            type=str, category='experiment', mandatory=True,
        ),
        'instrument': Param('The instrument name in the proposal system',
            type=str, category='experiment', mandatory=True,
        ),
        'cache_filepath': Param('Path to the proposal cache',
            type=str, category='experiment', mandatory=True,
        ),
        'update_interval': Param('Time interval (in hrs.) for cache updates',
            default=1.0, type=float)
    }

    parameter_overrides = {
        'propprefix': Override(default=''),
        'serviceexp': Override(default='Service'),
        'sendmail': Override(default=False),
        'zipdata': Override(default=False),
    }

    def doInit(self, mode):
        Experiment.doInit(self, mode)
        self._client = None
        self._update_cache_worker = createThread(
            'update_cache', self._update_cache, start=False)
        # Get secret from the environment
        token = os.environ.get('YUOS_TOKEN')
        if token:
            try:
                self._client = YuosClient(
                    self.server_url, token, self.instrument, self.cache_filepath)
                self._update_cache_worker.start()
            except BaseYuosException as error:
                self.log.warn(f'QueryDB not available: {error}')

    def _canQueryProposals(self):
        if self._client:
            return True

    def _update_cache(self):
        while True:
            # Client instantiation updates the cache. Thus wait before updating
            time.sleep(self.update_interval * 3600)
            self._client.update_cache()

    def _queryProposals(self, proposal=None, kwds=None):
        if not proposal:
            raise RuntimeError('Please enter a valid proposal ID')

        query_result = self._do_query(proposal)
        if not query_result:
            raise RuntimeError(f'could not find proposal {proposal}')
        result = {
            'proposal': str(query_result.id),
            'title': query_result.title,
            'users': self._extract_users(query_result),
            'localcontacts': [],
            'samples': self._extract_samples(query_result),
            'dataemails': [],
            'notif_emails': [],
            'errors': [],
            'warnings': [],
        }

        return [result]

    def _do_query(self, proposal):
        try:
            return self._client.proposal_by_id(proposal)
        except BaseYuosException as error:
            self.log.error(f'{error}')
            raise

    def _extract_samples(self, query_result):
        samples = []
        for sample in query_result.samples:
            samples.append({
                'name': sample.name,
                'formula': sample.formula,
                'number of': sample.number,
                'mass/volume':
                    f'{sample.mass_or_volume[0]} {sample.mass_or_volume[1]}'.strip(),
                'density': f'{sample.density[0]} {sample.density[1]}'.strip(),
            })
        return samples

    def _extract_users(self, query_result):
        users = []
        for first, last in query_result.users:
            users.append(
                {
                    'name': f'{first} {last}',
                    'email': '',
                    'affiliation': '',
                }
            )
        if query_result.proposer:
            first, last = query_result.proposer
            users.append(
                {
                    'name': f'{first} {last}',
                    'email': '',
                    'affiliation': '',
                }
            )
        return users
