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
from nicos_sinq.amor.devices.component_handler import ComponentLaserDistance
from nicos_sinq.amor.devices.hm_config import AmorTofArray


@usercommand
@helparglist('[components]')
def CalculateComponentDistances(components=None):
    """Routine to calculate the distances of various components in AMOR.
    The laser is moved to the height of a component and the distance is
    then measured. The distance read from the laser is changed for that
    component.

    NOTE: The distance devices for each components start with *d*, such
    as dsample, danalyzer and so on..

    Example:

    Following command calculates distances for all the components
    >>> CalculateComponentDistances()

    Following command calculates the distances for specified components
    >>> CalculateComponentDistances(['danalyzer', 'dsample'])
    """

    # Initialize the components list
    if not components:
        components = ['ddetector', 'danalyzer', 'dslit4', 'dsample', 'dslit3',
                      'dslit2', 'dpolarizer']

    # Get the motor to move the laser
    try:
        motor = session.getDevice('xlz')
    except ConfigurationError:
        session.log.error('The motor <xlz> that moves the laser pointer not '
                          'found. Cannot proceed.')
        return

    # Get the laser measurement device
    try:
        dimetix = session.getDevice('dimetix')
        if not dimetix.isSwitchedOn:
            session.log.info('Switching on the laser measurement device..')
            dimetix.switchOn()
    except ConfigurationError:
        session.log.error('The laser measurement device not found. Cannot '
                          'proceed')
        return

    for component in components:
        session.log.info('Calculating distance for component: %s..', component)
        try:
            # Get the device
            dev = session.getDevice(component)
            if not isinstance(dev, ComponentLaserDistance):
                session.log.error('The provided component is not valid!')
                continue

            # Check if the component has mirror height configured
            if dev.mirrorheight > 999:
                session.log.error('The mirror height for this component is not'
                                  'configured.')
                continue

            # Move the laser motor to correct position
            motor.maw(dev.mirrorheight)
            if motor.read(0) - dev.mirrorheight > motor.precision:
                session.log.error('Was not able to move the laser to target')
                continue

            # Read in and change the distance measured by laser
            position = dimetix.read(0)
            if position > 8000:
                # A position > 8000 means the component is not attached
                dev.active = False
                session.log.info('Component not active')
            else:
                dev.active = True
                dev.readvalue = position
                session.log.info('Read value = %f', position)

        except ConfigurationError:
            session.log.error('Was not able to find the component')


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
