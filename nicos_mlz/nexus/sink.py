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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""MLZ specific NeXus sink."""

from nicos.core.params import Param, dictof, listof, nicosdev, oneof
from nicos.nexus.nexussink import NexusSink
from nicos.utils import importString


class Sink(NexusSink):
    """MLZ specific NeXus file sink with environment setting."""

    parameters = {
        'env_mapping': Param('Define devices for different sample environments',
                             type=dictof(oneof('temp_env',
                                               'magnet_env',
                                               'stress_env',
                                               'efield_env',),
                                         listof(nicosdev)),
                             default={
                                'temp_env': ['T', 'Ts', ],
                                'magnet_env': ['B'],
                                'stress_env': ['teload', 'tepos', 'teext', ],
                                'efield_env': [],
                             },
                             ),
    }

    def loadTemplate(self):
        tp = importString(self.templateclass)()
        tp.init(**(self.device_mapping | self.env_mapping))
        return tp.getTemplate()
