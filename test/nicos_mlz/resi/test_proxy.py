#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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
#   Björn Pedersen <bjoern.pedersen@frm2.tum.de>
#
# *****************************************************************************

from __future__ import print_function

import pytest

from nicos.pycompat import cPickle as pickle
from nicos_mlz.resi.devices import residevice


@pytest.mark.skipif(residevice.position is None,
                    reason='RESI specific Nonius libs not present')
def test_pickable():
    store = {'phi': 3.1415926535897931, 'type': 'e', 'dx': 400, 'chi': 0.0,
             'theta': -0.17453292519943295, 'omega': 0.0}
    hw = None
    pos = residevice.position.PositionFromStorage(hw, store)
    proxied = residevice.ResiPositionProxy(pos)
    res = pickle.dumps(proxied, protocol=0)
    restored = pickle.loads(res)
    print(store)
    print(restored.storable())
    assert restored.storable() == store
