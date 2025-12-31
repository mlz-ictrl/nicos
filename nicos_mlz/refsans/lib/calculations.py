# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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
#   Matthias Pomm <matthias.pomm@hereon.de>
#   Gaetano Mangiapia <gaetano.mangiapia@hereon.de>
#
# *****************************************************************************
"""Chopper related devices."""

import copy
import inspect

import numpy as np
from scipy import constants

###########################################################################
#                             MODULE VARIABLES                            #
###########################################################################
# Distances of disk2 from disk 1, for the different positions, in meters.
# disk2_pos is the index of this array (corrected on 08Apr2021)
chopper_pos = np.array([None, .0576, 0.1553, 0.2948, 0.6384, 1.2885, 2.3163])

# Position of SC1 (disks 3 and 4) from disk 1 (in terms of disk2_pos)
SC1_Pos = 6

# distance disk1-SC2 (in meters)
d_SC2 = 10.61645

# horizontal distance from master chopper to pivot point 0 in mm
# (corrected on 10May2021)
pre_sample_path = 11024.6

# The thickness of the D900 detector is 40mm for Drift1 and 65mm for Drift2
# (see \\refsanssrv\docu\Instrument\Detector+Electronics\
# Detector900 DNX-700 SeNr 2016-700-01\Imdetector.pdf)
# This affects the beamline length and wavelength uncertainty. However, the
# detector depth contribution is neglected in the present calculations
detector_depth = 65.0  # in millimeters

# Ratio between Planck constant and neutron mass in Å m /s
h_m = constants.h / constants.m_n * 1.e10


def period(wl_min=0.0, wl_max=18.0, D=22.0, d_MCo=chopper_pos[5]):
    """Return the value of the rotation period of the disks, which ensures a
    permanent illumination of the detector, starting from the geometry and
    desired bandwidth.

    Input:

        wl_min:             minimum transmitted wavelength, in AA (float)
        wl_max:             maximum transmitted wavelength, in AA (float)
        D:                  beamline length, i.e. distance between disk1 and
                            detector, in meters.
                            THIS IS NOT THE FLIGHTPATH (float)
        d_MCo:              distance disk1-disk2, in meters. One can use the
                            chopper_pos list to get the distance (float)

    Output:

        period:             the optimal chopper period (permanent detector
                            illumination), in seconds (float)
    """
    # The optimal chopper period is such that the detector is always illuminated.
    # This happens when the fastest neutrons leaving the MCo just catch up the
    # slowest ones which have started from disk1 (MCc)

    return ((D - d_MCo) * wl_max - D * wl_min) / h_m


def angles_SC1(wl_min=0.0, wl_max=18.0, d_MCo=chopper_pos[5],
               d_SCo=chopper_pos[SC1_Pos], d_SCc=chopper_pos[SC1_Pos],
               freq=10.0):
    """Return the phases of disks 3 and 4 to achieve a given bandpass.

    Normally this task is provided by SC2, thus it is useful when SC2 is not
    in operation.

    Input:

        wl_min:             minimum transmitted wavelength, in AA (float)
        wl_max:             maximum transmitted wavelength, in AA (float)
        d_MCo:              distance disk1-disk2, in meters. One can use the
                            chopper_pos list to get the distance (float)
        d_SCc:              distance from disk1 to disk3, in meters (i.e to
                            the closing disk of SC1) (float)
        d_SCo:              distance from disk1 to disk4, in meters (i.e to
                            the opening disk of SC1) (float)
        freq:               the chopper frequency, in Hertz (float)

    Output:

        [angle3, angle4]:   a numpy array containing the phases of disks 3
                            and 4, in degrees (float)
    """
    t_close_SC1 = (d_SCc - d_MCo) * wl_max / h_m
    t_open_SC1 = d_SCo * wl_min / h_m

    deg_per_sec = 360. * freq

    angle_3 = t_close_SC1 * deg_per_sec
    angle_4 = t_open_SC1 * deg_per_sec

    return np.array([angle_3, angle_4])


def angles_SC2(wl_min=0.0, wl_max=18.0, d_MCo=chopper_pos[5], freq=10.0):
    """Return the phases of disks 5 and 6 to achieve a given bandpass.

    Input:

        wl_min:             minimum transmitted wavelength, in AA (float)
        wl_max:             maximum transmitted wavelength, in AA (float)
        d_MCo:              distance disk1-disk2, in meters. One can use the
                            chopper_pos list to get the distance (float)
        freq:               the chopper frequency, in Hertz (float)

    Output:

        [angle5, angle6]:   a numpy array containing the phases of disks 5
                            and 6, in degrees (float)
    """
    t_close_SC2 = (d_SC2 - d_MCo) * wl_max / h_m
    t_open_SC2 = d_SC2 * wl_min / h_m

    deg_per_sec = 360. * freq

    angle_5 = t_close_SC2 * deg_per_sec
    angle_6 = t_open_SC2 * deg_per_sec

    return np.array([angle_5, angle_6])


def angles_SC2_time(t_SC2o, t_SC2c, freq):
    """Return the phases of discs 5 and 6 as well as their difference
    angle5 - angle6, starting from the knowledge of their opening and
    closing-times.

    Input:

        t_SC2o:         opening time of SC2 pair (i.e. of disc6),
                        in seconds (float)
        t_SC2c:         closing time of SC2 pair (i.e. of disc5),
                        in seconds (float)
        freq:           chopper frequency, in Hertz (float)

    Output:

        ang_SC2:        a numpy array containing the phases of discs 5 and 6,
                        in degrees (float)
        SC2_opening:    the SC2 aperture, i.e. angle5 - angle6, in degrees
                        (float)
    """
    ang_SC2 = np.array([t_SC2c, t_SC2o]) * freq * 360.
    SC2_opening = ang_SC2[0] - ang_SC2[1]
    return ang_SC2, SC2_opening


def practical_SC2(wl_min=0.0, wl_max=6.0, D=22.8, disk2_pos=3,
                  freq_max=100.0, SC2_full_open=240.0, gap=0.1):
    """Calculate the chopper frequency and SC2 angles to use (i.e. phases of
    disks 5 and 6) for the following configurations:

        'default':              in this configuration, the period is
                                determined by the difference between
                                the arrival of the fastest neutrons and
                                the slowest neutrons on the detector.
                                This value can be increased by introducing
                                a period of time during which the detector
                                is not illuminated, as a safety feature
                                (see gap). If this configuration results in
                                disks 5 and 6 being open larger than
                                SC2_full_open, the configuration returned in
                                output will be 'default_full_open'.

        'default_full_open':    in this configuration, the period is
                                determined by imposing that the opening
                                of SC2 is as large as possible (i.e.
                                imposing that the difference between the
                                phases of disks 5 and 6 be equal to
                                SC2_full_open). In this configuration the gap
                                gap parameter is ignored. This configuration
                                could generate frame overlap if the detector
                                is too far from disk 1.

        'full_open':            this configuration is identical to
                                'default_full_open', with the difference that
                                a different detector position is returned in
                                output such to produce a permanent
                                illumination.

        'single_period':        safest configuration: the period is determined
                                by the arrival time of the slowest neutrons on
                                the detector (gap parameter is ignored)

    Input:

        wl_min:             minimum transmitted wavelength, in AA (float)
        wl_max:             maximum transmitted wavelength, in AA (float)
        D:                  beamline length, i.e. distance between disk1 and
                            detector, in meters.
                            THIS IS NOT THE FLIGHTPATH (float)
        disk2_pos:          position of disk2, 1-6 (int)
        freq_max:           the maximum allowed frequency of the chopper,
                            in Hertz (float).
                            THIS PARAMETER IS CURRENTLY IGNORED AND IS REPORTED
                            ONLY FOR BACKWARDS COMPATIBILITY REASONS
        SC2_full_open:      maximum possible aperture of SC2 pair, in degrees
                            (float)
        gap:                the fraction of a period in which the detector
                            should not be illuminated between the end of a frame
                            and the beginning of the next one (float)

    Output:

        a nested dictionary with different keys. The outer dictionary contains,
        as keys, the opening and closing times of SC2 disks (in seconds) for
        the 'default' configuration (times which are actually not needed but
        are neverthless provided for backwards compatibility reasons) and the
        various configurations as keys ('default', 'default_full_open', etc.).
        Each of these latter keys corresponds to a dictionary with the
        following subkeys:

        'per':              period of the pulse, in seconds (float)
        'freq':             chopper frequency, in Hertz (float)
        'rpm':              rotation disk speed, in rounds per minute (float)
        'ang_SC2':          array with the angles for disks 5 and 6, in
                            degrees (float)
        'SC2_opening':      opening of disks 5 and 6, i.e. difference between
                            the phases of disks 5 and 6, in degrees (float)
        'D':                distance between disk1 and detector, in meters
                            (float)
        'overlap':          relative overlap: if tmax and tmin are the
                            arrival times of the slowest and fastest neutrons
                            on the detector, respectively, and T is the
                            period of a frame, then
                            overlap = ((tmax - tmin) - T) / T
                            A positive value indicates a configuration
                            affected by frame overlap (float)
        'resolution':       wavelength resolution, NOT in percentage (float)
        'disk2_pos':        disk2 position. This parameter is basically
                            copied by the input data
        'wl_min_realised':  actual minimum wavelength trasmitted by the
                            configuration, in AA (float)
    """
    d_MCo = chopper_pos[disk2_pos]  # distance of disk2 from disk1

    # convert wavelength input in velocities (in meters per second)
    vel_min = h_m / wl_max

    # flight path (in meters) and wavelength resolution
    flightpath = D - d_MCo * 0.5
    resol = d_MCo * 0.5 / flightpath

    # _dD_SC2 = D - d_SC2  # Distance of disk2 from SC2

    #####################################################################
    # 'default' configuration uses the given detector position and sets the
    # period as the difference between the arrival of the fastest neutrons
    # and the slowest neutrons on it, plus possibly a small silent period
    # (gap).
    tof_min = D * wl_min / h_m
    tof_max = (D - d_MCo) / vel_min

    per = (tof_max - tof_min) * (1.0 + gap)
    freq = 1.0 / per
    rpm = freq * 60.0

    # Cloosing and opening times of SC2
    t_SC2c = (d_SC2 - d_MCo) / vel_min
    t_SC2o = d_SC2 * wl_min / h_m

    ang_SC2, SC2_opening = angles_SC2_time(t_SC2o, t_SC2c, freq)
    overlap = -gap / (1.0 + gap)

    res = {'t_SC2o': t_SC2o,
           't_SC2c': t_SC2c,
           'default': {'per': per,
                       'freq': freq,
                       'rpm': rpm,
                       'ang_SC2': ang_SC2,
                       'SC2_opening': SC2_opening,
                       'D': D,
                       'overlap': overlap,
                       'resolution': resol,
                       'disk2_pos': disk2_pos,
                       'wl_min_realised': wl_min
                       }
           }

    #####################################################################
    # 'default_full_open' configuration uses the given detector position and
    # the full apertures of SC2. In this case the maximal opening is fixed
    # (as if we used a single disk) and we must adapt the frequency to the
    # opening

    per_dfo = (360. / SC2_full_open) * (t_SC2c - t_SC2o)
    freq_dfo = 1. / per_dfo
    rpm_dfo = freq_dfo * 60.

    ang_SC2_dfo, _SC2_opening_dfo = angles_SC2_time(t_SC2o, t_SC2c, freq_dfo)

    overlap_dfo = (tof_max - tof_min) / per_dfo - 1.0
    res['default_full_open'] = {'per': per_dfo,
                                'freq': freq_dfo,
                                'rpm': rpm_dfo,
                                'ang_SC2': ang_SC2_dfo,
                                'SC2_opening': SC2_full_open,
                                'D': D,
                                'overlap': overlap_dfo,
                                'resolution': resol,
                                'disk2_pos': disk2_pos,
                                'wl_min_realised': wl_min
                                }

    # now we check if the 'default' configuration calculated has a valid SC2
    # aperture, and correct if needed
    if res['default']['SC2_opening'] > SC2_full_open:
        res['default'].update(res['default_full_open'])

    #####################################################################
    # 'full_open' is almost identical to 'default_full_open', using the full
    # aperture of SC2 but adjust D to maximize the intensity.
    # period, frequency, rotation speed and angles of SC2 are identical to
    # the ones of the 'default_full_open' configuration

    # To determine the beamline length, we have to impose that the arrival time
    # of the slowest neutrons in a frame is identical to the arrival time of
    # the fastest neutrons of the subsequent frame
    D_fo = (wl_max * d_MCo + h_m * per_dfo) / (wl_max - wl_min)

    resol_fo = d_MCo * 0.5 / (D_fo - d_MCo * 0.5)
    overlap_fo = 0.0

    res['full_open'] = {
        'per': per_dfo,
        'freq': freq_dfo,
        'rpm': rpm_dfo,
        'ang_SC2': ang_SC2_dfo,
        'SC2_opening': SC2_opening,
        'D': D_fo,
        'overlap': overlap_fo,
        'resolution': resol_fo,
        'disk2_pos': disk2_pos,
        'wl_min_realised': wl_min
        }

    #####################################################################
    # 'single_frame' configuration uses, as period, the flight time of the
    # slowest neutrons
    per_sf = tof_max
    freq_sf = 1.0 / per_sf
    rpm_sf = freq_sf * 60.

    ang_SC2_sf, SC2_opening_sf = angles_SC2_time(t_SC2o, t_SC2c, freq_sf)

    # Setting the period of the pulse equal to the time of flight of the
    # slowest neutrons could result in an opening of disks 5 and 6 such to
    # exceed the maximum possible phase difference, especially when a too
    # short disk 1 - detector distance is used: if this occurs, the wished
    # minimum wavelength can not be provided and it has to be increased
    # (the maximum wavelength determines the period and depends only on
    # the disk 1 - detector distance and therefore cannot be modified).

    if (SC2_opening_sf > SC2_full_open):

        t_SC2o_sf = t_SC2c - per_sf / (360. / SC2_full_open)
        ang_SC2_sf, SC2_opening_sf = angles_SC2_time(t_SC2o_sf, t_SC2c,
                                                     freq_sf)

        wl_min_real = h_m * t_SC2o_sf / d_SC2
        tof_min_sf = D * t_SC2o_sf / d_SC2

    else:
        wl_min_real = wl_min
        tof_min_sf = tof_min

    overlap_sf = (tof_max - tof_min_sf) / per_sf - 1.0

    res['single_frame'] = {'per': per_sf,
                           'freq': freq_sf,
                           'rpm': rpm_sf,
                           'ang_SC2': ang_SC2_sf,
                           'SC2_opening': SC2_opening_sf,
                           'D': D,
                           'overlap': overlap_sf,
                           'resolution': resol,
                           'disk2_pos': disk2_pos,
                           'wl_min_realised': wl_min_real
                           }

    return res


def chopper_parasitic(res, wl_start=25.0, wl_stop=95.0, wl_step=0.1,
                      deg_step=1.0):
    """Return a (nested) list of wavelength-bands which are transmitted by the
    chopper system.

    This is particularly useful for verifying the presence of any parasitic
    bands transmitted. The routine finds the parasitic ranges with a
    brute-force appproach, which is time-consuming. If the only interest
    is to know whether a certain configuration produces parasitic neutrons or
    not, the routine chopper_parasitic_bool is recommended

    Input:

        res:                output dictionary as returned by chopper_config.
                            The dictionary must contain, among others, the REAL
                            phases of disks from 2 to 6 (in degrees), their
                            rotational speed in rounds per minute, and the REAL
                            position of disk2 (1-5)
        wl_start:           minimum wavelength to be used for the search for
                            parasitic neutrons, in AA (float)
        wl_stop:            maximum wavelength to be used for the search for
                            parasitic neutrons, in AA (float)
        wl_step:            wavelength step to be used for the search, in AA:
                            the wavelengths from wl_start to wl_stop with steps
                            of wl_step will be probed (float)
        deg_step:           step through the disk1 aperture to be probed, in
                            degrees. The program will check all the neutrons
                            crossing the master chopper from 240 deg to 360 deg
                            phase, with steps defined by deg_step (float)

    Output:
        wl_through:         output list containing the wavelengths (in AA)
                            which are able to be transmitted by the chopper
                            system. The list can be composed by sublists
                            and / or single elements. A sublist contains the
                            wl_min-wl_max of a certain interval transmitted.
                            A single element represents a single (isolated)
                            wavelength found: usually this means that the
                            wavalength band transmitted has a width comparable
                            or smaller than wl_step or is transmitted through
                            a narrow region of disk1, which is in extension
                            comparable or smaller than deg_step
    """
    # The subroutine works in this way: for each wavelength, it starts from the
    # first frame and the master chopper, controlling all the possible phases
    # from 240 deg (the initial opening) up to 360 (when the master chopper
    # closes). For each phase, the path of the neutron is followed, checking
    # if it crosses a closed disk during the flight. The disks 1 and 2 are
    # assumed to have a single aperture of 120 deg. disks 3 and 4 are assumed
    # to have multiple apertures, as they have. In particular disk3 has four
    # apertures. If the edge of the beam closing is null, the apertures are
    # located:
    #
    # - between 213.0 deg and 217.0 deg
    # - between 223.5 deg and 226.5 deg
    # - between 234.0 deg and 236.0 deg
    # - between 240.0 deg and 360.0 deg (main aperture)
    #
    # disk4 has also four apertures. If the edge of the beam opening is
    # null, the apertures are located:
    #
    # - between   0.0 deg and 120.0 deg (main aperture)
    # - between 153.0 deg and 157.0 deg
    # - between 164.0 deg and 166.0 deg
    # - between 173.5 deg and 176.5 deg
    #
    # Between the opening edge of disk3 (240 deg) and the opening edge of the
    # most distant slit (213.0 deg) there are 27 deg of "extension".
    # Analogously between the closing edge of disk4 (120 deg) and the closing
    # edge of the most distant slit (176.5 deg) there are 56.5 deg
    # of "extension".
    # Now it is possible to ignore the additional apertures located on the
    # SC1 pair because the phase difference phi(disk3) - phi(disk4) may
    # vary between 0 deg and 120 deg, where the overlap between the disks goes
    # from 120 deg to 240 deg. In no cases this overlap goes below
    # 83.5 deg = 27 deg + 56.5 deg  which is the critical value to not get
    # neutrons passing through the additional slits

    # Checks that the position of disk2 is not virtual, raising eventually
    # an error
    disk2_pos = res['disk2_Pos']

    if disk2_pos == 6:
        raise Exception('Error! A value indicating the REAL position of'
                        'slave chopper has to be provided')

    if wl_stop < wl_start:
        raise Exception('Error! wl_stop might not be smaller than wl_start')

    # Array containing the phases from disk2 to disk6, in deg
    phase_arr = res['angles'][1:6]

    # Brings all the phases inside the range [0, 360[
    if (phase_arr[3] is None) and (phase_arr[4] is None):
        phase_arr[0:3] = np.mod(phase_arr[0:3], 360.0)
    else:
        phase_arr = np.mod(phase_arr, 360)

    # Width of disk opaque regions (from 2 to 6)
    if (phase_arr[3] is None) and (phase_arr[4] is None):
        ch_deg = np.array([240.0, 240.0, 240.0, 0.0, 0.0])  # SC2_Mode = None
    else:
        ch_deg = np.array([240.0, 240.0, 240.0, 120.0, 120.0])

    # disk1-disk2 distance in millimeters for the current position
    d_MS = 1000. * chopper_pos[disk2_pos]

    # disk1-SC1 distance in millimeters
    d_SC1 = 1000. * chopper_pos[SC1_Pos]

    # distances (in millimeters) at which the phases for the neutrons of the
    # various wavelengths have to be calculated
    d_check = np.array([d_MS, d_SC1, d_SC1, d_SC2 * 1.e3, d_SC2 * 1.e3])

    # Calculate the "forbidden" phases for disks from 2 to 6, for which
    # neutrons cannot be transmitted,
    phase_opaques = [None] * 5

    for i in range(0, 5, 2):  # It operates on the phases of disks 2, 4, 6. The
                              # index i runs on the elements of the phase_arr list
        if (phase_arr[i] is not None):
            t = np.mod(phase_arr[i], 360)
            if (t >= ch_deg[i]):
                phase_opaques[i] = [t-ch_deg[i], t, -np.inf, -np.inf]
            else:
                phase_opaques[i] = [0., t, t + 360. - ch_deg[i], 360.]
        else:
            phase_opaques[i] = [-np.inf, -np.inf, -np.inf, -np.inf]

    for i in range(1, 5, 2):  # It operates on the phases of disks 3 and 5. The
                              # index i runs on the elements of the phase_arr list
        if (phase_arr[i] is not None):
            t = np.mod(phase_arr[i], 360)
            if (t < 360. - ch_deg[i]):
                phase_opaques[i] = [t, t + ch_deg[i], -np.inf, -np.inf]
            else:
                phase_opaques[i] = [0., t + ch_deg[i] - 360., t, 360.]
        else:
            phase_opaques[i] = [-np.inf, -np.inf, -np.inf, -np.inf]

    wl_through = []  # Contains the list of neutrons with transmitted
                     # wavelengths
    ph_through = []  # Contains the list of the smallest possible phases of the
                     # transmitted neutrons: this is useful for plotting

    per = 60000. / res['rpm']  # Duration of a period in milliseconds

    fact_ang = h_m * per / 360.0  # factor to convert the wavelengths into phase
                                  # velocity, in Å mm / deg

    if (wl_start == 0.0):
        wl_start = wl_step

    wl = wl_start - wl_step

    # Number of wavelengths to check
    n_checks = int(np.ceil((wl_stop - wl_start) / wl_step + 1))

    # Maximum number of phases starting from disk 2 to check
    nmax_grad = int(np.ceil((360 - ch_deg[0]) / deg_step + 1))

    k_prev = -np.inf  # k_prev is the previous value of k (index that runs
                      # over the various wavelengths) for which the transmission
                      # of neutrons was found

    phase_min = -np.inf  # Minimum phase to be included in the ph_thorugh list

    for k in range(n_checks):

        wl += wl_step

        # It transforms the wavelength into phase velocity (i.e. how much angle
        # is swept per unit of time)
        vl_ang = fact_ang / wl  # in mm / deg. This is the angular coefficient
                                # of the neutron's trajectory on the
                                # phase / distance diagram

        # Now we need to check all the straight lines having this angular
        # coefficient and starting at any point from 240 to 360
        deg0 = ch_deg[0] - deg_step

        for j in range(nmax_grad):

            deg0 += deg_step

            # This trajectory has as equation: d = vl_ang * (phase - deg0). We
            # calculate the phase when d is corresponds to the position of the
            # various disks
            ierr = 0
            for i in range(5):
                phase_act = d_check[i]/vl_ang + deg0
                phase_red = np.mod(phase_act, 360.0)

                if ((phase_opaques[i][0] <= phase_red <= phase_opaques[i][1]) or
                   (phase_opaques[i][2] <= phase_red <= phase_opaques[i][3])):
                    ierr = 1  # Blocked neutron
                    break  # It is not necessary to verify the other disks

            if ((ierr == 1) and (k == k_prev + 1) and (j == nmax_grad - 1)):
                # The blocked neutron is the first appearing after a block of
                # transmitted neutrons
                if (wl_through[-1][0] != wl-wl_step):  # It might be a bandwidth
                                                       # smaller than wl_step
                    wl_through[-1].append(wl-wl_step)
                    ph_through[-1].append(phase_min)

            elif ((ierr == 0) and (k != k_prev + 1)):
                # The transmitted neutron is the first appearing after a block
                # of blocked neutrons
                wl_through.append([wl])
                ph_through.append([deg0])
                k_prev = k
                break  # It is not necessary to verify the other phases

            elif ((ierr == 0) and (k == k_prev + 1)):
                # The passing neutron is in a block of transmitted neutrons
                k_prev = k
                phase_min = deg0
                if (k == n_checks - 1):  # Last wavelength to be verified
                    wl_through[-1].append(wl)
                    ph_through[-1].append(deg0)

                break  # It is not necessary to verify the other phases

    return wl_through


def chopper_parasitic_bool(res, wl_start=25.0, wl_stop=95.0, wl_step=0.1,
                           deg_step=1.0):
    """Check whether parasitic bands are transmitted by a certain configuration
    of the chopper system.

    This routine does not provide the values of the parasitic wavelengths
    transmitted, and is normally (up to 15%) faster than the routine
    chopper_parasitic.

    Input:

        res:                output dictionary as returned by chopper_config.
                            The dictionary must contain, among others, the REAL
                            phases of disks from 2 to 6 (in degrees), their
                            rotational speed in rounds per minute, and the REAL
                            position of disk2 (1-5)
        wl_start:           minimum wavelength to be used for the search for
                            parasitic neutrons, in AA (float)
        wl_stop:            maximum wavelength to be used for the search for
                            parasitic neutrons, in AA (float)
        wl_step:            wavelength step to be used for the search, in AA:
                            the wavelengths from wl_start to wl_stop with steps
                            of wl_step will be probed (float)
        deg_step:           step through the disk1 aperture to be probed, in
                            degrees. The program will check all the neutrons
                            crossing the master chopper from 240 deg to 360 deg
                            phase, with steps defined by deg_step (float)

    Output:
                            In output a boolean value is returned specifying
                            whether parasitic wavelengths are trasmitted
                            (True) or not (False)
    """
    # The subroutine works mostly like chopper_parasitic

    # Checks that the position of disk2 is not virtual, raising eventually an
    # error
    disk2_pos = res['disk2_Pos']

    if disk2_pos == 6:
        raise Exception('Error! A value indicating the REAL position of'
                        'slave chopper has to be provided')

    if wl_stop < wl_start:
        raise Exception('Error! wl_stop might not be smaller than wl_start')

    # Array containing the phases from disk2 to disk6, in deg
    phase_arr = res['angles'][1:6]

    # Brings all the phases inside the range [0, 360[
    if (phase_arr[3] is None) and (phase_arr[4] is None):
        phase_arr[0:3] = np.mod(phase_arr[0:3], 360.0)
    else:
        phase_arr = np.mod(phase_arr, 360.0)

    # Width of disk opaque regions (from 2 to 6)
    if (phase_arr[3] is None) and (phase_arr[4] is None):
        ch_deg = np.array([240., 240., 240., 0., 0.])  # SC2_Mode = None
    else:
        ch_deg = np.array([240., 240., 240., 120., 120.])

    # disk1-disk2 distance in millimeters for the current position
    d_MS = 1000. * chopper_pos[disk2_pos]

    # disk1-SC1 distance in millimeters
    d_SC1 = 1000. * chopper_pos[SC1_Pos]

    # distances (in millimeters) at which the phases for the neutrons of the
    # various wavelengths have to be calculated
    d_check = np.array([d_MS, d_SC1, d_SC1, d_SC2 * 1.e3, d_SC2 * 1.e3])

    # Calculate the "forbidden" phases for disks from 2 to 6, for which
    # neutrons cannot be transmitted,
    phase_opaques = [None] * 5

    for i in range(0, 5, 2):
        # It operates on the phases of disks 2, 4, 6. The index i runs on the
        # elements of the phase_arr list
        if phase_arr[i] is not None:
            p = np.mod(phase_arr[i], 360)
            if p >= ch_deg[i]:
                phase_opaques[i] = [p - ch_deg[i], p, -np.inf, -np.inf]
            else:
                phase_opaques[i] = [0., p, p + 360. - ch_deg[i], 360.]
        else:
            phase_opaques[i] = [-np.inf, -np.inf, -np.inf, -np.inf]

    for i in range(1, 5, 2):
        # It operates on the phases of disks 3 and 5. The index i runs on the
        # elements of the phase_arr list
        if phase_arr[i] is not None:
            p = np.mod(phase_arr[i], 360)
            if p < 360. - ch_deg[i]:
                phase_opaques[i] = [p, p + ch_deg[i], -np.inf, -np.inf]
            else:
                phase_opaques[i] = [0., p + ch_deg[i] - 360., p, 360.]
        else:
            phase_opaques[i] = [-np.inf, -np.inf, -np.inf, -np.inf]

    per = 60000. / res['rpm']  # Duration of a period in milliseconds

    # factor to convert the wavelengths into phase velocity, in Å mm / deg
    fact_ang = h_m * per / 360.0

    if wl_start == 0.0:
        wl_start = wl_step

    wl = wl_start - wl_step
    n_checks = int(np.ceil((wl_stop - wl_start) / wl_step + 1))
    # Number of wavelengths to check
    nmax_grad = int(np.ceil((360 - ch_deg[0]) / deg_step + 1))
    # Maximum number of phases starting from disk 2 to check

    for _k in range(n_checks):

        wl += wl_step

        # It transforms the wavelength into phase velocity (i.e. how much angle
        # is swept per unit of time)
        vl_ang = fact_ang / wl
        # in mm / deg. This is the angular coefficient of the neutron's
        # trajectory on the phase / distance diagram

        # Now we need to check all the straight lines having this angular
        # coefficient and starting at any point from 240 to 360
        deg0 = ch_deg[0] - deg_step

        for _j in range(nmax_grad):

            deg0 += deg_step

            # This trajectory has as equation: d = vl_ang * (phase - deg0).
            # We calculate the phase when d is corresponds to the position of
            # the various disks
            ierr = 0
            for i in range(5):
                phase_act = d_check[i] / vl_ang + deg0
                phase_red = np.mod(phase_act, 360)

                if ((phase_opaques[i][0] <= phase_red <= phase_opaques[i][1]) or
                   (phase_opaques[i][2] <= phase_red <= phase_opaques[i][3])):
                    ierr = 1  # Blocked neutron
                    break  # It is not necessary to verify the other disks

            if (ierr == 0):
                return True

    return False


def adjust_parasitic_SC1(res, wl_start=25.0, wl_stop=95.0, wl_step=0.1,
                         deg_step=1.0, prec_phase=0.005):
    """Adjust the phases of disks 3 and 4 (SC1 pair) to suppress parasitic
    wavelength bands, when possible.

    Input:

        res:                output dictionary as returned by
                            chopper_config. The dictionary must contain,
                            among others, the REAL phases of disks from 2
                            to 6 (in degrees), their rotational speed in
                            rounds per minute, and the REAL position of
                            disk2 (1-5)
        wl_start:           minimum wavelength to be used for the search
                            for parasitic neutrons, in AA (float)
        wl_stop:            maximum wavelength to be used for the search
                            for parasitic neutrons, in AA (float)
        wl_step:            wavelength step to be used for the search, in
                            AA: the wavelengths from wl_start to wl_stop
                            with steps of wl_step will be probed (float)
        deg_step:           step through the disk1 aperture to be probed,
                            in degrees. The program will check all the
                            neutrons crossing the master chopper from 240
                            deg to 360 deg phase, with steps defined by
                            deg_step (float)
        prec_phase:         Precision of the phases for disks 3 and 4 to
                            be found: the phases of SC1 will be provided
                            within this value (float)

    Output:
         [angle3, angle4]   a numpy array containing the adjusted phases
                            of disks 3 and 4, in degrees (float). If the
                            refinement is not possible, None is returned
    """
    # The idea behind this routine is to start from a limit situation in which
    # the phases of SC1 pair define the wished wavelength band (therefore
    # behaving like SC2). If this configuration is "clean", in the sense that
    # it does not transmit parasitic neutrons, the two phases of SC1 are
    # "relaxed" (i.e. SC1 is opened as much as possbile) until a parasitic
    # band is found, using a dichotomic approach

    # we create a temp variable res_bis with which we operate
    res_bis = copy.deepcopy(res)

    # Let us evaluate the phases of SC1 such to behave as SC2: the phases of
    # disks 3 and 4 must lock the slowest and fastest wavelengths
    new_ph = angles_SC1(wl_min=res['wl_min'], wl_max=res['wl_max'],
                        d_MCo=chopper_pos[res['disk2_Pos']],
                        freq=res['freq'])

    res_bis['angles'][2] = new_ph[0]  # new phase disk3
    res_bis['angles'][3] = new_ph[1]  # new phase disk4

    # If this configuration is affected by parasitic neutrons, the subroutine
    # is stopped and a warning is displayed
    if chopper_parasitic_bool(res_bis, wl_start=wl_start, wl_stop=wl_stop,
                              wl_step=wl_step, deg_step=deg_step):
        return None

    for i in range(3, 1, -1):  # i=3 for disk4; i=2 for disk3
        toll = abs(new_ph[i-2] - res['angles'][i])

        old_val = res['angles'][i]
        while (toll >= prec_phase):

            res_bis['angles'][i] = (new_ph[i-2] + old_val) / 2.0

            if not chopper_parasitic_bool(
               res_bis, wl_start=wl_start, wl_stop=wl_stop, wl_step=wl_step,
               deg_step=deg_step):
                # The new phase is acceptable
                new_ph[i-2] = res_bis['angles'][i]
            else:  # We have to move in the direction of a restricted apertures
                old_val = res_bis['angles'][i]

            toll /= 2.0

        res_bis['angles'][i] = new_ph[i-2]

    return np.array([res_bis['angles'][2], res_bis['angles'][3]])


def chopper_config(wl_min=2.2, wl_max=21.0, D=22.8, disk2_pos=3,
                   gap=0.1, delay=0.0, SC2_mode='default',
                   SC2_full_open=240.0, suppress_parasitic=True,
                   wl_stop=95.0, interface=True):
    """Calculate the full chopper configuration.

    Input:

        wl_min:             minimum desired wavelength in AA (float)
        wl_max:             maximum desired wavelength in AA (float)
        D:                  beamline length, i.e. distance between disk1
                            and detector, in meters.
                            THIS IS NOT THE FLIGHTPATH (float)
        disk2_pos:          position of disk2 (1-6) (int)
        gap:                fraction of a period in which the detector
                            should not be illuminated between the end of a
                            frame and the beginning of the next one
                            (float). This parameter has effect only if
                            SC2_mode is set to 'default' or 'None' (float)
        delay:              a time delay to use as an offset for the clock
                            (affects the apparent tof) (float)
        SC2_mode:           configuration of SC2 pair: it may assume one of
                            the following values:

                            'default': in this configuration, the period is
                            determined by the difference between the
                            arrival of the fastest neutrons and the slowest
                            neutrons on the detector. This value can be
                            increased by introducing a period of time
                            during which the detector is not illuminated,
                            as a safety feature (see gap). If this
                            configuration results in disks 5 and 6 being
                            open larger than SC2_full_open, the
                            configuration returned in output will be
                            'default_full_open'.

                            'default_full_open': in this configuration, the
                            period is determined by imposing that the
                            opening of SC2 is as large as possible (i.e.
                            imposing that the difference between the phases
                            of disks 5 and 6 be equal to SC2_full_open). In
                            this configuration the gap parameter is
                            ignored. This configuration could generate
                            frame overlap if the detector is too far from
                            disk 1.

                            'full_open': this configuration is identical to
                            'default_full_open', with the difference that a
                            different detector position is returned in
                            output such to produce a permanent
                            illumination.

                            'single_period': safest configuration: the
                            period is determined by the arrival time of
                            the slowest neutrons on the detector (gap
                            parameter is ignored)

                            None: this value indicates a system with only
                            four disks, where the SC2 pair is not in
                            operation. In this case SC1 takes over the role
                            of SC2 and a configuration similar in some
                            respects to 'default' is returned (str)
        SC2_full_open:      maximum possible aperture of SC2 pair,
                            in degrees (float)
        suppress_parasitic: flag to check whether the configuration
                            transmits parasitic neutrons, i.e. neutrons
                            whose wavelength is larger than wl_max (bool)
        wl_stop:            maximum wavelength to be used for the search
                            for parasitic neutrons, in AA. This value has
                            effect only if suppress_parasitic = True
                            (float)
        interface:          THIS PARAMETER IS NO LONGER USED BUT IS KEPT
                            HERE JUST IN CASE. Originally it was used to
                            force the subroutine to return a dictionary
                            which is consistent with other subroutines
                            existing in NICOS

    Output:

        a set of quantities, namely:

        'rpm':              rotation disk speed, in rounds per minute,
                            rounded to the nearest integer (int)
        'angles':           a list with the disk phases from disk 1 to
                            disk 6, in degrees (float)
        'disk2_Pos':        the position of disk2 (1-6). If this value is 6,
                            then the position of disk2, as well its phase,
                            have to be intended as virtual values (int)
        'D':                distance between disk1 and detector,
                            in meters (float)
        'wl_min':           the minium wavelength transmitted, in AA (float)
        'wl_max':           the maximum wavelength transmitted, in AA (float)

        In case no working configurations can be found, all the output
        variables are set to None
    """
    if ((SC2_mode is None) and (disk2_pos == 6)):
        # We may not put disk2 in position 6 without SC2.
        return None, 6 * [None], None, None, None, None

    d_MCo = chopper_pos[disk2_pos]  # distance of disk2 from disk1

    # disks 3 and 4 (SC1) are at position with a small gap
    # between the two (neglected)
    d_SCo = chopper_pos[SC1_Pos]  # disk4
    d_SCc = chopper_pos[SC1_Pos]  # disk3

    if SC2_mode is not None:  # We start to get the phases of disks 5 and 6
        SC2_all = practical_SC2(wl_min=wl_min, wl_max=wl_max, D=D,
                                disk2_pos=disk2_pos,
                                SC2_full_open=SC2_full_open, gap=gap)
        SC2 = SC2_all[SC2_mode]
        D = SC2['D']
        freq = SC2['freq']
        angle_SC2 = SC2['ang_SC2']
        wl_min_realised = SC2['wl_min_realised']
        rpm = SC2['rpm']
        deg_per_sec = 360. * freq  # 'degrees' swept by the disks per second
        overlap = SC2['overlap']

        # We get the values for disks 3 and 4 such to cut very slow neutrons

        # Slave closing, must be calculated  not for wl_max but for:
        angle_SCc = d_SCc / d_SC2 * angle_SC2[0]

        # idem for the opening
        angle_SCo = (d_SCo - d_MCo) / (d_SC2 - d_MCo) * angle_SC2[1]

    else:
        # SC2 is not in operation. We use SC1 as disks to determine the
        # wavelength band
        SC2 = {'angles':          None,
               'rpm':             None,
               'freq':            None,
               'wl_min_realised': None
               }

        angle_SC2 = (None, None)
        freq = 1. / period(wl_min=wl_min, wl_max=wl_max,
                           D=D * (1. + gap), d_MCo=d_MCo)
        rpm = 60. * freq
        deg_per_sec = 360. * freq

        t_SCc = (d_SCc - d_MCo) * wl_max / h_m
        t_SCo = d_SCo * wl_min / h_m

        angle_SCc = deg_per_sec * t_SCc
        angle_SCo = deg_per_sec * t_SCo
        wl_min_realised = wl_min

    angles = [0.0, 0.0, angle_SCc, angle_SCo, angle_SC2[0], angle_SC2[1]]

    # The proper dictionary (cut if interface is True) is managed at the end of
    # this routine
    res = {'freq':           freq,
           'rpm':            rpm,
           'angles':         angles,
           'delay_time':     delay,
           'delay_angle':    delay * freq * 360,
           'disk2_Pos':      disk2_pos,
           'SC1_open_angle': angles[2] - angles[3],
           'SC1_phase':      angles[3],
           'SC2_phase':      angles[5],
           'wl_min':         wl_min_realised,
           'wl_max':         wl_max,
           'D':              D,
           'SC2_mode':       SC2_mode,
           }
    if SC2_mode is not None:
        res['SC2_open_angle'] = angles[4] - angles[5]

    # The routine checks if the configuration found produces frame overlap.
    # This is in particular critical if 'default_full_open' is chosen, since
    # this SC2_mode does not modify the beam line extension. Anyway we also
    # check whether the 'default' configuration is affected by this
    # inconvenience, since, when the 'default' needs a SC2 opening larger than
    # the maximum value, practical_SC2 replaces it with the 'default_full_open'

    if ((SC2_mode == 'default_full_open') or (SC2_mode == 'default')):
        if (overlap > 0.0):
            return None, 6 * [None], None, None, None, None

    # Before to continue, set the flag for virtual6_mode
    virtual6_mode = (disk2_pos == 6)

    # Now the most crucial part: the routine optimizes the configuration to
    # suppress eventual parasitic neutrons (if requested). The optimization
    # proceeds differently, depending on whether disk2_pos = 6 or not.
    #
    # If disk2_pos = 6 then:
    #   - disk2 is moved to position 5
    #   - its phase is set to 300 deg
    #   - eventual parasitic wavelengths are looked for this new configuration.
    # If no parasitic neutrons are found (which is normally not the case), the
    # routine stops and returns the nominal values (i.e. with disk2_pos = 6
    # and its phase set to 0.0 deg (as well as that of disk 4)
    # If parasitic neutrons are found (which is almost always the case) then:
    #   - disk2 is moved to position 1
    #   - its phase is adjusted to suppress the fastest neutrons of the first
    #     parasitic band
    #   - eventual parasitic wavelengths are looked for this adjusted
    #     configuration.
    # If no parasitic neutrons are found, then this new configuration is
    # returned
    # If parasitic neutrons are still present, no confguration is returned
    #
    # If disk_pos < 6 (i.e. from 1 to 5) then:
    #   - the phases of disks 3 and 4 are adjusted with an iterative procedure
    #     to suppress all parasitic bands found, where possible.

    if (suppress_parasitic):

        if (virtual6_mode):  # this means that disk2 = 6
            # Sets the phase of disk2 to the Matthias standard value
            res['angles'][1] = 300
            # Moves the disk in the position which has the minimum capability
            # to suppress parasitic neutrons
            res['disk2_Pos'] = 5

        # Check for parasitic bands, starting from 3 times wl_step "above"
        # wl_max (heuristic approach)
        parasitic_wl = chopper_parasitic(
            res, wl_start=wl_max + 3.0 *
            inspect.signature(chopper_parasitic).parameters['wl_step'].default,
            wl_stop=wl_stop)

        if len(parasitic_wl) > 0:

            if (virtual6_mode):  # Optimization for disk2_pos = 6

                # Gets the minimum wavelength of the first parasitic
                # wavelength band
                if isinstance(parasitic_wl[0], list):
                    parasitic_wl = parasitic_wl[0][0]
                else:
                    parasitic_wl = parasitic_wl[0]

                # Gets the velocity of the fastest neutron of the first
                # parasitic wavelength band
                parasitic_vl = h_m / parasitic_wl  # velocity in m/s

                # In order to know the phase to be set for disk2, we
                # have to know the trajectory of the parasitic neutron in a
                # distance/phase diagram.
                # If parasitic_vl is the neutron velocity, the trajectory has
                # as equation:
                #
                #  distance = parasitic_vl * T / 360 * (phase - phase_1)
                #
                # where T is the chopper period and phase_1 the phase of disk1
                # (master chopper) when the parasitic neutron gets in to the
                # chopper system (let us say in the first frame, hence
                # 240 <= phase_1 <= 360). The quantity
                #
                #                    parasitic_vl * T / 360
                #
                # basically corresponds to the distance swept by the parasitic
                # neutron in 1 deg of phase. To get the value for phase_1, we
                # impose that the parasitic neutron crosses the edge of disk 3
                # (in the second frame) when it reaches SC1, which has a
                # distance of d_SCc from master disk:
                #
                # phase_1 = (phase_3 + 360) -  d_SCc * 360 / (parasitic_vl * T)
                #
                # where phase_3 is the phase of disk3 which is located in the
                # range [0, 360[ (as always provided by chopper_config). Once
                # we know the value of phase_1, we move disk2 to position 1
                # and set its phase to cut with its edge the parasitic neutron
                # (this task always happens in the first frame).
                # If phase_2 is the phase to be found, we have:
                #
                #  phase_2 = (phase_3 + 360) - 360 / (parasitic_vl * T) *
                #             (d_SCc - d_MCo)
                #
                # d_MCo being the distance of disk1 from disk2, **** when this
                # latter is in position 1 ****

                res['disk2_Pos'] = 1
                res['angles'][1] = res['angles'][2] + 360.0 - 360.0 * freq / \
                    parasitic_vl * (d_SCc - chopper_pos[res['disk2_Pos']])

                # Since the phase of disk2 has been moved, we have to make sure
                # the wl_max is really trasmitted from the new configuration.
                # At this aim, let us evaluate the phase value of a neutron
                # with wavelength wl_max (and velocity vl_min) when it is at
                # the new disk2_pos. The equation to be used is
                #
                #  distance = vl_min * T / 360 * (phase - phase_1)
                #
                # where, this time, to find the new value of phase_1
                # (240 <= phase_1 <= 360) we have to impose that the phase of
                # the neutron is 360 deg when it crosses SC1 (because when the
                # system works in virtual mode, disk4 behaves like disk2, then
                # its phase has to be zero):
                #
                #         phase_1 = 360 * (1 - d_SCo / (vl_min * T))
                #
                # Now we have to check which phase this neutron has when it
                # reaches the position where disk2 is installed (d_MCo):
                #
                # phase_at_disk2pos = 360 * (1 - (d_SCo - d_MCo) /
                #                     (vl_min * T))
                #
                # If this phase is smaller than the value phase_2 we have
                # previously evaluated, then this wavelength can not be
                # provided and we have to evaluate the maximum possible
                # trasnmittable wavelength

                vl_min = h_m / wl_max
                phase_at_disk2pos = 360.0 * (1.0 - freq * (
                    d_SCo - chopper_pos[res['disk2_Pos']]) / vl_min)

                if phase_at_disk2pos < res['angles'][1]:
                    # The wl_max can not be provided. We evaluate the new value
                    # for wl_max, by imposing thet the trajectory of the
                    # neutron goes through phase_2 and (phase_5 + 360) at
                    # d = d_MCo and d = d_SC2, respectively
                    new_vl_max = (d_SC2 - chopper_pos[res['disk2_Pos']]) / \
                                  (res['angles'][4] - res['angles'][1] +
                                   360.) * 360. * freq
                    wl_max_real = h_m / new_vl_max
                    res['wl_max'] = wl_max_real

            else:  # Optimization for disk2_pos < 6

                # In this case, starting from the limit situation in which the
                # phases of SC1 pair define the wished wavelength ban
                # (therefore behaving like SC2) we relax the two phases until
                # a parasitic band is found, with a dichotomic approach

                # Gets the maximum wavelength of last parasitic wavelength band
                if isinstance(parasitic_wl[-1], list):
                    parasitic_wl = parasitic_wl[-1][-1]
                else:
                    parasitic_wl = parasitic_wl[-1]

                new_ph = adjust_parasitic_SC1(
                    res, wl_start=wl_max + 3.0 *
                    inspect.signature(adjust_parasitic_SC1).parameters['wl_step'].default,
                    wl_stop=parasitic_wl)

                if (new_ph is None):
                    # The most restrictive configuration for SC1 still
                    # transmits parasitic wavelengths. The routine is
                    # stopped
                    return None, 6 * [None], None, None, None, None
                res['angles'][2] = new_ph[0]
                res['angles'][3] = new_ph[1]

            # Now we check that the found configuration does not produce
            # any other parasitic bands. If the check fails, a warning
            # message is displayed and the routine is stopped
            if chopper_parasitic_bool(
               res, wl_start=res['wl_max'] + 3.0 *
               inspect.signature(chopper_parasitic_bool).parameters['wl_step'].default,
               wl_stop=wl_stop):
                return None, 6 * [None], None, None, None, None

        else:
            # parasitic wavelengths have not been found. If this happens for
            # disk2_Pos = 6, this means that virtual_6 may be achieved for
            # every disk2_pos value

            if (disk2_pos == 6):
                # Sets back the old values for disk2_pos and its phase
                res['disk2_Pos'] = 6
                res['angles'][1] = 0.0

    if interface:  # Removes the keys originally not expected from Jens
        res.pop('freq', None)
        res.pop('delay_time', None)
        res.pop('delay_angle', None)
        res.pop('SC1_open_angle', None)
        res.pop('SC1_phase', None)
        res.pop('SC2_phase', None)
        res.pop('SC2_mode', None)

    # Brings the angles in the range [0, 360[
    if (SC2_mode is not None):
        res['angles'] = np.mod(res['angles'], 360)
    else:
        res['angles'][0:4] = np.mod(res['angles'][0:4], 360)

    return int(round(rpm)), res['angles'], res['disk2_Pos'], res['D'], \
        res['wl_min'], res['wl_max']


def chopper_resolution(disk2_pos, D):
    """Return the relative wavelength resolution of a chopper configuration
    in percentage.

    Input:

        disk2_pos:  position of disk2 (1-6) (int)
        D:          disk1 - detector distance in meters (float). This is the
                    beamline length, NOT the flightpath

    Output:

        resol:      lambda resolution DeltaLambda/Lambda in percentage (float)

    """
    # Uncertainty affecting the flight path (should include half of detector
    # depth, which is neglected)
    uncert = 0.5 * chopper_pos[disk2_pos]

    # Flight path
    flight_path = D - uncert

    # Resolution in percent
    resol = 100.0 * uncert / flight_path

    return round(resol, 3)
