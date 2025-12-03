# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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

from nicos import session

from nicos_sinq.camea.commands import printToDiscord
from nicos_sinq.devices.experiment import SinqExperiment


class CameaExperiment(SinqExperiment):
    """Special doFinish method for CAMEA"""

    def doFinish(self):
        SinqExperiment.doFinish(self)
        text = '''This message marks the end of your CAMEA experiment. We hope you
        had a transcendent experience with us and hope to welcome you again for
        another experiment. \n We appreciate your feedback on DUO, and please
        cite RSI 94, 023302 (2023) and Software X 12, 100600 (2020) when
        publishing CAMEA data'''
        printToDiscord(text)
        session.log.info(text)
