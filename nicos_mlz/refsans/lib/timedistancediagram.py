#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2019 by the NICOS contributors (see AUTHORS)
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
#   Matthias Pomm <matthias.pomm@hzg.de>
#
# *****************************************************************************
"""Chopper related devices."""

from __future__ import absolute_import, division, print_function

import numpy as np

from nicos_mlz.refsans.lib.calculations import chopper_pos, d_SC2, SC1_Pos


def timedistancediagram(rpm, angles, disk2_pos=5, SC2_mode='default',
                        SC2_full_open=240, D=22.8, n_per=2, title_prefix='',
                        plot=None):
    """Draw a time-distance diagram for the chopper.

    input:
       rpm    : the running speed  (rounds per min)
       angles : the angles for d1 to d6 as returned by chopper_config ([deg])
       d_MCo  : dist from disk1 to the opening disk for the master (d2) (m)
       d_SCo  : dist from disk1 to the opening disk for the SC1 (m)
       d_SCc  : dist from disk1 to the closing disk for the SC1 (m)
       d_SC2  : distance from disk1 to SC2 (should not change...) (m)
       D      : beamline length (distance disk1 - detector !!NOT flightpath)(m)
       n_per  : the number of periods to display (int)

    """
    plot.clear()
    # if d_MCo == d_SCo:
    #    raise ValueError('Disk2 and 3 collide !')
    # ++ Param hack todo ###

    # --
    d_MCo = chopper_pos[disk2_pos]
    d_SCo = chopper_pos[SC1_Pos]
    d_SCc = chopper_pos[SC1_Pos]

    per = 60. / rpm if rpm else 1e10
    freq = 1. / per

    resolution = d_MCo / (D - d_MCo / 2.)

    angles = np.array(angles, dtype=float)
    trailing_edge_MC = (0 + 240) / (360 * freq)
    trailing_edge_SC = (0 + 240) / (360 * freq)
    trailing_edge_SC2 = (360 - SC2_full_open) / (360 * freq)
    # print(trailing_edge_SC2)

    if np.all(angles[-2:] == [None, None]):
        angles = angles[:-2]

    times = angles / (360 * freq)

    # period limits
    for i in range(n_per + 1):
        plot.vlines(i * per, 0, D, 'b', ':', lw=2)

    # beams
    t = np.linspace(-times[2], n_per * per)

    # wl_0 first
    # a hack to describe infinitely fast neutrons
    tof = np.array([times[0], times[3]])
    if tof[1] == 0:
        tof[1] = 1e-9
    pos = np.array([0, d_SCc])

    # f0 = p.polyfit(tof, pos, 1) flake8 assigned but never used
    # beam0 = p.polyval(f0, t) flake8 assigned but never used

    # wl_0 last
    tof = np.array([times[0], times[2]])
    # a hack to describe infinitelly fast neutrons
    if tof[1] == 0:
        tof[1] = 1e-9
    pos = np.array([0, d_SCc])
    # f = p.polyfit(tof, pos, 1) flake8 assigned but never used
    # beam1 = p.polyval(f, t) flake8 assigned but never used

    # wl_min
    if SC2_mode is not None:
        tof = np.array([times[0], times[5]])
        pos = np.array([0, d_SC2])
    else:
        tof = np.array([times[0], times[3]])
        pos = np.array([0, d_SCc])
    if tof[1] == 0:
        tof[1] = 1e-9
    f1 = np.polyfit(tof, pos, 1)
    beam2 = np.polyval(f1, t)
    # f1 = fit_lin(tof, pos)
    # beam2 = f1[0] * t +f1[1]
    detection = [1e3 * (D - f1[1]) / f1[0]]

    # wl_max
    if SC2_mode is not None:
        tof = np.array([times[1], times[4]])
        pos = np.array([d_MCo, d_SC2])
    else:
        tof = np.array([times[1], times[2]])
        pos = np.array([d_MCo, d_SCo])
    if tof[1] == 0:
        tof[1] = 1e-9
    f2 = np.polyfit(tof, pos, 1)
    beam3 = np.polyval(f2, t)
    # f2 = fit_lin(tof, pos)
    # beam3 = f2[0] * t +f2[1]

    detection.append(1e3 * (D - f2[1]) / f2[0])

    detection = np.array(detection)

    for i in range(-1, n_per + 1):
        ip = i * per
        # disk1: black line
        plot.hlines(0, ip, ip + trailing_edge_MC, lw=5)
        # disk2: blue line
        plot.hlines(d_MCo, times[1] - trailing_edge_SC2 + ip, times[1] + ip,
                    'b', lw=3)
        # disk3: green line
        plot.hlines(d_SCc, times[2] + ip, times[2] + trailing_edge_SC + ip,
                    'g', lw=3)
        # disk4: red line
        plot.hlines(d_SCo, times[3] - trailing_edge_SC + ip, times[3] + ip,
                    'r', lw=3)
        try:
            # disk5: green line
            plot.hlines(d_SC2 + 0.05, times[4] + ip,
                        times[4] + ip + trailing_edge_SC2, 'g', lw=3)
            # disk6: red line
            plot.hlines(d_SC2, times[5] + ip - trailing_edge_SC2,
                        times[5] + ip, 'r', lw=3)
        except IndexError:
            # means we have no SC2!
            pass

        # detector
        plot.hlines(D, *plot.get_xlim(), colors='#FFFF00', lw=4)

        # plot.plot(t + ip, beam0, 'g')
        # plot.plot(t + ip, beam1, 'g')
        plot.plot(t + ip, beam2, 'b')
        plot.plot(t + ip, beam3, 'r')

    plot.set_xlim(0, (n_per + .2) * per)
    plot.set_ylim(0, D * 1.1)

    detect_st = 'First n.: '
    for el in detection:
        detect_st += '%s ' % round(el, 1)
        elcorr = np.mod(el, per * 1000)

        if elcorr != el:
            detect_st += '(%s ms)' % round(elcorr, 1)

        detect_st += ' , Last n. : '
    detect_st = detect_st[:-10]

    title = '%s Angles : %s (deg) at %d rpm\n%s\nResolution %.1f (%%)' % (
        title_prefix, angles.round(2), int(rpm), detect_st, resolution * 100.)

    plot.set_title(title, fontsize='x-small')
    plot.set_xlabel('Time since start signal (s)')
    plot.set_ylabel('Distance from chopper 1 (m)')
