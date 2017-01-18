#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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
"""STRESS-SPEC specific commands for the robot to change the sample."""

from nicos import session
from nicos.commands import usercommand, helparglist
from nicos.commands.basic import sleep


@usercommand
@helparglist('')
def gauge_to_base():
    session.getDevice('phis').speed = 50
    session.getDevice('xt').speed = 40
    dev_pos = [('robt', 13),

               ('zt', -400), ('robj3', -1), ('robj1', -1), ('robj2', -2),
               ('robj3', -110),

               ('zt', 140), ('chis', 190), ('robb', -2), ('phis', 10),
               ('yt', 610), ('xt', -515)]

    for dev, pos in dev_pos:
        session.log.info('Move %s to %f', dev, pos)
        session.getDevice(dev).maw(pos)
        sleep(5)


@usercommand
@helparglist('toolnumber')
def base_to_gauge(tool):
    session.getDevice('phis').speed = 50
    session.getDevice('xt').speed = 40
    # omgr in robot software offset must be <= -10
    dev_pos = [('zt', -200), ('robj3', -1), ('robj1', -70), ('robj3', -100),
               ('xt', 0),
               ]
    for dev, pos in dev_pos:
        session.log.info('Move %s to %f', dev, pos)
        session.getDevice(dev).maw(pos)
        sleep(5)

    # select tool (gauge volume)
    session.getDevice('robt').maw(tool)
    sleep(5)

    # move to gauge center
    dev = 'chis'
    pos = 180.
    session.log.info('Move %s to %f', dev, pos)
    session.getDevice(dev).maw(pos)
    sleep(5)
    pos = 0
    for dev in ['robb', 'phis', 'zt', 'xt', 'yt']:
        session.log.info('Move %s to %f', dev, pos)
        session.getDevice(dev).maw(pos)
        sleep(5)


@usercommand
@helparglist('samplenumber')
def set_sample(sample):
    session.getDevice('robs').maw(int(sample))
