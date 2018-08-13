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

"""AMOR specific commands and routines"""

from nicos import session
from nicos.commands import usercommand, helparglist
from nicos.core.errors import ConfigurationError
from nicos.utils import printTable
from nicos_sinq.amor.devices.component_handler import ComponentLaserDistance
from nicos_sinq.amor.devices.hm_config import AmorTofArray


@usercommand
@helparglist('[components]')
def CalculateComponentDistances(components=None):
    """Routine to calculate the distances of various components in AMOR.
    The laser is moved to the height of a component and the distance is
    then measured. The distance read from the laser is changed for that
    component.

    NOTE: The following components are allowed:
    analyzer, detector, polarizer, filter, sample, slit1, slit2, slit3, slit4

    Example:

    Following command calculates distances for all the components
    >>> CalculateComponentDistances()

    Following command calculates distances for one component
    >>> CalculateComponentDistances('slit4')

    Following command calculates the distances for specified components
    >>> CalculateComponentDistances(['analyzer', 'sample'])
    """

    # Initialize the components list
    if not components:
        components = ['detector', 'analyzer', 'slit4', 'sample', 'slit3',
                      'slit2', 'polarizer', 'slit1', 'filter', 'selene']

    if not isinstance(components, list):
        components = [components]

    # cox motor should be at 0 during the calculations.
    try:
        cox = session.getDevice('cox')
        coxval = cox.read(0)
        cox.maw(0)
    except ConfigurationError:
        cox = None
        coxval = None

    # Check if the required devices are present
    devs = {}
    for d in ['laser_switch', 'laser_positioner', 'dimetix']:
        try:
            devs[d] = session.getDevice(d)
        except ConfigurationError:
            session.log.error('Device %s not found. Cannot proceed.', d)
            return

    # Switch ON the laser
    devs['laser_switch'].maw('ON')

    def logvalues(values, isheader=False):
        if isheader:
            values = ['{0: <11}'.format(val) for val in values]
            printTable(values, [], session.log.info)
        else:
            values = ['{0: >11}'.format(val) for val in values]
            printTable([], [values], session.log.info)

    logvalues(['Component', 'Read Value', 'Final Value', 'Comments'], True)
    for component in components:
        session.breakpoint(2)  # Allow break and continue here
        comments = ''
        try:
            # Get the device
            dev = session.getDevice('d' + component)
            if not isinstance(dev, ComponentLaserDistance):
                logvalues([component, "", "",
                           'Skipping! Provided component not valid..'])
                continue

            # Check if the component has mirror height configured
            if (component not in devs['laser_positioner'].mapping
                    or devs['laser_positioner'].mapping[component] > 999):
                comments = 'Using old value as height not configured..'
                position = dev.readvalue
            else:
                devs['laser_positioner'].maw(component)
                # Sleep for few seconds before reading the value
                session.delay(5)
                # Read in and change the distance measured by laser
                position = devs['dimetix'].read(0)

                if position > 8000:
                    # A position > 8000 means the component is not attached
                    dev.active = False
                    comments = 'NOT ACTIVE'
                else:
                    dev.active = True
                    dev.readvalue = position
            logvalues([component, position, dev.read(0), comments])
        except ConfigurationError:
            logvalues([component, "", "",
                       'Skipping! Was not able to find the component..'])

    # Finally, bring the devices back to their initial/park positions
    if cox:
        cox.maw(coxval)
    if 'park' in devs['laser_positioner'].mapping:
        devs['laser_positioner'].maw('park')
    # Switch OFF the laser
    devs['laser_switch'].maw('OFF')
    session.log.info('Finished. Parked and turned off laser.')


@usercommand
@helparglist('scheme, [value]')
def UpdateTimeBinning(scheme, value=None):
    """Changes the time binning for histogramming the data
    Time binning schemes:
        c/q/t <argument>
        c means Delta q / q = constant = <argument>
        q means Delta q = constant, <argument> is the number of bins/channels
        qq assumes two spectra per pulse
        t means Delta t = constant, <argument> is the number of bins/channels

    Example:

    Following command uses the scheme c with resolution of 0.005
    >>> UpdateTimeBinning('c', 0.005)

    Following command uses the scheme q with 250 channels
    >>> UpdateTimeBinning('q', 250)

    """
    # Get the configurator device
    try:
        configurator = session.getDevice('hm_configurator')
        for arr in configurator.arrays:
            if isinstance(arr, AmorTofArray):
                arr.applyBinScheme(scheme, value)
        configurator.updateConfig()
    except ConfigurationError:
        session.log.error('The configurator device not found. Cannot proceed')
