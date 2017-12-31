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

"""Test configuration file containing fixtures for individual tests."""

test_devices = {
    'sinq_motor': ['com', 'coz', 'aom', 'd1b'],
    'sinq_magnet': ['pby'],
    'sinq_counter': ['psd_tof'],
}


def pytest_addoption(parser):
    parser.addoption("--sinq", action="store_true",
                     help="run tests for devices in SINQ facility")
    parser.addoption("--device", action="append", default=[],
                     help="restrict device to be tested (multiple allowed)")


def pytest_generate_tests(metafunc):
    sinq_movable = []
    sinq_motor = []
    sinq_counter = []
    devices = []
    for devs in test_devices.values():
        devices += devs

    if metafunc.config.getoption('sinq', default=False):
        devices_to_test = devices
        if metafunc.config.getoption('device'):
            devices_to_test = metafunc.config.getoption('device')

        for dev in devices_to_test:
            if dev in devices:
                if dev in test_devices['sinq_motor']:
                    sinq_movable.append(dev)
                    sinq_motor.append(dev)
                elif dev in test_devices['sinq_magnet']:
                    sinq_movable.append(dev)
                elif dev in test_devices['sinq_counter']:
                    sinq_counter.append(dev)
            else:
                print('WARNING: ' + dev + ' not found in testable devices')

    if 'sinq_motor' in metafunc.fixturenames:
        metafunc.parametrize('sinq_motor', sinq_motor)

    if 'sinq_movable' in metafunc.fixturenames:
        metafunc.parametrize('sinq_movable', sinq_movable)

    if 'sinq_counter' in metafunc.fixturenames:
        metafunc.parametrize('sinq_counter', sinq_counter)
