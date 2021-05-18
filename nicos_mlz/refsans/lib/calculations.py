#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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

# Geometrical Parameters
#
#
chopper_pos = [None, .0576, 0.1553, 0.2948, 0.6384, 1.2885, 2.3163]
# in meters from 10.05.2021.
# Old values were:
# chopper_pos = [None, .0715, 0.168, 0.305, 0.651, 1.296, 2.33]

d_SC2 = 10.61645
# distance from disk1 to SC2 (discs 5 and 6) in meters from 10.05.2021.
# Old values was: d_SC2 = 10.61

SC1_Pos = 6
# SC1_Pos is the distance from disk 1 to SC1 (discs 3 and 4) which is now fixed
# at pos 6

pre_sample_path = 11024.6
# horizontal distance from master chopper to pivot point 0 in mm,
# from 10.05.2021. Old value was: pre_sample_path = 11028

# The thickness of the D900 detector is 40mm for Drift1 and 65mm for Drift2
# (see \\refsanssrv\docu\Instrument\Detector+Electronics\
# Detector900 DNX-700 SeNr 2016-700-01\Imdetector.pdf)
# This affects the beamline length and wavelength uncertainty. However, the
# detector depth contribution is neglected in the present calculations
detector_depth = 65  # in millimeters

h_m = constants.h / constants.m_n * 1e10
# Ratio between Planck constant and neutron mass in Å m /s


def period(wl_min=0.0, wl_max=18.0, D=22.0, d_MCo=chopper_pos[5]):
    # New sub added on 10.05.2021, already existing in chopper.py of
    # refsans_tools

    """
    Returns the optimal period of the chopper, which ensures permanent
    illumination of the detector, given the geometry and desired bandwidth

    Input:

        wl_min,wl_max: the wavelength limits in AA (float)
        D:             the disc1 - detector distance in meters (float)
                       !! This is the beamline length, NOT the flightpath !!
        d_MCo:         distance disc1-disc2, in meters. One can use the
                       chopper_pos list to get real values (float)

    Output :

        period:     the optimal chopper period (permanent detector
                    illumination), in seconds (float)
    """

    # The optimal chopper period is such that the detector is always
    # illuminated The fast neutrons leaving the MCo just catch up the slow ones
    # which have started from disc1 (MCc)

    return ((D - d_MCo) * wl_max - D * wl_min) / h_m


def angles_SC1(wl_min=0.0,
               wl_max=18.0,
               d_MCo=chopper_pos[5],
               d_SCo=chopper_pos[6],
               d_SCc=chopper_pos[6],
               freq=10.0,
               ):
    # New sub added on 21.02.2022, already existing in chopper.py of
    # refsans_tools
    """
    Returns the phases of discs 3 and 4 to achieve a given bandpass. This is
    useful when SC2 is not in operation

    Input:

        wl_min: minimum wavelength in AA (float)
        wl_max: maximum wavelength in AA (float)
        d_MCo:  distance from disc1 to disc2 in meters
        (i.e to the opening disc of MC)
        d_SCc:  distance from disc1 to disc3 in meters
        (i.e to the closing disc of SC1)
        d_SCo:  distance from disc1 to disc4 in meters
        (i.e to the opening disc of SC1)
        freq:   the chopper frequency in Hertz (float)

    Output:

        [angle3, angle4]: a list containing the phases of discs 3 and 4, in
        degrees (float)
    """

    t_close_SC1 = (d_SCc - d_MCo) * wl_max / h_m
    t_open_SC1 = d_SCo * wl_min / h_m

    deg_per_sec = 360 * freq

    angle_3 = t_close_SC1 * deg_per_sec
    angle_4 = t_open_SC1 * deg_per_sec

    return [angle_3, angle_4]


def angles_SC2(wl_min=0,
               wl_max=18,
               d_MCo=chopper_pos[5],
               freq=10,
               ):
    # New sub added on 21.02.2022, already existing in chopper.py of
    # refsans_tools
    """
    Returns the phases of discs 5 and 6 to achieve a given bandpass

    Input:

        wl_min: minimum wavelength in AA (float)
        wl_max: maximum wavelength in AA (float)
        d_MCo:  distance from disc1 to disc2 in meters,
        i.e to the opening disc of MC (float)
        freq:   the chopper frequency in Hertz (float)

    Output:

        (angle5, angle6): a tuple containing the phases of discs 3 and 4,
        in degrees (float)

    """

    t_open = d_SC2 * wl_min / h_m
    t_close = (d_SC2 - d_MCo) * wl_max / h_m

    deg_per_sec = 360 * freq
    return (t_close * deg_per_sec, t_open * deg_per_sec)


def chopper_config(wl_min=0.0,
                   wl_max=20.0,
                   D=22.8,
                   disk2_pos=3,
                   delay=0,
                   SC2_mode='default',
                   SC2_full_open=240,
                   suppress_parasitic=True,
                   wl_stop=95.0,
                   gap=.1,
                   interface=True,
                   ):
    """
    Calculate the full chopper configuration

    Input:
        wl_min:             minimum desired wavelength in AA (float)
        wl_max:             maximum desired wavelength in AA (float)
        D:                  disc1 - detector distance in meters (float).
                            This is the beamline length, NOT the flightpath
        disk2_pos:          position of disk2 (1-6) (int)
        delay:              a time delay to use as an offset for the clock
                            (affects the apparent tof) (float)
        SC2_mode:           'default' (smart overlap): a new pulse reaches the
                                detector just after the previous one is
                                extinct, plus eventually a silence period set
                                by gap
                            'default_full_open': this mode behaves like
                                'default', but opening SC2 at the maximum
                                possible value. Note that this configuration
                                might produce frame overlap if the
                                disc1-detector distance is too large
                            'full_open': this mode behaves like
                                'default_full_open', but adjusts also the
                                disc1-detector distance to maximize the
                                intensity
                            'single_period': confines the spectrum to the first
                            chopper period
                            None: to remove SC2
        suppress_parasitic: if set to True, provided an optimized configuration
                            to suppress all the parasitic wavelengths (bool)
        wl_stop:            maximum value to check for the presence of
                            parasitic wavelengts, in AA (float). This parameter
                            is ignored if suppress_parasitic = False
        gap:                the fraction of a period which should be not
                            illuminated between frame end and next frame start.
                            This parameter only affects the 'default' and None
                            configurations (float)
        interface:          THIS PARAMETER IS NO LONGER USED BUT IS KEPT HERE
                            JUST IN CASE. Originarily it was used to force
                            the subroutine to return a dictionary which is
                            consistent with other subroutines existing in
                            NICOS

    Output:

        rpm:        chopper speed in rounds per minute, rounded to the closest
                    integer (float)
        angles:     list with angles for discs from 1 to 6, in degrees (float)
        disk2_Pos:  position of disk2 (1-6) (int). This position might differ
                    from the input. This happens especially when disk2_Pos = 6
                    and suppress_parasitic = True
                    because, in order to suppress parasitic bands, disk2 has to
                    be shifted in position 1. If disk2_Pos = 6 is returned in
                    the output, it means that the
                    old configuration, consisting in moving it to 300 degrees
                    and keeping it in any real position (1-5), does not
                    transmit any parasitic wavelength
        D:          disc1 - detector distance in meters (float). This value
                    might differ from the input, in case the 'full_open'
                    configuration as SC2_Mode is chosen
        wl_min:     minimum wavelength transmitted value of the configuration,
                    in AA (float). This value might differ from the input.
                    This may happens, for example, when
                    SC2_Mode = 'single_period' in some cases.
        wl_max:     maximum wavelength transmitted value of the configuration,
                    in AA (float). This value might differ from the input. This
                    happens, for example, when disk2_Pos = 6 and
                    suppress_parasitic = True in some cases.

        In case no working configurations are found, based on the input values,
        all the output variables are set to None
    """

    d_MCo = chopper_pos[disk2_pos]

    # in the new configuration discs 3 and 4 are at position  with a small gap
    # between the two (neglected)
    d_SCo = chopper_pos[SC1_Pos]
    d_SCc = chopper_pos[SC1_Pos]

    if SC2_mode is not None:
        SC2 = practical_SC2(wl_min=wl_min,
                            wl_max=wl_max,
                            D=D,
                            disk2_pos=disk2_pos,
                            SC2_full_open=SC2_full_open,
                            gap=gap
                            )[SC2_mode]
        D = SC2['D']
        freq = SC2['freq']
        angle_d56 = SC2['ang_SC2']

        wl_min_realised = SC2['wl_min_realised']
        rpm = SC2['rpm']
        deg_per_sec = 360 * freq

        # Slave closing, must be calculated not for wl_max but for:
        angle_SCc = d_SCc / d_SC2 * SC2['ang_SC2'][0]

        # idem for the opening
        angle_SCo = (d_SCo - d_MCo) / (d_SC2 - d_MCo) * SC2['ang_SC2'][1]

    else:
        SC2 = {
            'angles': None,
            'rpm': None,
            'freq': None,
            'wl_min_realised': None,
        }

        angle_d56 = (None, None)

        # NOTE: In the old version the following freq expression was commented
        # but it is nevertheless necessary in case we work without SC2
        freq = 1 / period(wl_min=wl_min,
                          wl_max=wl_max,
                          D=D * (1 + gap),
                          d_MCo=d_MCo)
        rpm = 60 * freq
        deg_per_sec = 360 * freq

        t_SCc = (d_SCc - d_MCo) * wl_max / h_m
        t_SCo = d_SCo * wl_min / h_m

        angle_SCc = deg_per_sec * t_SCc
        angle_SCo = deg_per_sec * t_SCo
        wl_min_realised = wl_min

    angles = [0, 0, angle_SCc, angle_SCo, angle_d56[0], angle_d56[1]]

    # The proper dictionary (cut if interface is True) is managed at the end of
    # this routine
    res = {
        'freq': freq,
        'rpm': rpm,
        'angles': angles,
        'delay_time': delay,
        'delay_angle': delay * freq * 360,
        'disk2_Pos': disk2_pos,
        'SC1_open_angle': angles[2] - angles[3],
        'SC1_phase': angles[3],
        'SC2_phase': angles[5],
        'wl_min': wl_min_realised,
        'wl_max': wl_max,
        'D': D,
        'gap': gap,
        'SC2_mode': SC2_mode
    }
    if SC2_mode is not None:
        res['SC2_open_angle'] = angles[4] - angles[5]

    # The routine checks if the configuration found produces frame overlap.
    # This is in particular critical if 'default_full_open'
    # is chosen, since this SC2_mode does not modify the beam line extension
    if SC2_mode == 'default_full_open':
        if res['D'] > practical_SC2(wl_min=wl_min, wl_max=wl_max, D=D,
                                    disk2_pos=disk2_pos,
                                    SC2_full_open=SC2_full_open,
                                    gap=gap)['full_open']['D']:
            return None, 6 * [None], None, None, None, None

    # The routine now optimizes the configuration to suppress eventual
    # parasitic neutrons. The optimization proceeds differently, depending on
    # whether disk2_pos = 6 or not. In the first case, disk2 is moved to
    # position 5, its phase is fixed at 300 deg, and eventual parasitic bands
    # are looked for. If they are found, disk2 is moved to position 1,
    # adjusting its phase to suppress the fastest neutrons of the first
    # parasitic band. If disk2 in not in virtual mode, the phases of discs 3
    # and 4 are adjusted to suppress all parasitic bands found, where possible.
    #
    if suppress_parasitic:

        if disk2_pos == 6:
            res['angles'][1] = 300
            # Sets the phase of disk2 to the Matthias standard value
            res['disk2_Pos'] = 5
            # Moves the disc in the position which has the minimum capability
            # to suppress parasitic neutrons

        # Check for parasitic bands, starting from 3 times wl_step "above"
        # wl_max (heuristic approach)
        parasitic_wl = chopper_parasitic(
            res, wl_start=wl_max + 3 *
            inspect.signature(chopper_parasitic).parameters['wl_step'].default,
            wl_stop=wl_stop)

        if len(parasitic_wl) > 0:

            if disk2_pos == 6:  # Optimization for disk2_pos = 6

                # Gets the minimum wavelength of the first parasitic wavelength
                # band
                if isinstance(parasitic_wl[0], list):
                    parasitic_wl = parasitic_wl[0][0]
                else:
                    parasitic_wl = parasitic_wl[0]

                # Gets the velocity of the fastest neutron of the first
                # parasitic wavelength band
                parasitic_vl = h_m / parasitic_wl  # velocity in m/s

                # The trajectory of a neutron with velocity parasitic_vl in a
                # distance/phase diagram has as equation:
                #
                # distance = parasitic_vl * T / 360 * (phase - phase_0)
                #
                # where T is the period and phase_0 is a constant which we
                # evaluate imposing that this neutrons cross the edge of
                # disc 3 when
                # it has a distance of d_SC1 from master disc.

                res['disk2_Pos'] = 1
                res['angles'][1] =\
                    360 * freq / parasitic_vl *\
                    (chopper_pos[res['disk2_Pos']] - d_SCc) +\
                    min(120.0, np.mod(res['angles'][2], 360))

                res['angles'][1] = np.mod(res['angles'][1], 360)

                # Since the phase of disk2 has been moved, we have to check
                # that the wl_max is really trasmitted from the new
                # configuration
                # Let us evaluate the phase of a neutron with wl_max when it is
                # at the new disk2_pos. The equation to be solved is
                #
                # distance = vl_max * T / 360 * (phase - phase_0)
                #
                # where, this time, we have to impose that the phase of the
                # neutron is null when it crosses SC1
                phase_at_disk2pos = np.mod(
                    360 * freq * wl_max / h_m *
                    (chopper_pos[res['disk2_Pos']] - d_SCc), 360)

                if phase_at_disk2pos < res['angles'][1]:
                    # The wl_max may not be provided. Evaluates the new value
                    # for wl_max
                    new_vl_max = (d_SC2 - chopper_pos[res['disk2_Pos']]) /\
                        (res['angles'][4] - res['angles'][1] + 360) * 360 *\
                        freq
                    wl_max_real = h_m / new_vl_max
                    res['wl_max'] = wl_max_real

            elif SC2_mode is not None:  # Optimization for disk2_pos < 6

                # In this case, since SC1 does not determine the wavelength
                # band, an analytic approach for solving the problem does not
                # work, since we should get a complete list of phases (at
                # Master Chopper position) through which the parasitic neutrons
                # of the various wavelengths pass (in a time / phase diagram).
                # The approach adopted is different: starting from the limit
                # situation in which the phases of SC1 pair define the wished
                # wavelength band (behaving like SC2) we relax the two phases
                # until a parasitic band is found

                # Let's start to check that no parasitic neutrons are
                # transmitted with this limit configuration. At this aim, we
                # create a temp variable res_bis with which we operate
                res_bis = copy.deepcopy(res)

                # The phases of discs 3 and 4 must lock the slowest and
                # fastest wavelengths
                new_ph = angles_SC1(wl_min=res['wl_min'],
                                    wl_max=res['wl_max'],
                                    d_MCo=chopper_pos[res['disk2_Pos']],
                                    freq=res['freq'],
                                    )

                res_bis['angles'][2] = new_ph[0]  # new phase disc3
                res_bis['angles'][3] = new_ph[1]  # new phase disc4

                # If this configuration is affected by parasitic neutrons,
                # the subroutine is stopped
                if len(chopper_parasitic(
                   res_bis, wl_start=wl_max + 3 * inspect.signature(
                       chopper_parasitic).parameters['wl_step'].default,
                   wl_stop=wl_stop)) != 0:
                    return None, 6 * [None], None, None, None, None

                else:
                    # No parasitic neutrons. Now the phases of discs 3 and 4
                    # are relaxed as much as possible

                    prec_phase = 0.005
                    # Precision of phase setting in degrees
                    # (it is actually 0.01 deg)

                    for i in range(3, 1, -1):
                        toll = abs(new_ph[i - 2] - res['angles'][i])

                        old_val = res['angles'][i]

                        while (toll >= prec_phase):

                            res_bis['angles'][i] = (new_ph[i - 2] + old_val) / 2
                            par_wl_bis = chopper_parasitic(
                                res_bis, wl_start=wl_max + 3 * inspect.signature(
                                    chopper_parasitic).parameters['wl_step'].default,
                                wl_stop=wl_stop)

                            if len(par_wl_bis) == 0:
                                # The new phase is acceptable
                                new_ph[i - 2] = res_bis['angles'][i]
                            else:
                                # We have to move in the direction of a
                                # restricted apertures
                                old_val = res_bis['angles'][i]

                            toll /= 2

                        res['angles'][i] = new_ph[i - 2]

            else:
                # SC2 does not exist and there are parasitic bands.
                # The routine is stopped
                return None, 6 * [None], None, None, None, None

            # Now we check that the current configuration does not produce
            # other parasitic bands. If the check fails, the routine is stopped
            parasitic_wl_new = chopper_parasitic(
                res, wl_start=res['wl_max'] + 3 * inspect.signature(
                    chopper_parasitic).parameters['wl_step'].default,
                wl_stop=wl_stop)
            if len(parasitic_wl_new) > 0:
                return None, 6 * [None], None, None, None, None

        else:
            # parasitic wavelengths have not been found. If this happens for
            # disk2_Pos = 6, this means that virtual_6 may be achieved for
            # every disk2_pos value
            if disk2_pos == 6:
                # Sets back the old values for disk2_pos and its phase
                res['disk2_Pos'] = 6
                # Sets the disc2 in the generic position 6
                res['angles'][1] = 0.0

    if interface:  # Removes the keys originarily not expected from Jens
        res.pop('freq', None)
        res.pop('delay_time', None)
        res.pop('delay_angle', None)
        res.pop('SC1_open_angle', None)
        res.pop('SC1_phase', None)
        res.pop('SC2_phase', None)
        res.pop('SC2_mode', None)

    if SC2_mode is not None:
        res['SC2_open_angle']: angles[4] - angles[5]

# OUTPUT
# 10.05.2021. In the previous version there was int(rpm) but it is better to
#             round the value before to make it integer. Here there is an
#             important change!!! As output a third paramater is provided:
#             disk2_Pos. This is not trivial because NICOS could need to move
#             the slave disc to a different position with respect to the
#             actual position.
# 22.02.2022. Three additional outputs (beam-line length, wl_min and wl_max)
#             have been added: these might be used by NICOS to check for
#             eventual frame overlap, as well as to display correctly the
#             minimum and maximum real wavelengths
    return int(round(rpm)), res['angles'], res['disk2_Pos'], res['D'],\
        res['wl_min'], res['wl_max']


def chopper_parasitic(res,
                      wl_start=25,
                      wl_stop=95,
                      wl_step=0.1,
                      deg_step=1.0,
                      ):

    """
    chopper_parasitic (res,
                     wl_start = 25,
                     wl_stop = 95,
                     wl_step = 0.1,
                     deg_step = 1.0):

    returns a list of wavelength-bands which are transmitted by the chopper
    system. This is particularly useful for verifying the presence of any
    parasitic bands transmitted

    Input:
        res:        output dictionary as rteturned by chopper_config. The
                    dictionary must contain, among others, the REAL phases of
                    discs 2-6 in degrees, their rotational speed in rounds per
                    minute, and the REAL position of disc2 (1-5)
        wl_start:   first wavelength to be checked for the transmission,
                    in AA (float)
        wl_stop:    last wavelength to be checked for the transmission,
                    in AA (float)
        wl_step:    wavelength step to be used for the check, in AA. The
                    wavelengths from wl_start to wl_stop with steps of wl_step
                    will be probed (float)
        deg_step:   step through the disc1 aperture to be probed, in degrees.
                    The program will check all the neutrons crossing the master
                    chopper from 240 deg to 360 deg phase, with steps defined
                    by deg_step (float)

    Output:
        wl_through: output list containing the wavelengths (in AA) which are
        able to be transmitted by the chopper system. The list is composed by
        sublist or single elements. A sublist contains the wl_min-wl_max of the
        interval transmitted. A single element represents a single (isolated)
        wavelength found: usually this means that the wavalengthband
        transmitted has a width comparable or smaller than wl_step or is
        transmitted through a narrow region of disc1, which is in extension
        comparable or smaller than deg_step

    """

    # The subroutine works in this way: for each wavelength, it starts from the
    # first frame and the master chopper, controlling all the possible phases
    # from 240 deg (the initial opening) up to 360 (when the master chopper
    # closes). For each phase, the path of the neutron is followed,  checking
    # if it crosses a closed disc during the flight. The discs 1 and 2 are
    # assumed to have a single aperture of 120 deg. Discs 3 and 4 are assumed
    # to have multiple apertures, as they have. In particular disc3 has four
    # apertures. If the edge of the beam closing is null, the apertures are
    # located:
    #
    # - between 213.0 deg and 217.0 deg
    # - between 223.5 deg and 226.5 deg
    # - between 234.0 deg and 236.0 deg
    # - between 240.0 deg and 360.0 deg (main aperture)
    #
    # Disc4 has also four apertures. If the edge of the beam opening is null,
    # the apertures are located:
    #
    # - between   0.0 deg and 120.0 deg (main aperture)
    # - between 153.0 deg and 157.0 deg
    # - between 164.0 deg and 166.0 deg
    # - between 173.5 deg and 176.5 deg
    #
    # Between the opening edge of disc3 (240 deg) and the opening edge of the
    # most distant slit (213.0 deg) there are 27 deg of "extension".
    # Analogously between the closing edge of disc4 (120 deg) and the closing
    # edge of the most distant slit (176.5 deg) there are 56.5 deg
    # of "extension".
    # Now it is possible to ignore the additional apertures located on the SC1
    # pair because the phase difference phi(disc3) - phi(disc4) may vary
    # between 0 deg and 120 deg, where the overlap between the discs goes
    # from 120 deg to 240 deg. In no cases this overlap goes below 83.5
    # deg = 27 deg + 56.5 deg  which is the critical value to not get neutrons
    # passing through the additional slits

    # Checks that the position of disc2 is not virtual, raising eventually an
    # error
    disk2_pos = res['disk2_Pos']

    if disk2_pos == 6:
        raise Exception('Error! A value indicating the REAL position of slave\
                         chopper has to be provided')

    if wl_stop < wl_start:
        raise Exception('Error! wl_stop might not be smaller than wl_start')

    # Array containing the phases from disc2 to disc6, in deg
    phase_arr = res['angles'][1:6]

    # Width of disc opaque regions (from 2 to 6)
    if (phase_arr[3] is None) and (phase_arr[4] is None):
        ch_deg = [240, 240, 240, 0, 0]  # SC2_Mode = None
    else:
        ch_deg = [240, 240, 240, 120, 120]

    # disc1-disc2 distance in millimeters for the current position
    d_MS = 1000 * chopper_pos[disk2_pos]

    # disc1-SC1 distance in millimeters
    d_SC1 = 1000 * chopper_pos[SC1_Pos]

    # distances (in millimeters) at which the phases for the neutrons of the
    # various wavelengths have to be calculated
    d_check = [d_MS, d_SC1, d_SC1, d_SC2 * 1e3, d_SC2 * 1e3]

    # Calculate the "forbidden" phases for discs from 2 to 6, for which
    # neutrons cannot be transmitted,
    phase_opaques = [None] * 5

    for i in range(0, 5, 2):
        # It operates on the phases of discs 2, 4, 6. The index i runs on the
        # elements of the phase_arr list
        if phase_arr[i] is not None:
            t = np.mod(phase_arr[i], 360)
            if t >= ch_deg[i]:
                phase_opaques[i] = [t - ch_deg[i], t, -np.inf, -np.inf]
            else:
                phase_opaques[i] = [0, t, t + 360 - ch_deg[i], 360]
        else:
            phase_opaques[i] = [-np.inf, -np.inf, -np.inf, -np.inf]

    for i in range(1, 5, 2):
        # It operates on the phases of discs 3 and 5. The index i runs on the
        # elements of the phase_arr list
        if phase_arr[i] is not None:
            t = np.mod(phase_arr[i], 360)
            if t < 360 - ch_deg[i]:
                phase_opaques[i] = [t, t + ch_deg[i], -np.inf, -np.inf]
            else:
                phase_opaques[i] = [0, t + ch_deg[i] - 360, t, 360]
        else:
            phase_opaques[i] = [-np.inf, -np.inf, -np.inf, -np.inf]

    wl_through = []
    # Contains the list of neutrons with transmitted wavelengths
    ph_through = []
    # Contains the list of the smallest possible phases of the transmitted
    # neutrons: this is useful for plotting

    per = 60000 / res['rpm']  # Duration of a period in milliseconds

    fact_ang = h_m * per / 360.0
    # factor to convert the wavelengths into phase velocity, in Å mm / deg

    if wl_start == 0:
        wl_start = wl_step

    wl = wl_start - wl_step
    n_checks = int(np.ceil((wl_stop - wl_start) / wl_step + 1))
    # Number of wavelengths to check
    nmax_grad = int(np.ceil((360 - ch_deg[0]) / deg_step + 1))
    # Maximum number of phases starting from disc 2 to check

    k_prev = -np.inf
    # k_prev is the previous value of k (index that runs over the various
    # wavelengths) for which the transmission of neutrons was found

    phase_min = -np.inf  # Minimum phase to be included in the ph_thorugh list

    for k in range(n_checks):

        wl += wl_step

        # It transforms the wavelength into phase velocity (i.e. how much angle
        # is swept per unit of time)
        vl_ang = fact_ang / wl
        # in mm / deg. This is the angular coefficient of the neutron's
        # trajectory on the phase / distance diagram

        # Now we need to check all the straight lines having this angular
        # coefficient and starting at any point from 240 to 360
        deg0 = ch_deg[0] - deg_step

        for j in range(nmax_grad):

            deg0 += deg_step

            # This trajectory has as equation: d = vl_ang * (phase - deg0).
            # We calculate the phase when d is corresponds to the position of
            # the various discs
            ierr = 0
            for i in range(5):
                phase_act = d_check[i] / vl_ang + deg0
                phase_red = np.mod(phase_act, 360)

                if (((phase_red >= phase_opaques[i][0]) and
                     (phase_red <= phase_opaques[i][1])) or
                    ((phase_red >= phase_opaques[i][2]) and
                     (phase_red <= phase_opaques[i][3]))):
                    ierr = 1  # Blocked neutron
                    break  # It is not necessary to verify the other discs

            if (ierr == 1) and (k == k_prev + 1) and (j == nmax_grad - 1):
                # The blocked neutron is the first appearing after a block of
                # transmitted neutrons
                if wl_through[-1][0] != wl - wl_step:
                    # It might be a bandwidth smaller than wl_step
                    wl_through[-1].append(wl - wl_step)
                    ph_through[-1].append(phase_min)

            elif (ierr == 0) and (k != k_prev + 1):
                # The transmitted neutron is the first appearing after a block
                # of blocked neutrons
                wl_through.append([wl])
                ph_through.append([deg0])
                k_prev = k
                break  # It is not necessary to verify the other phases

            elif (ierr == 0) and (k == k_prev + 1):
                # The passing neutron is in a block of transmitted neutrons
                k_prev = k
                phase_min = deg0
                if k == n_checks - 1:  # Last wavelength to be verified
                    wl_through[-1].append(wl)
                    ph_through[-1].append(deg0)

                break  # It is not necessary to verify the other phases

    return wl_through


def practical_SC2(wl_min=0,
                  wl_max=6,
                  D=22.8,
                  disk2_pos=3,
                  freq_max=100,
                  SC2_full_open=240.,
                  gap=.1
                  ):
    """
    Calculates the chopper frequency and SC2 angles to use, taking the maximum
    possible opening angle of SC2 into account. The calculations are performed
    for all the SC2_modes available in which the pair is used, namely
    'default', 'default_full_open', 'full_open, and 'single_period'

    Input:

        wl_min:     minimum desired wavelength in AA (float)
        wl_max:     maximum desired wavelength in AA (float)
        D:          disc1 - detector distance in meters (float). This is the
                    beamline length, NOT the flightpath
        disk2_pos:  position of disk2 (1-6) (int)
        freq_max:   the maximum allowed frequency of the chopper, in Hertz
                    (float). Parameter currently ignored
        gap:        the fraction of a period which should be not illuminated
                    between frame end and next frame start

    Output:

        a dict with different keys, including:
            'ang_SC2': list of angles for discs 5 and 6, in degrees (float)
            'rpm': chopper speed in rounds per minute (float)
            'freq': chopper frequency in Hertz (float)

        This dictionary also contains some input parameters

    """

    d_MCo = chopper_pos[disk2_pos]

    def angles(t_SCo, t_SCc, freq):

        """
        Returns a list with the angles (in degrees) of SC2 [angle(disc5),
        angle(disk6)] starting from the knowledge of the opening- and
        closing-times (in seconds) of the SC2 discs
        """

        ang_SC2 = np.array([t_SC2c, t_SC2o]) * freq * 360
        SC2_opening = ang_SC2[0] - ang_SC2[1]
        return ang_SC2, SC2_opening
        # was return s.mod(ang_SC2, 360), SC2_opening butr this can lead to
        # wrong order

    # convert maximum wavelength input in velocities (in meters per second)
    vel_min = h_m / wl_max

    # flight path (in meters) and wavelength resolution
    # never used flightpath = D - d_MCo * .5
    resol = chopper_pos[disk2_pos] * .5 / (D - chopper_pos[disk2_pos] * .5)

    dD = D - d_SC2

    # 'default' configuration uses the given the detector position
    tof_min = D * wl_min / h_m
    tof_max = (D - d_MCo) / vel_min

    # We want no neutron overlap, hence there must be at max one chopper period
    # between the slowest and fastest neutron
    d_tof = tof_max - tof_min
    t_SC2c = (d_SC2 - d_MCo) / vel_min
    t_SC2o = d_SC2 * wl_min / h_m

    per = d_tof * (1 + gap)
    freq = 1 / per
    rpm = freq * 60
    ang_SC2, SC2_opening = angles(t_SC2o, t_SC2c, freq)
    overlap = 0
    res = {
        't_SC2o': t_SC2o,
        't_SC2c': t_SC2c,
        'default': {
            'per': per,
            'freq': freq,
            'rpm': rpm,
            'ang_SC2': ang_SC2,
            'SC2_opening': SC2_opening,
            'D': D,
            'overlap': overlap,
            'resolution': resol,
            'disk2_pos': disk2_pos,
            'wl_min_realised': wl_min,
        }
    }
    # 'default_full_open' configuration uses the given detector position using
    # the full apertures of SC2. In this case the maximal opening is fixed
    # (as if we used a single disc) and we must adapt the frequency to the
    # opening
    per_default_full_open = (360. / SC2_full_open) * (t_SC2c - t_SC2o)
    freq_default_full_open = 1 / per_default_full_open
    rpm_default_full_open = freq_default_full_open * 60
    ang_SC2c = t_SC2c * 360 * freq_default_full_open
    ang_SC2o = t_SC2o * 360 * freq_default_full_open
    # Useful to avoid rounding off error
    ang_SC2_default_full_open = np.mod(np.array([ang_SC2c, ang_SC2o]), 360)

    overlap_default_full_open = (tof_max - tof_min) / per_default_full_open - 1
    res['default_full_open'] = {
        'per': per_default_full_open,
        'freq': freq_default_full_open,
        'rpm': rpm_default_full_open,
        'ang_SC2': ang_SC2_default_full_open,
        'SC2_opening': SC2_full_open,
        'D': D,
        'overlap': overlap_default_full_open,
        'resolution': resol,
        'disk2_pos': disk2_pos,
        'wl_min_realised': wl_min,
    }

    # now we check if the 'default' configuration calculated has a valid SC2
    # aperture, and correct if needed
    if res['default']['SC2_opening'] > SC2_full_open:
        res['default'].update(res['default_full_open'])

    # 'full_open' configuration uses, as 'default_full_open', the full aperture
    # of SC2 and, at the same time, adjust D to maximize the intensity
    # given the max opening of SC2 what is the minimal period from the open
    # period dT we calculate the rotation freq (deg/sec)
    dt_chopper = t_SC2c - t_SC2o
    per_chopper_full_open = dt_chopper * 360 / SC2_full_open
    freq_chopper_full_open = 1 / per_chopper_full_open
    rpm_chopper_full_open = freq_chopper_full_open * 60
    # from period and times calculate angles
    ang_SC2_chopper_full_open, SC2_opening = angles(t_SC2o,
                                                    t_SC2c,
                                                    freq_chopper_full_open)
    # and the corresponding distance disc1-detector to avoid overlap is
    D_chopper_full_open = (wl_max * d_MCo + h_m * per_chopper_full_open) /\
        (wl_max - wl_min)

    resol_adj_D =\
        chopper_pos[disk2_pos] * .5 /\
        (D_chopper_full_open - chopper_pos[disk2_pos] * .5)
    overlap_full_open = 0

    res['full_open'] = {
        'per': per_chopper_full_open,
        'freq': freq_chopper_full_open,
        'rpm': rpm_chopper_full_open,
        'ang_SC2': ang_SC2_chopper_full_open,
        'SC2_opening': SC2_opening,
        'D': D_chopper_full_open,
        'overlap': overlap_full_open,
        'resolution': resol_adj_D,
        'disk2_pos': disk2_pos,
        'wl_min_realised': wl_min,
    }

    # There is no overlap of different wl but the spectrum
    # might be spreading over two periods
    # never used nperiod_tof_min = int(tof_min / per)
    # never used nperiod_tof_max = int(tof_max / per)
    # print 'tmin is in per', nperiod_tof_min,
    # print 'tmax is in per', nperiod_tof_max
    # never used t1 = tof_max - per * (nperiod_tof_max)
    # never used t2 = tof_min - per * (nperiod_tof_min)
    # never used t3 = per
    # never used dt1 = nperiod_tof_min * per
    # never used dt2 = nperiod_tof_max * per

    # 'single_frame' configuration uses, as frame period, the travel time of
    # the slowest neutrons

    per_single_frame = tof_max
    freq_single_frame = 1 / per_single_frame
    rpm_single_frame = freq_single_frame * 60

    t_SC2c = tof_max - dD / vel_min
    t_SC2o = tof_min - dD * wl_min / h_m

    ang_SC2_single_frame, SC2_opening_single_frame = angles(t_SC2o,
                                                            t_SC2c,
                                                            freq_single_frame)
    # here overlap is actually underuse of the frames Setting the period of the
    # pulse equal to the time of flight of the slowest neutrons could result in
    # an opening of disks 5 and 6 such to exceed the maximum possible phase
    # difference, especially when a too short disk 1 - detector distance is
    # used: if this occurs, the wished minimum wavelength can not be provided
    # and it has to be increased (the maximum wavelength depends only on the
    # disk 1 - detector distance and therefore cannot be modified).

    if SC2_opening_single_frame > SC2_full_open:
        t_SC2o = t_SC2c - per_single_frame / (360 / SC2_full_open)
        ang_SC2_single_frame, SC2_opening_single_frame = \
            angles(t_SC2o, t_SC2c, freq_single_frame)

        wl_min_real = h_m * t_SC2o / d_SC2
        tof_min_single_frame = D * t_SC2o / d_SC2
    else:
        wl_min_real = wl_min
        tof_min_single_frame = tof_min

    overlap_single_frame = (tof_max - tof_min_single_frame) /\
        per_single_frame - 1
    res['single_frame'] = {
        'ang_SC2': ang_SC2_single_frame,
        'SC2_opening': SC2_opening_single_frame,
        'freq': freq_single_frame,
        'rpm': rpm_single_frame,
        'D': D,
        'overlap': overlap_single_frame,
        'resolution': resol,
        'disk2_pos': disk2_pos,
        'wl_min_realised': wl_min_real
    }

    # if freq > freq_max:
    #     raise ValueError('Maximal frequency exceeded... you might increase '
    #                      'bandwidth!')

    return res


def chopper_resolution(disk2_pos, D):
    """
    Returns the relative wavelength resolution in percentage

    Input:

        disk2_pos:  position of disk2 (1-6) (int)
        D:          disc1 - detector distance in meters (float). This is the
                    beamline length, NOT the flightpath

    Output:

        resol:  lambda resolution DeltaLambda/Lambda in percentage (float)

    """

    # Uncertainty affecting the flight path (should include half of detector
    # depth, which is neglected)
    uncert = chopper_pos[disk2_pos] / 2

    # Flight path
    flight_path = D - uncert

    # Resolution in percent
    resol = 100.0 * uncert / flight_path

    return round(resol, 3)
