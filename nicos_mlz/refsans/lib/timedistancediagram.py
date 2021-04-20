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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#   Matthias Pomm <matthias.pomm@hzg.de>
#   Gaetano Mangiapia <gaetano.mangiapia@hzg.de>
#
# *****************************************************************************
"""Chopper related devices."""

import numpy as np

from nicos_mlz.refsans.lib.calculations import SC1_Pos, chopper_pos, d_SC2


def timedistancediagram(speed, angles, disk2_pos, D,
                        SC2_full_open=240, n_per=2,
                        disk2_mode='normal_mode',
                        plot=None,
                        Actual_D=None):

    """Draw a time-distance diagram for the chopper for Monitor 01

    input:
    :param speed: disc running speed  (rounds per min)
    :param angles: Real angles, from disk1 to disk6, in a list, in degrees.
                   If SC2 is not used, last two angles have to be set to None.
    :param disk2_pos: the real disk 2 position (from 1 to 5)
    :param D: last beamline length (disk1 - detector distance, in meters) set
              in chopper_config
    :param SC_full_open: ???
    :param n_per: the number of periods to display (int)
    :param disk2_mode: the disk2 mode. oneof('normal_mode',
                                             'virtual_disc2_pos_6')
    :param plot: matplotlib plot object, on which the plot has to be shown
    :param Actual_D: actual beamline length, in meters
    """

    plot.clear()

    # Background color as from NICOS Monitor
    plot.set_facecolor('#F0F0F0')
    plot.figure.patch.set_color('#F0F0F0')

    # if d_MCo == d_SCo:
    #    raise ValueError('Disk2 and 3 collide !')
    # ++ Param hack todo ###

    # distance from disk1 to the opening disk for the master (d2) (m)
    d_MCo = chopper_pos[disk2_pos]
    # distance from disk1 to the opening disk for the SC1 (m)
    d_SCo = chopper_pos[SC1_Pos]
    # distance from disk1 to the closing disk for the SC1 (m)
    d_SCc = chopper_pos[SC1_Pos]

    per = 60000.0 / speed if speed else 1e13  # in ms
    freq = 1.0 / per  # in kHz

    angles = np.array(angles, dtype=float)
    trailing_edge_MC = (0 + 240) / (360 * freq)  # in ms
    trailing_edge_SC = (0 + 240) / (360 * freq)  # in ms
    trailing_edge_SC2 = (360 - SC2_full_open) / (360 * freq)  # in ms
    # print(trailing_edge_SC2)

    # if SC2 is not present limit the angles to 4 values
    if np.all(angles[-2:] == [None, None]):
        angles = angles[:-2]

    times = angles / (360 * freq)  # in ms

    # period limits
    for i in range(n_per + 1):
        plot.vlines(i * per, 0, D, 'b', ':', lw=2)  # in ms

    # beams
    t = np.linspace(-times[2], n_per * per)  # in ms

    # wl_min
    if len(angles) == 6:  # SC2 pair is used
        tof = np.array([times[0], times[5]])
        pos = np.array([0, d_SC2])
    else:  # SC2 is not used
        tof = np.array([times[0], times[3]])
        pos = np.array([0, d_SCc])

    if tof[1] == 0:
        tof[1] = 1e-6  # a hack to describe infinitely fast neutrons

    f1 = np.polyfit(tof, pos, 1)
    beam2 = np.polyval(f1, t)

    detection = [(D - f1[1]) / f1[0]]

    # wl_max
    if (disk2_mode == 'virtual_disc2_pos_6'):
        # In this case SC2 must be used. The check of disk2_mode is important
        # to prevent wrong display of wl_max
        tof = np.array([times[3], times[4]])
        pos = np.array([d_SCo, d_SC2])
    elif (disk2_mode == 'normal_mode'):
        if len(angles) == 6:  # SC2 pair is used
            tof = np.array([times[1], times[4]])
            pos = np.array([d_MCo, d_SC2])
        else:
            tof = np.array([times[1], times[2]])
            pos = np.array([d_MCo, d_SCo])

    if tof[1] == 0:
        tof[1] = 1e-6

    f2 = np.polyfit(tof, pos, 1)
    beam3 = np.polyval(f2, t)

    detection.append((D - f2[1]) / f2[0])

    detection = np.array(detection)

    for i in range(-1, n_per + 1):
        ip = i * per

        # disk1: black line
        if i == -1:
            plot.hlines(0, ip, ip + trailing_edge_MC, lw=3, label='disk 1')
        else:
            plot.hlines(0, ip, ip + trailing_edge_MC, lw=3)

        # disk2: blue line
        if i == -1:
            plot.hlines(d_MCo, times[1] - trailing_edge_SC2 + ip,
                        times[1] + ip, 'b', lw=3, label='disk 2')
        else:
            plot.hlines(d_MCo, times[1] - trailing_edge_SC2 + ip,
                        times[1] + ip, 'b', lw=3)

        # disk3: green line
        if i == -1:
            plot.hlines(d_SCc, times[2] + ip, times[2] + trailing_edge_SC + ip,
                        'g', lw=3, label='disks 3 and 5')
        else:
            plot.hlines(d_SCc, times[2] + ip, times[2] + trailing_edge_SC + ip,
                        'g', lw=3)

        # disk4: red line
        if i == -1:
            plot.hlines(d_SCo, times[3] - trailing_edge_SC + ip, times[3] + ip,
                        'r', lw=3, label='disks 4 and 6')
        else:
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

        # detector (from chopper_config)
        if i == -1:
            plot.hlines(D, *plot.get_xlim(), colors='#FFFF00', lw=4,
                        label='detector set position')
        else:
            plot.hlines(D, *plot.get_xlim(), colors='#FFFF00', lw=4)

        # detector (actual position)
        if Actual_D is not None:
            if i == -1:
                plot.hlines(Actual_D, *plot.get_xlim(), colors='#FF7F39', lw=4,
                            label='detector actual position')
            else:
                plot.hlines(Actual_D, *plot.get_xlim(), colors='#FF7F39')

        plot.plot(t + ip, beam2, 'b')
        plot.plot(t + ip, beam3, 'r')

    plot.set_xlim(0, (n_per + .2) * per)
    plot.set_ylim(0, D * 1.1)

    detect_st = 'First n.: '
    for el in detection:
        detect_st += '%s ' % round(el, 1)
        elcorr = np.mod(el, per)

        if elcorr != el:
            detect_st += '(%s ms)' % round(elcorr, 1)

        detect_st += ' , Last n. : '
    detect_st = detect_st[:-10]

    title = 'Angles : %s (deg) at %.0f speed\n%s' % (
        angles.round(2), speed, detect_st)

    plot.set_title(title, fontsize='x-small')
    plot.set_xlabel('Time since start signal / ms')
    plot.set_ylabel('Distance from master chopper / m')
    plot.legend(loc='upper center', ncol=6, borderaxespad=0.)
    if Actual_D is not None:
        # possible frame overlap. The warning is raised by using a orange frame
        # and a text on top of the plot
        if Actual_D > D:
            plot.set_facecolor('orange')
            plot.figure.suptitle(
                'POSSIBLE FRAME OVERLAP. CHECK CHOPPER SETTINGS', fontsize=16,
                fontweight='bold', color='orange')
