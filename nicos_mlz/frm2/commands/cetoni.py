# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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
#   Konstantin Kholostov <k.kholostov@fz-juelich.de>
#
# *****************************************************************************

"""User commands for high pressure stopped flow experiment."""


from nicos import session
from nicos.commands import helparglist, usercommand
from nicos.commands.measure import count
from nicos.protocols.daemon import BREAK_AFTER_STEP


@usercommand
@helparglist('')
def cetoni_calibrate_sensors():
    """Calculates and stores offsets to atmospheric pressure for pressure
    sensors installed on cetoni pumps.
    """
    pump1 = session.getDevice('pump1')
    pump2 = session.getDevice('pump2')
    pump3 = session.getDevice('pump3')

    pump1.set_valve_state('pass_through')
    pump2.set_valve_state('pass_through')
    pump3.set_valve_state('pass_through')

    value1 = pump1._pressure.read_weighted()[0]
    value2 = pump2._pressure.read_weighted()[0]
    value3 = pump3._pressure.read_weighted()[0]

    pump1._pressure.doAdjust(value1, 1.01325)
    pump2._pressure.doAdjust(value2, 1.01325)
    pump3._pressure.doAdjust(value3, 1.01325)


@usercommand
@helparglist('pressure, volume1, volume2, time, [detectors], [presets]')
def cetoni_count(pressure, volume1, volume2, time, *detlist, **preset):
    """Performs mixing of liquids of *volume1* and *volume2* that are stored in
    pump 1 and pump 2. Mixing happens in the pressure cell under specified
    pressure. Corresponding valves are switched automatically. Pump 3 moves
    accordingly to maintain the specified pressure.

    Example:

    >>> cetoni_count(30, 1, 1, 10)
    >>> cetoni_count(30, 1, 1, 10, t=10)
    >>> cetoni_count(30, 1, 1, 10, psd, t=10)

    At first pumps 1 and 2 will be discharged and charged again to the maximum
    fill level. Pump 3 will be discharged too, but filled enough to create
    specified pressure in the pressure cell with background liquid.
    PID algorithm is used in order to stabilize the pressure values. Once
    pressure values are reached, pumps 1 and 2 start to discharge liquids in
    the pressure cell, while pump 3 sucks the liquids out of the pressure cell.
    Pump 3 moves at a rate that allows to maintain specified pressure. Once
    the movement is complete, PID controller is engaged to maintain the
    pressure in the cell during the experiment.

    """
    pump1 = session.getDevice('pump1')
    pump2 = session.getDevice('pump2')
    pump3 = session.getDevice('pump3')

    pump1.set_valve_state('inlet')
    pump2.set_valve_state('inlet')
    pump3.set_valve_state('inlet')

    pump1.speed = pump1._max_speed
    pump1.doStart(0)
    pump2.speed = pump2._max_speed
    pump2.doStart(0)
    pump3.speed = pump3._max_speed
    pump3.doStart(0)
    pump1._hw_wait()
    pump2._hw_wait()
    pump3._hw_wait()
    pump1.speed = pump1._max_speed
    pump1.doStart(25)
    pump2.speed = pump2._max_speed
    pump2.doStart(25)
    pump3.speed = pump3._max_speed
    pump3.doStart(3)
    pump1._hw_wait()
    pump2._hw_wait()
    pump3._hw_wait()
    session.log.info('Liquids have been refreshed.\n'
                     'Setting the pressure values.')

    pump1.set_valve_state('closed')
    pump2.set_valve_state('closed')
    pump3.set_valve_state('outlet')

    pump1.keep_pressure(pressure)
    pump2.keep_pressure(pressure)
    pump3.keep_pressure(pressure)
    while 1:
        try:
            session.breakpoint(BREAK_AFTER_STEP)
        except BaseException:
            pump1.stop_pid()
            pump2.stop_pid()
            pump3.stop_pid()
            break
        if pump1.pid_ready and pump2.pid_ready and pump3.pid_ready:
            session.log.info('Pressure values have been reached.')
            pump1.stop_pid()
            pump2.stop_pid()
            pump3.stop_pid()
            break
        session.delay(1)

    pump1.set_valve_state('outlet')
    pump2.set_valve_state('outlet')
    pump3.set_valve_state('outlet')

    pump3.suck_from_cell(volume1 + volume2, time)
    pump1.dispense_to_cell(volume1, time)
    pump2.dispense_to_cell(volume2, time)
    pump1._hw_wait()
    pump2._hw_wait()
    pump3._hw_wait()
    pump1.set_valve_state('closed')
    pump2.set_valve_state('closed')

    session.log.info('Mixing is finished. Starting the detector.\n'
                     'Keeping pressure in pump3.')
    pump3._x = [i + volume1 + volume2 for i in pump3._x]
    pump3.keep_pressure(pressure, rewrite_xy=False)
    try:
        result = count(*detlist, **preset)
    finally:
        pump3.stop_pid()
    return result
