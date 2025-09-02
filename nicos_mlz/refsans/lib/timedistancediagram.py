# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
"""Code to show a time/distance diagram."""

import numpy as np

from nicos_mlz.refsans.lib.calculations import SC1_Pos, chopper_pos, d_SC2, h_m


def timedistancediagram(speed, angles, disk2_pos, D, SC2_full_open=240.,
                        n_per=2, disk2_mode='normal_mode', plot=None,
                        Actual_D=None):

    """Draw a time/distance diagram for the chopper configuration provided.
    This routine is an adaptation of the homonymous routine present in
    refsans_tools.
    In the plot, all the distances are shown in meters, whereas all the times
    in milliseconds.

    Input:

        speed :             rotation disc speed, in rounds per minute (float)
        angles :            an array with the REAL disc phases from disc 1 to
                            disc 6, in degrees. If SC2 is not used, last two
                            angles have to be set to None (float)
        disk2_pos :         the REAL position of disk2 (1-5) (int)
        D :                 distance between disc1 and detector which is set
                            in chopper_config, expressed in meters (float)
        SC2_full_open :     maximum possible aperture of SC2 pair,
                            in degrees (float)
        n_per :             number of periods (frames) which should be
                            diaplayed in the time/distance diagram (int)
        disk2_mode :        flag to specify the working mode of the chopper
                            system (str). It can be set to:
                            - 'normal_mode',          for the normal operations
                            - 'virtual_disc2_pos_6',  when the position 6 has
                                                      to be simulated

        plot :              matplotlib plot object, on which the plot has to
                            be shown
        Actual_D :          actual disc1 - detector distance, in meters
    """

    plot.clear()

    # Background color as from NICOS Monitor
    plot.set_facecolor('#F0F0F0')
    plot.figure.patch.set_color('#F0F0F0')

    # Max value for y-axis scaling
    if Actual_D is not None:
        y_max = 1.1 * max(D, Actual_D)
    else:
        y_max = 1.1 * D

    # disk1-disk2 distance (m)
    d_MCo = chopper_pos[disk2_pos]
    # disk1-disk4 (opening disk for SC1) distance (m)
    d_SCo = chopper_pos[SC1_Pos]
    # disk1-disk3 (closing disk for SC1) distance (m)
    d_SCc = chopper_pos[SC1_Pos]

    # Period and frequency
    per = 60000.0 / speed if speed else 1e13  # in ms
    freq = 1.0 / per  # in kHz

    trailing_edge_MC = (0. + 240.) / (360. * freq)  # in ms
    trailing_edge_SC = (0. + 240.) / (360. * freq)  # in ms
    trailing_edge_SC2 = (360. - SC2_full_open) / (360. * freq)  # in ms

    # if SC2 is not present limit the angles to 4 values
    if ((angles[-1] is None) and (angles[-2] is None)):
        angles = angles[:-2]

    n_angles = len(angles)  # dimension of array angles

    for i in range(2, n_angles - 1, 2):
        if angles[i] < angles[i + 1]:
            # Closing time must be greater than opening time!!
            angles[i] += 360.0

    angles = np.array(angles, dtype=float)
    times = angles / (360. * freq)  # in ms

    # draws the period limits (vertical lines splitting the frames)
    for i in range(n_per + 1):
        plot.vlines(i * per, 0, y_max, 'b', ':', lw=2)  # in ms

    # beams for minimum and maximum wavelengths
    # t = np.linspace(-times[2], n_per * per)  # in ms
    t = np.linspace(-times[2], (n_per + 0.3) * per)  # in ms

    # wl_min (and labels for the disks in the plot)
    if n_angles == 6:  # SC2 pair is used
        tof = np.array([times[0], times[5]])
        pos = np.array([0.0, d_SC2])
        minwl = h_m * times[5] / d_SC2 / 1000.0
        label_35 = 'disks 3 and 5'
        label_46 = 'disks 4 and 6'
    else:  # SC2 is not used
        tof = np.array([times[0], times[3]])
        pos = np.array([0, d_SCc])
        minwl = h_m * times[3] / d_SCc / 1000.0
        label_35 = 'disk 3'
        label_46 = 'disk 4'

    if tof[1] == 0.0:
        tof[1] = 1e-6  # a hack to describe infinitely fast neutrons

    f1 = np.polyfit(tof, pos, 1)
    beam2 = np.polyval(f1, t)

    # wl_max
    if disk2_mode == 'normal_mode':
        if n_angles == 6:  # SC2 pair is used
            tof = np.array([times[1], times[4]])
            pos = np.array([d_MCo, d_SC2])
            maxwl = h_m * (times[4] - times[1]) / (d_SC2 - d_MCo) / 1000.
        else:
            tof = np.array([times[1], times[2]])
            pos = np.array([d_MCo, d_SCo])
            maxwl = h_m * (times[2] - times[1]) / (d_SCo - d_MCo) / 1000.

    else:  # chopper system in virtual mode. In this case it is assumed that SC2 is operational

        # Check the real maximum wavelength transmitted due to the modified
        # position and phase of disc2_pos
        maxwl = h_m * (times[4] - times[3]) / (d_SC2 - d_SCo) / 1000.
        maxwl_new = h_m * (times[4] + per - times[1]) / (d_SC2 - d_MCo) / 1000.

        if maxwl_new < maxwl:
            maxwl = maxwl_new
            tof = np.array([times[1], times[4]+per])
            pos = np.array([d_MCo, d_SC2])
        else:
            tof = np.array([times[3], times[4]])
            pos = np.array([d_SCo, d_SC2])

    if tof[1] == 0:
        tof[1] = 1e-6

    f2 = np.polyfit(tof, pos, 1)
    beam3 = np.polyval(f2, t)

    for i in range(-1, n_per + 1):
        ip = i * per

        # disk1: black line
        if i == -1:
            plot.hlines(0, ip, ip + trailing_edge_MC, lw=3, label='disk 1')
        else:
            plot.hlines(0, ip, ip + trailing_edge_MC, lw=3)

        # disk2: blue line
        if i == -1:
            plot.hlines(d_MCo, times[1] - trailing_edge_SC + ip,
                        times[1] + ip, 'b', lw=3, label='disk 2')
        else:
            plot.hlines(d_MCo, times[1] - trailing_edge_SC + ip,
                        times[1] + ip, 'b', lw=3)

        # disk3: green line
        if i == -1:
            plot.hlines(
                d_SCc + 0.05, times[2] + ip, times[2] + trailing_edge_SC + ip,
                'g', lw=3, label=label_35)
        else:
            plot.hlines(
                d_SCc + 0.05, times[2] + ip, times[2] + trailing_edge_SC + ip,
                'g', lw=3)

        # disk4: red line
        if i == -1:
            plot.hlines(d_SCo, times[3] - trailing_edge_SC + ip, times[3] + ip,
                        'r', lw=3, label=label_46)
        else:
            plot.hlines(d_SCo, times[3] - trailing_edge_SC + ip, times[3] + ip,
                        'r', lw=3)

        if (n_angles == 6):  # means we have SC2!
            # disk5: green line
            plot.hlines(d_SC2 + 0.05, times[4] + ip,
                        times[4] + ip + trailing_edge_SC2, 'g', lw=3)
            # disk6: red line
            plot.hlines(d_SC2, times[5] + ip - trailing_edge_SC2,
                        times[5] + ip, 'r', lw=3)

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
                plot.hlines(Actual_D, *plot.get_xlim(), colors='#FF7F39', lw=4)

        plot.plot(t + ip, beam2, 'b')
        plot.plot(t + ip, beam3, 'r')

    plot.set_xlim(0, (n_per + .2) * per)
    plot.set_ylim(0, y_max)

    title = 'Disc phases : %s (deg) at %.0f rpm \n \u03bb\u2098\u1d62\u2099 = \
    %.1f \u212b; \u03bb\u2098\u2090\u2093 = %.1f \u212b' % (
        angles.round(2), speed, minwl, maxwl)

    plot.set_title(title, fontsize='x-small')
    plot.set_xlabel('Time since start signal / ms')
    plot.set_ylabel('Distance from master chopper / m')
    plot.legend(loc='upper center', ncol=6, borderaxespad=0.)
    plot.figure.suptitle(' ', fontsize=16, fontweight='bold')
    if ((Actual_D is not None) and (speed)):
        # check for possible frame overlap. The warning is raised by using an
        # orange frame and a text on top of the plot
        #
        # t_det is the difference between the arrival times of the fastest and
        # slowest neutrons on the detector
        t_det = (Actual_D * (maxwl - minwl) - (
            chopper_pos[disk2_pos] * (disk2_mode == 'normal_mode') +
            chopper_pos[6] * (disk2_mode != 'normal_mode')
            ) * maxwl) / h_m * 1000.

        if t_det > per:
            plot.set_facecolor('orange')
            plot.figure.suptitle(
                'POSSIBLE FRAME OVERLAP. CHECK CHOPPER SETTINGS', fontsize=16,
                fontweight='bold', color='orange')
