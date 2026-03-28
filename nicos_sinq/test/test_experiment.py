# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-present by the NICOS contributors (see AUTHORS)
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
#   Alexander Söderqvist <alexander.soederqvist@psi.ch>
#
# *****************************************************************************
import pytest

from nicos.core.errors import InvalidValueError
from unittest import mock
session_setup = 'experiment'

# pylint: disable=line-too-long
prop1 =  {'beamline': 'TEST', 'proposal': '20265353', 'title': 'calibration', 'firstname': 'Peter', 'lastname': 'Mueller', 'email': 'peter.mueller@web.test', 'account': 'pmueller', 'affiliation': {'id': 19301, 'name': 'Paul Scherrer Institute PSI', 'department': 'Lab. for Neutron Scattering and Imaging (LNS)', 'country': 'Switzerland', 'address': ['Forschungsstrasse 111', '5232 Villigen PSI']}, 'pi_firstname': 'Peter', 'pi_lastname': 'Mueller', 'pi_email': 'peter.muellerr@psi.ch', 'pi_account': 'pmueller', 'pi_affiliation': {'id': 19301, 'name': 'Paul Scherrer Institute PSI', 'department': 'Lab. for Neutron Scattering and Imaging (LNS)', 'country': 'Switzerland', 'address': ['Forschungsstrasse 111', '5232 Villigen PSI']}, 'eaccount': '', 'pgroup': 'p217347', 'abstract': '', 'schedule': [{'id': 2228364, 'start': '04/03/2026', 'end': '05/03/2026'}], 'proposal_submitted': '09/02/2026', 'proposal_expire': '21/02/2026', 'proposal_status': 'Finished', 'delta_last_schedule': 1, 'mainproposal': '', 'proposal_type': 'Instrument Development', 'authors': [{'relations': ['pi', 'proposer'], 'author': {'userid': 4570, 'title': 'Dr.', 'firstname': 'Peter', 'lastname': 'Mueller', 'phone': '+41-xxxxxxxxxx', 'email': 'peter.mueller@psi.ch', 'umbrella': False, 'affilation': {'id': 19301, 'name': 'Paul Scherrer Institute PSI', 'department': 'Lab. for Neutron Scattering and Imaging (LNS)', 'country': 'Switzerland', 'address': ['Forschungsstrasse 111', '5232 Villigen PSI']}, 'adaccount': {'username': 'pmueller', 'status': 'Active', 'expire': '1601-01-01'}}}]}

propprop = {
   "beamline": "TEST-Legacy",
   "proposal": "20260338",
   "type": "Proprietary"
}

class MockHttpResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data

class TestExperiment:
    devname = 'Exp'

    @pytest.fixture(autouse=True)
    def initialize_device(self, session):
        self.exp = session.getDevice(self.devname)
        self.exp._getDuoapikey = mock.Mock()
        self.exp._getDuoapikey.return_value = 'lorem-ipsum'
        session.current_sysconfig['experiment'] = self.devname

    @pytest.mark.parametrize("num, dinfo", [("20265353", prop1), ("20260338", propprop)])
    def test_prop_allowed(self, num, dinfo):
        with mock.patch('requests.get', return_value=MockHttpResponse(dinfo, 200)):
            duoinfo = self.exp._requestDuoProposal(num)
            assert duoinfo == dinfo
            errstr = self.exp._proposalIsAllowed(duoinfo)
            assert errstr is None

    @pytest.mark.parametrize("num, prop", [(20265353, prop1), (20260338, propprop)])
    def test_query(self, num, prop):
        with mock.patch('requests.get', return_value=MockHttpResponse(prop, 200)):
            ret = self.exp._queryProposals(proposal=num)
            assert ret[0].get('errors', None) is None

    def test_checkNewInvalid(self):
        with pytest.raises(InvalidValueError):
            self.exp._newCheckHook(proptype=None, proposal="2026553")

    def test_new(self):
        with mock.patch('requests.get', return_value=MockHttpResponse(prop1, 200)):
            self.exp.new(proposal="20265353")
