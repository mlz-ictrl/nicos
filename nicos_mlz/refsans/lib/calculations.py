#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2022 by the NICOS contributors (see AUTHORS)
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
'''Chopper related devices.

ATTENTION: this set of subroutines has been heavily modified in on 10.05.2021
after integration of a new version of chopper.py in refsans_tools.
A line-to-line comparison with the old version is not easy
The following main changes have been done:

- A new routine (chopper_parasitic) has been added to calculates the parasitic
  wavelength bands transmitted. This routine may give, optionally, a
  time/distance diagram with the trajectory of the parasitic wavelength bands

- A flag in chopper_config (suppress_parasitic) which is normally set to True
  to optimize the   configuration when disk2_pos = 6. In this case an optimized
  configuration is returned to prevent the overlapping of slow neutrons in
  virtual_disk2_pos6. This is done by moving disk2 in pos 1 and adjusting
  its phase to cut the fastest neutrons of the first parasitic wavalength band
  which is potentially transmissible. This gives in some conditions
  (such as short D values) a value of wl_max which is smaller than the one
  desired Setting suppress_parasitic = False gives the old values, without
  optimization

- The distances of the instrument elements have been updated to the new values
  after a fully and deep revision of the beamline geometry operated
  by MH and GM

'''

import numpy as np
from scipy import constants

# Geometrical Parameters

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

# die Dicke des Detektors D900 ist bei Drift1 40mm und bei Drift2 65mm
# refsanssrv\docu\Instrument\Detektor+Elektronik\
# Detektor900 DNX-700 SeNr 2016-700-01\ImDetektor.pdf
# bezogen auf die length des MasterChopperst ergibt sich ein Fehler
#   65mm              90.9   38.7 21,3 10.0   5.0   2.8
Detectordepth = 65

h_m = constants.h / constants.m_n * 1e10
# Ratio between Planck constant and neutron mass in Å m /s


def bring_in_2pi(phase):  # New sub added on 10.05.2021
    # It moves a phase value 'phase' in deg, to the interval [0, 360]
    phase_scal = phase - (int(phase/360.0) - int(phase != 0) *
                          (1 - np.sign(phase))/2) * 360.0
    if (phase_scal == 360):
        phase_scal = 0

    return phase_scal


def period(wl_min=0, wl_max=18, D=22, d_MCo=chopper_pos[5]):
    # New sub added on 10.05.2021, already existing in chopper.py of
    # refsans_tools

    '''
    Optimal period of the chopper given the geometry and desired
    bandwidth

    Input :

        wl_min,wl_max : the wavelength limits in Angstrom (Floats)
        D             : the disc1-detector distance (m)(Float)
                        !! not flightpath !!
        d_MCo         : distance disc1 to master opening disc (m)
                        one can use the chopper_pos list to get real values

    Output :

        period        : the optimal chopper period (permanent detector
                        illumination) (s) (Float)
    '''

    # The optimal chopper period is such that the detector is always
    # illuminated. The fast neutrons leaving the MCo just catch up the slow
    # ones which have started from disc1 (MCc)

    v_max = h_m / wl_min
    v_min = h_m / wl_max

    return (D - d_MCo) / v_min - D / v_max


def chopper_config(wl_min=0,
                   wl_max=20,
                   D=22.8,
                   disk2_pos=3,  # NOTE: changed with respect to chopper.py
                   # from disc2_Pos ('k' instead of 'c') to maintain
                   # compatibility with the old versions from Jens (10.05.2021)
                   delay=0,
                   SC2_mode='default',
                   SC2_full_open=240,
                   suppress_parasitic=True,
                   gap=0.1,
                   interface=True
                   ):
    '''
    Calculate the full chopper configuration

    Input:
        wl_min:             minimum desired wavelength (Ang)
        wl_max:             maximum desired wavelength (Ang)
        D:                  beamline length (distance disc1-Detector).
                            This is NOT the flightpath (m)
        disk2_pos:          position of disk2, 1-6 (int)
        delay:              a time delay to use as an offset for the clock
                            (affects the apparent tof)
        SC2_mode:           'default' (smart overlap): a new pulse reaches the
                                detector just after the previous one is
                                extinct, plus eventually a silence period set
                                by gap
                            'default_full_open': this mode behaves like
                                'default', but opening SC2 at the maximum
                                possible value. Note that this configuration
                                might produce frame overlap if the
                                disk1-detector distance is too large
                            'full_open': this mode behaves like
                                'default_full_open', but adjusts also the
                                disk1-detector distance to maximize the
                                intensity
                            'single_period': confines the spectrum to the first
                                chopper period
                            None: to remove SC2
        suppress_parasitic: if set to true and if disc2_pos = 6, provided an
                            optimized configuration to suppress all the
                            parasitic wavelengths, moving the disc in pos 1 and
                            setting a phase to an appropriate value
        gap:                the fraction of a period which should be not
                            illuminated between frame end and next frame start

    Output:

        a dict with keys:
            'angles'        : (angles in deg for discs 1 to 6) (deg)
            'freq'          : chopper frequency (s-1)
            'rpm'           : chopper speed in rpm

        This dictionary also contains the input parameters
    '''

    # for display reasons
    if wl_min == 0:
        wl_min = 1e-5

    d_MCo = chopper_pos[disk2_pos]
    # in the new configuration discs 3 and 4 are at position  with a small gap
    # between the two (neglected)
    d_SCo = chopper_pos[SC1_Pos]
    d_SCc = chopper_pos[SC1_Pos]

    if SC2_mode is not None:
        res = practical_SC2(wl_min=wl_min,
                            wl_max=wl_max,
                            D=D,
                            disk2_pos=disk2_pos,
                            SC2_full_open=SC2_full_open,
                            gap=gap,
                            )
        SC2 = res[SC2_mode]
        D = SC2['D']
        freq = SC2['freq']
        angle_d56 = SC2['ang_SC2']

        # wl_min_realised = SC2['wl_min_realised']
        rpm = SC2['rpm']
        deg_per_sec = 360 * freq

        # Slave closing, must be calculated not for wl_max but for:
        v_wl_cut_min = d_SC2 / (SC2['ang_SC2'][0]/deg_per_sec)
        t_SCc = d_SCc / v_wl_cut_min
        angle_SCc = deg_per_sec * t_SCc

        # idem for the opening
        v_wl_cut_max = (d_SC2 - d_MCo) / (SC2['ang_SC2'][1]/deg_per_sec)
        t_SCo = (d_SCo - d_MCo) / v_wl_cut_max
        angle_SCo = deg_per_sec * t_SCo

    else:
        SC2 = {'angles':          None,
               'rpm':             None,
               'freq':            None,
               'wl_min_realised': None
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
        v_wl_cut_max = h_m / wl_max
        t_SCc = (d_SCc - d_MCo) / v_wl_cut_max
        v_wl_cut_min = h_m / wl_min
        t_SCo = d_SCo / v_wl_cut_min

        angle_SCc = deg_per_sec * t_SCc
        angle_SCo = deg_per_sec * t_SCo
        # wl_min_realised = wl_min

    angles = [0, 0, angle_SCc, angle_SCo, angle_d56[0], angle_d56[1]]

    # The proper dictionary (cut if interface is True) is managed at the end of
    # this routine

    res = {'freq':            freq,
           'rpm':             rpm,
           'angles':          angles,
           'delay_time':      delay,
           'delay_angle':     delay * freq * 360,
           'disk2_Pos':       disk2_pos,
           # NOTE: changed with respect to chopper.py from
           # disc2_Pos ('k' instead of 'c') to maintain compatibility with the
           # old versions from Jens
           'SC1_open_angle':  angles[2] - angles[3],
           'SC1_phase':       angles[3],
           'SC2_phase':       angles[5],
           'wl_min':          wl_min,
           'wl_max':          wl_max,
           'D':               D,
           'gap':             gap,
           'SC2_mode':        SC2_mode
           }

    if (disk2_pos == 6 and suppress_parasitic is True and
        SC2_mode is not None):
        # Optimizes the configuration to suppress the parasitic neutrons

        res['angles'][1] = 300
        # Sets the phase of disk2 to the Matthias' standard value
        res['disk2_Pos'] = 5
        # Sets the disk2 in the position which has the minimum capability to
        # suppress parasitic neutrons
        parasitic_wl = chopper_parasitic(res, wl_start=wl_max + 1)
        # Checks for parasitic neutrons from 1Å above wl_max
        # (euristic approach)

        if len(parasitic_wl) > 0:
            if isinstance(parasitic_wl[0], list):
                parasitic_wl = parasitic_wl[0][0]
                # Minimum wavelength of the first parasitic wavelength band
            else:
                parasitic_wl = parasitic_wl[0]
            # Gets the velocity of the fastest neutron of the first parasitic
            # wavelength band
            parasitic_vl = h_m / parasitic_wl  # velocity in m/s

            # The trajectory of a neutron with velocity parasitic_vl in
            # a distance/phase diagram has as equation:
            #
            #           distance = parasitic_vl * T / 360 * (phase - phase_0)
            #
            # where T is the period and phase_0 is a constant which we evaluate
            # imposing that this neutrons cross the edge of disc 3 or disc 4
            # when it has a distance of d_SC1 from master disk.

            res['disk2_Pos'] = 1
            res['angles'][1] = 360 * freq / parasitic_vl *\
                (chopper_pos[res['disk2_Pos']] - d_SCc) +\
                min(120.0, bring_in_2pi(res['angles'][2]))

            res['angles'][1] = bring_in_2pi(res['angles'][1])

            # Since the phase of disk2 has been moved, we have to check that
            # the wl_max is really mitted from the new configuration.
            # Let us evaluate the phase of the neutron with wl_max when it is
            # at the new disk2_pos. The equation to be solved is
            #
            #           distance = vl_max * T / 360 * (phase - phase_0)
            #
            # where, this time, we have to impose that the phase of the neutron
            # is null when it cross SC1
            phase_at_disk2pos = bring_in_2pi(
                360 * freq * wl_max / h_m * (
                    chopper_pos[res['disk2_Pos']] - d_SCc))

            if phase_at_disk2pos < res['angles'][1]:
                # The wl_max may not be provided. Evaluates the new value
                # for wl_max
                new_vl_max = (d_SC2 - chopper_pos[res['disk2_Pos']]) /\
                    (res['angles'][4] - res['angles'][1] + 360) * 360 * freq
                wl_max_real = h_m / new_vl_max
                res['wl_max'] = wl_max_real

            # Now we check that the current configuration does not produce
            # other parasitic bands. If the check fails, the program gives
            # the settings valid for disk2_pos = 5, which is the closest
            # possible configuration to be achieved
            parasitic_wl_new = chopper_parasitic(res, wl_start=res['wl_max']+1)
            if len(parasitic_wl_new) > 0:
                # The optimized found configuration may not be used. We give
                # the values for disk2_pos = 5. We use a recursivity for
                # chopper_config, but this should not give rise to problems,
                # since for disk2_pos we don't use 6
                rpm_pos5, angles_pos5, disk2_pos_5 =\
                    chopper_config(wl_min=wl_min, wl_max=wl_max, D=D,
                                   disk2_pos=5, delay=delay, SC2_mode=SC2_mode,
                                   SC2_full_open=SC2_full_open,
                                   suppress_parasitic=False, gap=gap,
                                   interface=True)

                return rpm_pos5, angles_pos5, disk2_pos_5  # Exits from the sub

        else:
            # parasitic wavelengths have not been found. This means that
            # virtual_6 may be achieved for every disc2_pos value
            res['disk2_Pos'] = 6
            # Differently from chopper_config, which in this case returns also
            # a null phase for disk2, this routine gives back the Matthias'
            # standard value (300 deg)

    elif (disk2_pos == 6 and suppress_parasitic is False and
          SC2_mode is not None):
        # No optimization requested. This corresponds to the 'dirty beam'
        # configuration, in which disk2 is not moved and its phase is set
        # to 300 deg
        res['angles'][1] = 300
        res['disk2_Pos'] = 6

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

    return int(round(rpm)), res['angles'], res['disk2_Pos']
    # 10.05.2021. In the previous version there was int(rpm) but it is better
    # to round the value before to make it integer
    # Here there is an important change!!! As output a third paramater is
    # provided: disk2_Pos. This is not trivial because NICOS could need to move
    # the slave disc to a different position with respect to the actual
    # position.


def chopper_parasitic(res,
                      wl_start=25,
                      wl_stop=95,
                      wl_step=0.1,
                      deg_step=1.0):

    '''
    chopper_parasitic (res,
                     wl_start=25,
                     wl_stop=95,
                     wl_step=0.1,
                     deg_step = 1.0)

    returns a list of wavelength-bands which are transmitted by the chopper
    system. This is particularly useful for verifying the presence of any
    parasitic bands transmitted

    res:        output dictionary given by chopper_config. The dictionary
                contains, among others, the real phases of disks 2-6 in deg,
                their rotational speed in rounds per minute, and the REAL
                position of disk 2 (1-5)
    wl_start:   first wavelength to be checked for the transmission, in Å
    wl_stop:    last wavelength to be checked for the transmission, in Å
    wl_step:    wavelength step to be used for the check, in Å. The wavelengths
                from wl_start to wl_stop with steps of wl_step will be probed
    deg_step:   degree step thorugh the disk1 aperture to be probed. The
                program will check all the neutrons crossing the master chopper
                from 240 deg to 360 deg phase, with steps defined by deg_step.
    wl_through: output list containing the wavelengths which are able to
                betransmitted by the chopper system
    '''

    # The subroutine works in this way: for each wavelength, it starts from
    # the first frame and the master chopper, controlling all the possible
    # phases from 240 deg (the initial opening) up to 360 (when the master
    # chopper closes). For each phase, the path of the neutron is followed,
    # checking if it crosses a closed disk during the flight.
    #
    # Checks that the position of disk2 is not virtual, raising eventually an
    # error
    disk2_pos = res['disk2_Pos']

    if disk2_pos == 6:
        raise Exception('Error! A value indicating the REAL position of slave\
             chopper has to be provided')

    # Array containing the phases from disk2 to disk6, in deg
    phase_arr = res['angles'][1:6]

    # Width of disc locks (from 2 to 6)
    if (phase_arr[3] is None) and (phase_arr[4] is None):
        ch_deg = [240, 240, 240, 0, 0]  # SC2_Mode = None
        phase_arr[3] = 0
        phase_arr[4] = 0
    else:
        ch_deg = [240, 240, 240, 120, 120]

    # disk1-disk2 distance in millimeters for the current position
    d_MS = 1000 * chopper_pos[disk2_pos]

    # disk1-SC1 distance in millimeters
    d_SC1 = 1000 * chopper_pos[SC1_Pos]

    # distances (in millimeters) at which the phases for the neutrons of the
    # various wavelengths have to be calculated
    d_check = [d_MS, d_SC1, d_SC1, d_SC2 * 1e3, d_SC2 * 1e3]

    # Calculate the 'forbidden' phases for disks from 2 to 6,
    # for which neutrons cannot be transmitted,
    phase_opaques = [None] * 5

    for i in range(0, 5, 2):
        # It operates on the phases of disks 2, 4, 6.
        # The index i runs on the elements of the phase_opaques list
        t = bring_in_2pi(phase_arr[i])
        if (t >= ch_deg[i]):
            phase_opaques[i] = [t-ch_deg[i], t, -np.inf, -np.inf]
        else:
            phase_opaques[i] = [0, t, t + 360 - ch_deg[i], 360]

    for i in range(1, 5, 2):
        # It operates on the phases of disks 3 and 5.
        # The index i runs on the elements of the phase_opaques list
        t = bring_in_2pi(phase_arr[i])
        if (t < 360 - ch_deg[i]):
            phase_opaques[i] = [t, t + ch_deg[i], -np.inf, -np.inf]
        else:
            phase_opaques[i] = [0, t + ch_deg[i] - 360, t, 360]

    wl_through = []
    # Contains the list of neutrons with transmitted wavelengths
    ph_through = []
    # Contains the list of the smallest possible phases of the transmitted
    # neutrons: this is useful for plotting

    per = 60000 / res['rpm']
    # Duration of a period in milliseconds

    fact_ang = h_m * per / 360.0
    # factor to convert the wavelengths into phase velocity, in Å mm / deg

    if (wl_start == 0):
        wl_start = wl_step

    wl = wl_start - wl_step
    n_checks = int(np.ceil((wl_stop - wl_start) / wl_step + 1))
    # Number of wavelengths to check
    nmax_grad = int(np.ceil((360 - ch_deg[0]) / deg_step + 1))
    # Maximum number of phases starting from disk 2 to check

    k_prev = -np.inf  # k_prev is the previous value of k
    # (index that runs over the various wavelengths) for which the transmission
    # of neutrons was found

    phase_min = -np.inf  # Minimum phase to be included in the ph_thorugh list

    for k in range(n_checks):

        wl += wl_step

        # It transforms the wavelength into phase velocity
        # (i.e. how much angle is swept per unit of time)
        vl_ang = fact_ang / wl  # in mm / deg. This is the angular coefficient
        # of the neutron's trajectory on the phase / distance diagram

        # Now we need to check all the straight lines having this angular
        # coefficient and starting at any point from 240 to 360
        deg0 = ch_deg[0] - deg_step

        for j in range(nmax_grad):

            deg0 += deg_step

            # This trajectory has as equation: d = vl_ang * (phase - deg0).
            # We calculate the phase when d is corresponds to the position of
            # the various disks
            ierr = 0
            for i in range(5):
                phase_act = d_check[i]/vl_ang + deg0
                phase_red = bring_in_2pi(phase_act)

                if (phase_opaques[i][0] <= phase_red <= phase_opaques[i][1] or
                    phase_opaques[i][2] <= phase_red <= phase_opaques[i][3]):
                    ierr = 1  # Blocked neutron
                    break  # It is not necessary to verify the other disks

            if ((ierr == 1) and (k == k_prev + 1) and (j == nmax_grad - 1)):
                # The blocked neutron is the first appearing after a block of
                # transmitted neutrons
                if (wl_through[-1][0] != wl-wl_step):
                    # It might be a bandwidth smaller than wl_step
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


def practical_SC2(wl_min=0,
                  wl_max=6,
                  D=22.8,
                  disk2_pos=3,  # NOTE: changed with respect to chopper.py
                  # from disc2_Pos ('k' instead of 'c') to maintain
                  # compatibility with the old versions from Jens
                  SC2_mode='default',
                  freq_max=100,
                  SC2_full_open=240.,
                  gap=.1
                  ):
    '''
    calculate the chopper frequency and SC2 angles to use taking the max open
    angle of SC2  into account

    Input:

        wl_min:     minimum desired wavelength (Ang)
        wl_max:     maximmum desired wavelength (Ang)
        D:          beamline length (!!! from first disc to detector.
                    This is NOT flight_path0 !!!) (m)
        d_MCo:      dist from disc1 to the opening disc for the master (d2) (m)
        d_SC2:      distance from disc1 to SC2 (should not change...) (m)
        freq_max:   the maximum allowed frequency of the chopper
        gap: the    fraction of a period which should be not illuminated
                    between frame end and next frame start

    Output:

        a dict with keys:
            'angles'        : (angles in deg for discs 2 to 6) (deg)
            'rpm'           : chopper speed in rpm
            'freq'          : chopper frequency (s-1)
    '''
    d_MCo = chopper_pos[disk2_pos]

    def angles(t_SCo, t_SCc, freq):
        ang_SC2 = np.array([t_SC2c, t_SC2o]) * freq * 360
        SC2_opening = ang_SC2[0] - ang_SC2[1]
        return ang_SC2, SC2_opening

    vel_max = h_m / wl_min
    vel_min = h_m / wl_max

    # lambda resolution
    resol = chopper_resolution(disk2_pos, D)

    dD = D - d_SC2

    # default configuration uses the given the detector position
    tof_min = D / vel_max
    tof_max = (D - d_MCo) / vel_min

    # We want no neutron overlap, hence there must be at max one
    # chopper period between the slowest and fastest neutron

    d_tof = tof_max - tof_min
    t_SC2c = (d_SC2 - d_MCo) / vel_min

    if wl_min > 0:
        t_SC2o = d_SC2 / vel_max
    else:
        t_SC2o = 0

    per = d_tof * (1.0 + gap)
    freq = 1.0 / per
    rpm = freq * 60
    ang_SC2, SC2_opening = angles(t_SC2o, t_SC2c, freq)
    overlap = 0
    res = {
           't_SC2o':    t_SC2o,
           't_SC2c':    t_SC2c,
           'default': {
                        'per':          per,
                        'freq':         freq,
                        'rpm':          rpm,
                        'ang_SC2':      ang_SC2,
                        'SC2_opening':  SC2_opening,
                        'D':            D,
                        'overlap':      overlap,
                        'resolution':   resol,
                        'disk2_Pos':    disk2_pos,
                       }
           }
    # if the maximal opening of the chopper is not tunable (single disc for
    # instance) we must adapt the frequency to the opening
    per_default_full_open = (360. / SC2_full_open) * (t_SC2c - t_SC2o)
    freq_default_full_open = 1. / per_default_full_open
    rpm_default_full_open = freq_default_full_open * 60
    ang_SC2c = t_SC2c * 360.0 * freq_default_full_open
    ang_SC2_default_full_open = np.mod(np.array([ang_SC2c,
                                                 ang_SC2c - SC2_full_open]),
                                       360)
    overlap_default_full_open = (tof_max - tof_min) / per_default_full_open - 1
    res['default_full_open'] = {
                                'per':          per_default_full_open,
                                'freq':         freq_default_full_open,
                                'rpm':          rpm_default_full_open,
                                'ang_SC2':      ang_SC2_default_full_open,
                                'SC2_opening':  SC2_full_open,
                                'D':            D,
                                'overlap':      overlap_default_full_open,
                                'resolution':   resol,
                                'disk2_Pos':    disk2_pos,
                                }

    # now we check if the default calculated before are valid and correct if
    # needed
    if res['default']['SC2_opening'] > SC2_full_open:
        res['default'].update(res['default_full_open'])

    # another possibility is to open SC2 as much as possible and
    # adjust D
    # given the max opening of SC2 what is the minimal period
    # from the open period dT we calculate the rotation freq (deg/sec)
    dt_chopper = t_SC2c - t_SC2o
    per_chopper_full_open = dt_chopper * 360 / SC2_full_open
    freq_chopper_full_open = 1 / per_chopper_full_open
    rpm_chopper_full_open = freq_chopper_full_open * 60
    # from period and times calculate angles
    ang_SC2_chopper_full_open, SC2_opening = angles(t_SC2o,
                                                    t_SC2c,
                                                    freq_chopper_full_open)
    # and the corresponding distance disc1-detector to avoid overlap
    # the time for intersection of the fast and slow neutrons is
    t = (d_MCo + vel_max * per_chopper_full_open) / (vel_max - vel_min)
    # and the corresponding distance
    D_chopper_full_open = vel_max * (t - per_chopper_full_open)
    resol_adj_D = chopper_pos[disk2_pos] * .5 / (D_chopper_full_open -
                                                 chopper_pos[disk2_pos] * .5)
    overlap_full_open = 0

    res['full_open'] = {
                        'per':          per_chopper_full_open,
                        'freq':          freq_chopper_full_open,
                        'rpm':           rpm_chopper_full_open,
                        'ang_SC2':       ang_SC2_chopper_full_open,
                        'SC2_opening':   SC2_opening,
                        'D':             D_chopper_full_open,
                        'overlap':       overlap_full_open,
                        'resolution':    resol_adj_D,
                        'disk2_Pos':     disk2_pos,
                        }

    # There is no overlap of different wl but the spectrum
    # might be spreading over two periods
    # nperiod_tof_min = int(tof_min/per)
    # nperiod_tof_max = int(tof_max/per)
    # print 'tmin is in per', nperiod_tof_min,
    # print 'tmax is in per', nperiod_tof_max
    # t1 = tof_max - per * (nperiod_tof_max)
    # t2 = tof_min - per * (nperiod_tof_min)
    # t3 = per
    # dt1 = nperiod_tof_min * per
    # dt2 = nperiod_tof_max * per

    per_single_frame = tof_max
    freq_single_frame = 1 / per_single_frame
    rpm_single_frame = freq_single_frame * 60

    t_SC2c = tof_max - dD / vel_min
    t_SC2o_desired = tof_min - dD / vel_max

    t_SC2o = t_SC2o_desired if wl_min > 0 else 0

    ang_SC2_single_frame, SC2_opening_single_frame = angles(t_SC2o,
                                                            t_SC2c,
                                                            freq_single_frame)
    # here overlap is actually underuse of the frames
    overlap_single_frame = (tof_max - tof_min) / per_single_frame - 1
    res['single_frame'] = {'ang_SC2':          ang_SC2_single_frame,
                           'SC2_opening':      SC2_opening_single_frame,
                           'freq':             freq_single_frame,
                           'rpm':              rpm_single_frame,
                           'D':                D,
                           'overlap':          overlap_single_frame,
                           'resolution':       resol,
                           'disk2_Pos':        disk2_pos
                           }

# if freq > freq_max:
#    raise ValueError('Maximal frequency exceeded...
#        you might increase bandwidth!')

    min_t_SC2o = t_SC2c - per_single_frame / (360 / SC2_full_open)
    if t_SC2o < min_t_SC2o:
        t_SC2o = min_t_SC2o
        wl_min_real = h_m * t_SC2o / d_SC2
        print('Minimum wavelength cannot be satisfied, you get %s' %
              round(wl_min_real, 2))
    else:
        wl_min_real = wl_min

    for mode in ['default', 'default_full_open', 'full_open', 'single_frame']:
        res[mode]['wl_min_realised'] = wl_min_real

    return res


def chopper_resolution(disk2_pos, D):
    '''

    Returns the lambda resolution in percentage

    chopper2_pos: disk2 position (1-6)
    D: disk1-detector distance, in meters. This is not the flight path!!
    resol: Wavelength resolution in percent (%)
    '''

    # Uncertainty affecting the flight path
    uncert = chopper_pos[disk2_pos] / 2  # + Detectordepthh / 2

    # Flight path
    flight_path = D - uncert  # + Detectordepth / 2

    # Uncertainty and flight_path should include half of Detectordepth
    resol = 100.0 * uncert / flight_path

    return round(resol, 3)
