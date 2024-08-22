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


@usercommand
@helparglist('')
def cetoni_calibrate_sensors():
    """Calculates and stores offsets to atmospheric pressure for pressure
    sensors installed on cetoni syringes.
    """
    syringe1 = session.getDevice('syringe1')
    syringe2 = session.getDevice('syringe2')
    syringe3 = session.getDevice('syringe3')

    syringe1.set_valve_state('pass_through')
    syringe2.set_valve_state('pass_through')
    syringe3.set_valve_state('pass_through')

    value1 = syringe1._pressure.read_weighted()[0]
    value2 = syringe2._pressure.read_weighted()[0]
    value3 = syringe3._pressure.read_weighted()[0]

    syringe1._pressure.doAdjust(value1, 1.01325)
    syringe2._pressure.doAdjust(value2, 1.01325)
    syringe3._pressure.doAdjust(value3, 1.01325)


@usercommand
@helparglist('pressure, volume1, volume2, time, [detectors], [presets]')
def cetoni_count(pressure, volume1, volume2, time, *detlist, **preset):
    """Performs mixing of liquids of *volume1* and *volume2* that are stored in
    syringe1 and syringe2. Mixing happens in the pressure cell under specified
    pressure. Corresponding valves are switched automatically. syringe3 moves
    accordingly to maintain the specified pressure.

    Example:

    >>> cetoni_count(30, 1, 1, 10)
    >>> cetoni_count(30, 1, 1, 10, t=10)
    >>> cetoni_count(30, 1, 1, 10, psd, t=10)

    At first syringes 1 and 2 will be discharged and charged again to the maximum
    fill level. syringe 3 will be discharged too, but filled enough to create
    specified pressure in the pressure cell with background liquid.
    PID algorithm is used in order to stabilize the pressure values. Once
    pressure values are reached, syringes 1 and 2 start to discharge liquids in
    the pressure cell, while syringe3 sucks the liquids out of the pressure cell.
    syringe3 moves at a rate that allows to maintain specified pressure. Once
    the movement is complete, PID controller is engaged to maintain the
    pressure in the cell during the experiment.

    """
    syringe1 = session.getDevice('syringe1')
    syringe2 = session.getDevice('syringe2')
    syringe3 = session.getDevice('syringe3')

    syringe1.set_valve_state('inlet')
    syringe2.set_valve_state('inlet')
    syringe3.set_valve_state('inlet')

    syringe1.speed = syringe1._max_speed
    syringe1.doStart(0)
    syringe2.speed = syringe2._max_speed
    syringe2.doStart(0)
    syringe3.speed = syringe3._max_speed
    syringe3.doStart(0)
    syringe1._hw_wait()
    syringe2._hw_wait()
    syringe3._hw_wait()
    syringe1.speed = syringe1._max_speed
    syringe1.doStart(25)
    syringe2.speed = syringe2._max_speed
    syringe2.doStart(25)
    syringe3.speed = syringe3._max_speed
    syringe3.doStart(3)
    syringe1._hw_wait()
    syringe2._hw_wait()
    syringe3._hw_wait()
    session.log.info('Liquids have been refreshed.\n'
                     'Setting the pressure values.')

    syringe1.set_valve_state('closed')
    syringe2.set_valve_state('closed')
    syringe3.set_valve_state('outlet')

    syringe1.keep_pressure(pressure)
    syringe2.keep_pressure(pressure)
    syringe3.keep_pressure(pressure)
    while 1:
        try:
            session.breakpoint(2)
        except BaseException:
            syringe1.stop_pid()
            syringe2.stop_pid()
            syringe3.stop_pid()
            break
        if syringe1.pid_ready and syringe2.pid_ready and syringe3.pid_ready:
            session.log.info('Pressure values have been reached.')
            syringe1.stop_pid()
            syringe2.stop_pid()
            syringe3.stop_pid()
            break
        session.delay(1)

    syringe1.set_valve_state('outlet')
    syringe2.set_valve_state('outlet')
    syringe3.set_valve_state('outlet')

    syringe3.suck_from_cell(volume1 + volume2, time)
    syringe1.dispense_to_cell(volume1, time)
    syringe2.dispense_to_cell(volume2, time)
    syringe1._hw_wait()
    syringe2._hw_wait()
    syringe3._hw_wait()
    syringe1.set_valve_state('closed')
    syringe2.set_valve_state('closed')

    session.log.info('Mixing is finished. Starting the detector.\n'
                     'Keeping pressure in syringe3.')
    syringe3._x = [i + volume1 + volume2 for i in syringe3._x]
    syringe3.keep_pressure(pressure, rewrite_xy=False)
    try:
        result = count(*detlist, **preset)
    finally:
        syringe3.stop_pid()
    return result
