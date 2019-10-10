#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2019 by the NICOS contributors (see AUTHORS)
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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""VTREFF mirror sample device."""

from __future__ import absolute_import, division, print_function

import random

from nicos.core import Param, dictof, floatrange
from nicos.core.constants import MASTER

from nicos_mlz.treff.devices import MirrorSample as BaseMirrorSample


class MirrorSample(BaseMirrorSample):

    _misalignments = {}

    parameters = {
        'alignerrors': Param('Errors to simulate the sample misalignment',
                             type=dictof(str, floatrange(0)),
                             settable=False, userparam=False,
                             default={
                                 'sample_y': 2,
                                 'omega': 0.1,
                                 'detarm': 0.2,
                                 'chi': 1,
                             },),
    }

    def doInit(self, mode):
        if mode == MASTER:
            self._misalign()

    def _applyParams(self, number, parameters):
        BaseMirrorSample._applyParams(self, number, parameters)
        self._misalign()

    def _misalign(self):
        for n, err in self.alignerrors.items():
            self._misalignments[n] = random.uniform(-err, err)
