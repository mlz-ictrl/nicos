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
#   Stefan Mathis <stefan.mathis@psi.ch>
#
# *****************************************************************************


import pytest

from nicos.core.device import Device
from nicos.core.errors import ProgrammingError
from nicos.core.params import Override, Param

from test.utils import ErrorLogged

session_setup = 'volatile1'

class Foo(Device):
    parameters = {
        'volaposition': Param('A volatile parameter', type=int, volatile=True)
    }

    def doReadVolaposition(self):
        return 42

def test_volatile_param_given_in_setup(session):

    # Load setup 1 where no param is given in the session
    session.loadSetup('volatile1', autocreate_devices=True)
    dev1 = session.getDevice('dev1')
    assert dev1.volaposition == 42

    # Now try to load setup 2
    with pytest.raises(ErrorLogged) as exc:
        session.loadSetup('volatile2', autocreate_devices=True)
    msg = str(exc)
    assert "parameter 'volaposition' is volatile and must not be defined in " \
        'the setup file' in msg
    assert 'Configuration error' in msg

def test_ambigious_parameters(session):
    """
    Defining this class should already raise an exception.
    """

    with pytest.raises(ProgrammingError) as exc:
        class Bar(Device): # pylint: disable=unused-variable
            """
            This device has an illegal combination of parameters and cannot be created
            """
            parameters = {
                'volaposition': Param('An internal parameter', type=int,
                                      internal=True, mandatory=True)
            }

            def doReadVolaposition(self):
                return 84
    assert 'Ambiguous parameter settings detected' in str(exc)

    with pytest.raises(ProgrammingError) as exc:
        class Baz(Device): # pylint: disable=unused-variable
            """
            This device has an illegal combination of parameters and cannot be created
            """
            parameters = {
                'volaposition': Param('A volatile parameter', type=int,
                                      volatile=True, mandatory=True)
            }

            def doReadVolaposition(self):
                return 84
    assert 'Ambiguous parameter settings detected' in str(exc)

def test_override(session):

    with pytest.raises(ProgrammingError) as exc:
        class FooOverride(Foo): # pylint: disable=unused-variable

            parameter_overrides = {
                'volaposition': Override(mandatory=True),
            }
    assert 'Ambiguous parameter definition detected' in str(exc)
