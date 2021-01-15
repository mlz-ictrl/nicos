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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#
# *****************************************************************************

from nicos import session
from nicos.core.errors import NicosError

from nicos_ess.nexus import DeviceStream
from nicos_ess.nexus.elements import KafkaStream, NXAttribute, NXDataset, \
    NXGroup, NXLink
from nicos_ess.nexus.placeholder import DeviceValuePlaceholder


class NexusTemplateConverter:
    """Converts the provided nexus template. Creates and populates the entry
    groups from nexus template and then creates and returns the nexus
    structure from those entry groups.
    """

    def convert(self, template, metainfo):
        """ Convert the provided template with the given devices that
        should be tracked during the run.
        :param template: Template dictionary
        :param metainfo: meta information of devices from dataset
        """
        if not isinstance(template, dict):
            raise NicosError('The template should be of type dict!')

        # Generate the basic neXus hierarchy
        root_name, root_value = self._populate('root:NXroot', template)

        if not isinstance(root_value, NXGroup):
            return {}

        structure = root_value.structure(root_name, metainfo)[0]

        # Need only children and attributes in the top
        return {
            "children": structure.get("children"),
            "attributes": structure.get("attributes"),
        }

    def _populate(self, element, value):
        if isinstance(value, NXGroup):
            return element, value

        # Group keys are named as <name>:<nxclass>
        if ':' not in element:
            session.log.info('Can\'t write the group %s, no nxclass defined!',
                             element)
            return element, None

        [nxname, nxclass] = element.rsplit(':', 1)
        group = NXGroup(nxclass)

        if isinstance(value, dict):
            # Populate rest of the elements
            for key, val in value.items():
                if isinstance(val, dict):
                    # This is another group
                    child_nxname, child_value = self._populate(key, val)
                    if isinstance(child_value, NXGroup):
                        group.children.update({child_nxname: child_value})
                elif isinstance(val, (NXGroup, NXLink, KafkaStream)):
                    group.children[key] = val
                elif isinstance(val, NXDataset):
                    # Check if the this dataset should rather be tracked
                    # and should appear as NXlog
                    tracked = session.experiment.envlist
                    if isinstance(val.value, DeviceValuePlaceholder):
                        if val.value.device in tracked:
                            stream = DeviceStream(val.value.device,
                                                  val.value.parameter)
                            stream.stream_attrs = val.attrs
                            group.children[key] = stream
                            continue
                    group.children[key] = val
                elif isinstance(val, NXAttribute):
                    group.attrs[key] = val
                else:
                    group.attrs[key] = NXAttribute(val)

        return nxname, group
