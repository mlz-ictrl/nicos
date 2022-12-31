#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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

from nicos_mlz.reseda.devices.armcontrol import ArmController
from nicos_mlz.reseda.devices.astrium import SelectorLambda, \
    SelectorLambdaSpread
from nicos_mlz.reseda.devices.cbox import CBoxResonanceFrequency
from nicos_mlz.reseda.devices.experiment import Experiment
from nicos_mlz.reseda.devices.regulator import Regulator
from nicos_mlz.reseda.devices.rte1104 import RTE1104, \
    RTE1104TimescaleSetting, RTE1104YScaleSetting
from nicos_mlz.reseda.devices.scandet import ScanningDetector
from nicos_mlz.reseda.devices.tuning import EchoTime
