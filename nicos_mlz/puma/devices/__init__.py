#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2022 by the NICOS contributors (see AUTHORS)
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

from nicos_mlz.puma.devices.attenuator import Attenuator
from nicos_mlz.puma.devices.collimator import Collimator
from nicos_mlz.puma.devices.comb_ax import CombAxis
from nicos_mlz.puma.devices.coupledaxis import PumaCoupledAxis
from nicos_mlz.puma.devices.datasinks import PolarizationFileSink
from nicos_mlz.puma.devices.deflector import Deflector
from nicos_mlz.puma.devices.filter import PumaFilter
from nicos_mlz.puma.devices.focus import FocusAxis
from nicos_mlz.puma.devices.hecell import HeCellLifter
from nicos_mlz.puma.devices.ipc import Coder, Motor, Motor1, ReferenceMotor
from nicos_mlz.puma.devices.kineticdetector import KineticDetector
from nicos_mlz.puma.devices.maglock import MagLock
from nicos_mlz.puma.devices.mchanger import Mchanger
from nicos_mlz.puma.devices.mtt import MttAxis
from nicos_mlz.puma.devices.multianalyzer import PumaMultiAnalyzer
from nicos_mlz.puma.devices.multidetector import PumaMultiDetectorLayout
from nicos_mlz.puma.devices.pgfilter import PGFilter
from nicos_mlz.puma.devices.seccoll import PumaSecCollBlockChanger, \
    PumaSecCollLift, PumaSecCollPair, PumaSecondaryCollimator
from nicos_mlz.puma.devices.senseswitch import SenseSwitch
from nicos_mlz.puma.devices.sh_cylinder import SH_Cylinder
from nicos_mlz.puma.devices.spectro import PUMA
from nicos_mlz.puma.devices.sr7 import SR7Shutter
from nicos_mlz.puma.devices.stackedaxis import StackedAxis
from nicos_mlz.puma.devices.tango import CycleCounter
from nicos_mlz.puma.devices.virtual import VirtualDigitalInput, \
    VirtualDigitalOutput, VirtualLogoFeedback, VirtualReferenceMotor
