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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#
# *****************************************************************************

from __future__ import absolute_import, division, print_function

from nicos import session
from nicos.core import Attach, Param, dictof, listof, status, usermethod
from nicos.core.device import Moveable, Readable
from nicos.core.errors import ConfigurationError
from nicos.devices.generic.sequence import BaseSequencer, SeqCall, SeqDev, \
    SeqSleep
from nicos.pycompat import number_types
from nicos.utils import printTable

from nicos_sinq.amor.devices.sps_switch import SpsSwitch


class DistancesHandler(BaseSequencer):
    """
    AMOR component handling module. These distances along the optical bench
    are measured with the dimetix laser distance measurement device.
    To this purpose each component has a little mirror attached to it,
    at a different height for each component. The dimetix is sitting
    on a translation that can be moved up and down and thus can measure
    the distance of a given component by selecting the appropriate height.

    The calculation of distance for each component involves following
    properties:

     - Known offset of the attached mirror to the actual component
     - Offset in the calculation of the distance (occurs when laser is not at 0)
     - Value read from the laser

    The actual value is then given with the following equation:

     S = d - S' - ls

    where d is scale offset, S' is the value read by laser and ls is the
    known offset.
    """

    valuetype = list

    parameters = {
        'components': Param('Components mapped to tuple of their offsets '
                            '(mark_offset, scale_offset)',
                            type=dictof(str, tuple), userparam=False),
        'fixedcomponents': Param('Fixed components mapped to their distances',
                                 type=dictof(str, float)),
        'rawdistances': Param('Calculated distances of components',
                              type=dictof(str, float), userparam=False,
                              settable=True),
        'order': Param('Order of componenets for display/mesaurment',
                       type=listof(str), userparam=False)
    }

    attached_devices = {
        'switch': Attach('Switch to turn laser on/off', SpsSwitch),
        'positioner': Attach('Positions laser to measure various components',
                             Moveable),
        'dimetix': Attach('Measures and returns the distance', Readable)
    }

    def __call__(self, components=None):
        # Print the distances of specified components from
        # Laser, Sample and Chopper
        if not components:
            components = self._components()
        sample = getattr(self, 'sample', None)
        chopper = getattr(self, 'chopper', None)
        table = []
        self.log.info('Horizontal distances of components:')
        for component in components:
            distance = getattr(self, component, None)
            row = [component]
            if isinstance(distance, number_types):
                if isinstance(sample, number_types):
                    row.append(str(sample - distance))
                else:
                    row.append('-')
                if isinstance(chopper, number_types):
                    row.append(str(chopper - distance))
                else:
                    row.append('-')
                table.append(row)
        printTable(['Component', 'From SAMPLE', 'From CHOPPER'],
                   table, self.log.info, rjust=True)

    def doInit(self, mode):
        self._update()

    def _update(self):
        unknown = []
        inactive_loaded = []
        for component in self._components():
            self._update_component(component)
            val = getattr(self, component)
            if val == 'UNKNOWN':
                unknown.append(component)
            elif val == 'NOT ACTIVE' and component in session.loaded_setups:
                inactive_loaded.append(component)

        if unknown:
            self.log.warning('Distances for following components unknown:')
            self.log.warning('** ' + ', '.join(unknown))
            self.log.warning(' ')

        if inactive_loaded:
            self.log.warning('Following components are inactive but loaded in '
                             'setups:')
            self.log.warning('** ' + ', '.join(inactive_loaded))
            self.log.warning('Do one of the following:')
            self.log.warning('Unload these setups OR Run: %s.mesaure() to '
                             'redo distances!' % self.name)

    def doInfo(self):
        ret = []
        for component in self._components():
            ret.append((component, getattr(self, component),
                        str(getattr(self, component)), 'mm', 'general'))
        return ret

    def doRead(self, maxage=0):
        return ''

    def doStatus(self, maxage=0):
        if self._seq_is_running():
            return status.BUSY, 'Measuring'
        return status.OK, ''

    def doIsAtTarget(self, pos):
        return True

    def _update_component(self, component, printValues=False):
        if component in self.fixedcomponents:
            self.__dict__[component] = self.fixedcomponents.get(component)
            if printValues:
                self._logvalues([component, "", getattr(self, component),
                                 "FIXED"])
            return

        if component in self.components:
            raw = self.rawdistances.get(component)
            if raw is None:
                self.__dict__[component] = 'UNKNOWN'
                if printValues:
                    self._logvalues([component, "", "", "UNKNOWN"])
                return

            if raw > 8000:
                self.__dict__[component] = 'NOT ACTIVE'
                if printValues:
                    self._logvalues([component, raw, "", "NOT ACTIVE"])
                return

            offsets = self.components[component]
            if not isinstance(offsets, tuple):
                offsets = tuple(offsets)
            scaleoffset = offsets[1] if len(offsets) > 1 else 0.0
            markoffset = offsets[0]
            self.__dict__[component] = abs(scaleoffset - raw - markoffset)
            if printValues:
                self._logvalues([component, raw, getattr(self, component), ""])

    def _logvalues(self, values, isheader=False):
        if isheader:
            values = ['{0: <13}'.format(val) for val in values]
            printTable(values, [], self.log.info)
        else:
            values = ['{0: >13}'.format(val) for val in values]
            printTable([], [values], self.log.info)

    def _components(self):
        # Return the ordered list of components
        components = self.components.keys() + self.fixedcomponents.keys()

        # Add the missing components in the order dict
        ordered = self.order
        for comp in components:
            if comp not in ordered:
                ordered.append(comp)

        return sorted(components, key=ordered.index)

    def _update_raw_distance(self, component):
        distances = {}
        if self.rawdistances:
            distances.update(self.rawdistances)

        # Get the value from cox
        try:
            cox = session.getDevice('cox')
        except ConfigurationError:
            coxval = 0.0
        else:
            coxval = cox.read(0)

        distances[component] = self._attached_dimetix.read(0) + coxval
        self.rawdistances = distances

    def _generateSequence(self, target):
        if not target:
            target = self._components()

        # Add everything to be done in the seq list
        seq = []

        # If the laser is now on, turn it on
        if self._attached_switch.read(0) != 'ON':
            seq.append(SeqDev(self._attached_switch, 'ON'))
            seq.append(SeqSleep(5))

        seq.append(SeqCall(self._logvalues,
                           ['Component', 'Read', 'Final', 'Comments'],
                           True))

        for component in target:
            if component not in self._components():
                comments = 'Skipping! Component not valid..'
                seq.append(SeqCall(self._logvalues, [component, '', '',
                                                     comments]))
                continue

            if component in self.fixedcomponents:
                comments = 'Skipping! Component fixed..'
                seq.append(SeqCall(self._logvalues, [component, '', '',
                                                     comments]))
                continue

            if component not in self._attached_positioner.mapping:
                comments = 'Skipping! Height not configured..'
                seq.append(SeqCall(self._logvalues, [component, '', '',
                                                     comments]))
                continue

            # Move the laser to the component height
            seq.append(SeqDev(self._attached_positioner, component))

            # Sleep for few seconds before reading the value
            seq.append(SeqSleep(3))

            # Read in and change the distance measured by laser
            seq.append(SeqCall(self._update_raw_distance, component))
            seq.append(SeqCall(self._update_component, component, True))

        seq.append(SeqCall(self.log.info, 'Parking and turning off laser..'))
        seq.append(SeqDev(self._attached_positioner, 'park'))
        seq.append(SeqDev(self._attached_switch, 'OFF'))
        seq.append(SeqCall(self.log.info, 'Done! Summary below:'))
        seq.append(SeqCall(self.__call__, target))
        seq.append(SeqCall(self._update))

        return seq

    # User Methods
    @usermethod
    def measure(self, components=None):
        """Routine to calculate the distances of various components in AMOR.
        The laser is moved to the height of a component and the distance is
        then measured.

        NOTE: The following components are allowed:
        analyzer, detector, polarizer, filter, sample, slit1, slit2, slit3,
        slit4, selene

        Example:

        Following command calculates distances for all the components
        >>> CalculateComponentDistances()

        Following command calculates the distances for specified components
        >>> CalculateComponentDistances(['analyzer', 'sample'])
        """
        if components is None:
            components = []
        self.maw(components)
