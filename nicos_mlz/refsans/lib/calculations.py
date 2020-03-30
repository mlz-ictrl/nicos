#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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
from scipy import constants

chopper_pos = [None, .0715, 0.168, 0.305, 0.651, 1.296, 2.33]  # in m

# distance from disk1 to SC2 (should not change...) (m)
d_SC2 = 10.61
# SC1_Pos is the distance from disk 1 to SC1 which is now fixed at pos 6
SC1_Pos = 6
# horizontal distance from first chopper disc (position) to pivot point 0 in mm
pre_sample_path = 11028

# die Dicke des Detektors D900 ist bei Drift1 40mm und bei Drift2 65mm
# refsanssrv\docu\Instrument\Detektor+Elektronik\
# Detektor900 DNX-700 SeNr 2016-700-01\ImDetektor.pdf
# bezogen auf die length des MasterChopperst ergibt sich ein Fehler
#   65mm              90.9   38.7 21,3 10.0   5.0   2.8
Detectordepth = 65

h = constants.value('Planck constant')
mn = constants.value('neutron mass')


def chopper_config(wl_min=0,
                   wl_max=20,
                   D=22.8,
                   disk2_pos=3,
                   delay=0,
                   SC2_mode='default',
                   SC2_full_open=240,
                   gap=.1,
                   interface=True,
                   ):
    """
    Calculate the full chopper configuration.

    Input:
        wl_min    : minimum desired wavelength (Ang)
        wl_max    : maximmum desired wavelength (Ang)
        D         : beamline length (distance disk1-Detector
                     not flightpath)(m)
        disk2_pos : position of disk2 (int)
        delay     : a time delay to use as an offset for the clock
                    (affects the apparent tof)
        SC2_mode  : 'smart' (use smart overlap) OR 'single_period'
                    (confines the spectrum to the first chopper period)
                    OR None to remove SC2.
        gap       : the fraction of a period which should be not
                    illuminated between frame end and next frame start

    Output:

        a dict with keys:
            'angles'        : (angles in deg for disks 1 to 6) (deg)
            'freq'          : chopper frequency (s-1)
            'rpm'           : chopper speed in rpm

        This dictionary also contains the input parameters
    """
    # fixme todo ###
    # params --

    # for display reasons
    if wl_min == 0:
        wl_min = 1e-5

    d_MCo = chopper_pos[disk2_pos]
    # in the new configuration disks 3 and 4 are at position with a small
    # gap between the two (neglected)
    d_SCo = chopper_pos[SC1_Pos]
    d_SCc = chopper_pos[SC1_Pos]

    if SC2_mode is not None:
        res = practical_SC2(wl_min=wl_min,
                            wl_max=wl_max,
                            D=D,
                            disk2_pos=disk2_pos,
                            SC2_full_open=SC2_full_open,
                            gap=gap
                            )
        SC2 = res[SC2_mode]
        D = SC2['D']
        freq = SC2['freq']
        angle_d56 = SC2['ang_SC2']

        # wl_min_realised = SC2['wl_min_realised']
        rpm = SC2['rpm']
        deg_per_sec = 360 * freq

        # Slave closing, must be calculated  not for wl_max but for:
        v_wl_cut_min = d_SC2 / (SC2['ang_SC2'][0] / deg_per_sec)
        t_SCc = d_SCc / v_wl_cut_min
        angle_SCc = deg_per_sec * t_SCc

        # idem for the opening
        v_wl_cut_max = (d_SC2 - d_MCo) / (SC2['ang_SC2'][1] / deg_per_sec)
        t_SCo = (d_SCo - d_MCo) / v_wl_cut_max
        angle_SCo = deg_per_sec * t_SCo
    else:
        SC2 = {'angles': None,
               'rpm': None,
               'freq': None,
               'wl_min_realised': None
               }

        angle_d56 = (None, None)
        # flake8
        # TODO: function period definition (J.K.)
        # freq = 1 / period(wl_min=wl_min,
        #                   wl_max=wl_max,
        #                   D=D * (1 + gap),
        #                   d_MCo=d_MCo)
        rpm = 60 * freq
        deg_per_sec = 360 * freq
        v_wl_cut_max = neutron_wavelength2vel(wl_max * 1e-10)
        t_SCc = (d_SCc - d_MCo) / v_wl_cut_max
        v_wl_cut_min = neutron_wavelength2vel(wl_min * 1e-10)
        t_SCo = d_SCo / v_wl_cut_min

        angle_SCc = deg_per_sec * t_SCc
        angle_SCo = deg_per_sec * t_SCo

    angles = [0, 0, angle_SCc, angle_SCo, angle_d56[0], angle_d56[1]]

    if disk2_pos == 6:
        # log.info('virtual 6 MP')
        angles[1] = 300

    if interface:
        res = {'rpm': rpm,
               'angles': angles,
               # 'freq': freq,
               # 'delay_time': delay,
               # 'delay_angle': delay * freq * 360,
               'disk2_Pos': disk2_pos,
               # 'SC1_open_angle': angles[2] - angles[3],
               # 'SC1_phase': angles[3],
               # 'SC2_phase': angles[5],
               'wl_min': wl_min,
               'wl_max': wl_max,
               'D': D,
               'gap': gap,
               # 'SC2_mode': SC2_mode,
               }
    else:
        res = {'freq': freq,
               'rpm': rpm,
               'angles': angles,
               'delay_time': delay,
               'delay_angle': delay * freq * 360,
               'disk2_Pos': disk2_pos,
               'SC1_open_angle': angles[2] - angles[3],
               'SC1_phase': angles[3],
               'SC2_phase': angles[5],
               'wl_min': wl_min,
               'wl_max': wl_max,
               'D': D,
               'gap': gap,
               'SC2_mode': SC2_mode,
               }
    if SC2_mode is not None:
        res['SC2_open_angle'] = angles[4] - angles[5]
    return int(rpm), angles


def practical_SC2(wl_min=0,
                  wl_max=6,
                  D=22.8,
                  disk2_pos=3,
                  SC2_mode='default',
                  freq_max=100,
                  SC2_full_open=240.,
                  gap=.1
                  ):
    """
    calculate the chopper frequency and SC2 angles to use taking the
      max open angle of SC2  into account

    Input:

        wl_min   : minimum desired wavelength (Ang)
        wl_max   : maximmum desired wavelength (Ang)
        D        : beamline length (!!! from first disk to detector.
                   This is NOT flight_path0 !!!) (m)
        freq_max : the maximum allowed frequency of the chopper
        gap      : the fraction of a period which should be not
                   illuminated between frame end and next frame start

    Output:

        a dict with keys:
            'angles'        : (angles in deg for disks 2 to 6) (deg)
            'rpm'           : chopper speed in rpm
            'freq'          : chopper frequency (s-1)

    """

    d_MCo = chopper_pos[disk2_pos]

    def angles(t_SCo, t_SCc, freq):
        ang_SC2 = np.array([t_SC2c, t_SC2o]) * freq * 360
        SC2_opening = ang_SC2[0] - ang_SC2[1]
        return ang_SC2, SC2_opening

    # convert wavelength input in Angstrom to m
    wl_min *= 1e-10
    wl_max *= 1e-10

    vel_max = neutron_wavelength2vel(wl_min)
    vel_min = neutron_wavelength2vel(wl_max)

    # flight path
    # flightpath = D - d_MCo * .5  # TODO: Never used (J.K.)
    resol = chopper_pos[disk2_pos] / 2. / (D - chopper_pos[disk2_pos] / 2.)

    dD = D - d_SC2

    # default configuration uses the given the detector position
    tof_min = D / vel_max
    tof_max = (D - d_MCo) / vel_min

    # We want no neutron overlap, hence there must be at max one
    # chopper period between the slowest and fastest neutron

    d_tof = tof_max - tof_min
    t_SC2c = (d_SC2 - d_MCo) / vel_min

    t_SC2o = d_SC2 / vel_max if wl_min > 0 else 0

    per = d_tof * (1 + gap)
    freq = 1. / per
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
            'disk2_pos': disk2_pos
        },
    }
    # if the maximal opening of the chopper is not tunable (single disk for
    # instance) we must adapt the frequency to the opening
    per_default_full_open = (360. / SC2_full_open) * (t_SC2c - t_SC2o)
    freq_default_full_open = 1 / per_default_full_open
    rpm_default_full_open = freq_default_full_open * 60
    ang_SC2c = t_SC2c * 360 * freq_default_full_open
    ang_SC2_default_full_open = np.mod(np.array([ang_SC2c,
                                                 ang_SC2c - SC2_full_open]),
                                       360)

    # log.debug('ang_SC2c %s', ang_SC2c)
    # log.debug('ang_SC2c - SC2_full_open %s', (ang_SC2c - SC2_full_open))
    # log.debug('ang_SC2_default_full_open %s', ang_SC2_default_full_open)
    # log.debug('replace p')

    overlap_default_full_open = (tof_max - tof_min) /\
        per_default_full_open - 1
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
    }

    # now we check if the default calculated before are valid and correct
    # if needed
    if res['default']['SC2_opening'] > SC2_full_open:
        res["default"].update(res['default_full_open'])

    # another possibility is to open SC2 as much as possible and
    # adjust D
    # given the max opening of SC2 what is the minimal period
    # from the open period dT we calculate the rotation freq (deg/sec)
    dt_chopper = t_SC2c - t_SC2o
    per_chopper_full_open = dt_chopper * 360 / SC2_full_open
    freq_chopper_full_open = 1 / per_chopper_full_open
    rpm_chopper_full_open = freq_chopper_full_open * 60
    # from period and times calculate angles
    ang_SC2_chopper_full_open, SC2_opening = angles(
        t_SC2o, t_SC2c, freq_chopper_full_open)
    # and the corresponding distance disk1-detector to avoid overlap
    # the time for intersection of the fast and slow neutrons is
    t = (d_MCo + vel_max * per_chopper_full_open) / (vel_max - vel_min)
    # and the corresponding distance
    D_chopper_full_open = vel_max * (t - per_chopper_full_open)
    resol_adj_D = chopper_pos[disk2_pos] * .5 / (
        D_chopper_full_open - chopper_pos[disk2_pos] * .5)
    overlap_full_open = 0

    res['full_open'] = {'per': per_chopper_full_open,
                        'freq': freq_chopper_full_open,
                        'rpm': rpm_chopper_full_open,
                        'ang_SC2': ang_SC2_chopper_full_open,
                        'SC2_opening': SC2_opening,
                        'D': D_chopper_full_open,
                        'overlap': overlap_full_open,
                        'resolution': resol_adj_D,
                        'disk2_pos': disk2_pos
                        }

    # ++  flake8 assigned to but never used
    # There is no overlap of different wl but the spectrum
    # might be spreading over two periods
    # nperiod_tof_min = int(tof_min/per)
    # nperiod_tof_max = int(tof_max/per)
    # print('tmin is in per', nperiod_tof_min)
    # print('tmax is in per', nperiod_tof_max)
    # t1 = tof_max - per * (nperiod_tof_max)
    # t2 = tof_min - per * (nperiod_tof_min)
    # t3 = per
    # dt1 = nperiod_tof_min * per
    # dt2 = nperiod_tof_max * per
    # --

    per_single_frame = tof_max
    freq_single_frame = 1 / per_single_frame
    rpm_single_frame = freq_single_frame * 60

    t_SC2c = tof_max - dD / vel_min
    t_SC2o_desired = tof_min - dD / vel_max

    t_SC2o = t_SC2o_desired if wl_min > 0 else 0

    ang_SC2_single_frame, SC2_opening_single_frame =\
        angles(t_SC2o, t_SC2c, freq_single_frame)
    # here overlap is actually underuse of the frames
    overlap_single_frame = (tof_max - tof_min) / per_single_frame - 1
    res['single_frame'] = {'ang_SC2': ang_SC2_single_frame,
                           'SC2_opening': SC2_opening_single_frame,
                           'freq': freq_single_frame,
                           'rpm': rpm_single_frame,
                           'D': D,
                           'overlap': overlap_single_frame,
                           'resolution': resol,
                           'disk2_pos': disk2_pos
                           }

    # if freq > freq_max:
    #     raise ValueError('Maximal frequency exceeded...' +
    #        'you might increase bandwidth!')
    #
    min_t_SC2o = t_SC2c - per_single_frame / (360 / SC2_full_open)
    if t_SC2o < min_t_SC2o:
        t_SC2o = min_t_SC2o
        wl_min_real = neutron_vel2wavelength(d_SC2 / t_SC2o) * 1e10
        print('Minimum wavelength cannot be satisfied, you get %s' %
              wl_min_real)
    else:
        wl_min_real = wl_min * 1e10

    for mode in ['default', 'default_full_open', 'full_open',
                 'single_frame']:
        res[mode]['wl_min_realised'] = wl_min_real

    return res


# TODO: Never used, remove or add parameter d_SC2 (J.K.)
def calc_wl(rpm,
            angles,
            d_MCo=None,
            d_SCo=None,
            d_SCc=None,
            # d_SC2=d_SC2,
            freq=None):

    if d_MCo is None:
        d_MCo = chopper_pos[5],
    if d_SCo is None:
        d_SCo = chopper_pos[6],
    if d_SCc is None:
        d_SCc = chopper_pos[6],

    if freq is not None:
        per = 1 / freq
    else:
        per = 60 / rpm
        freq = 1 / per

    deg_per_sec = 360 * freq

    t_SC2o = angles[5] / deg_per_sec
    wl_min = neutron_vel2wavelength(d_SC2 / t_SC2o)

    t_SC2c = angles[4] / deg_per_sec
    wl_max = neutron_vel2wavelength((d_SC2 - d_MCo) / t_SC2c)

    return (wl_min * 1e10, wl_max * 1e10)


def neutron_vel2wavelength(vel):
    # log.info('neutron_vel2wavelength ???')
    return neutron_wavelength2vel(vel)
    # wavelength = h * math.sqrt(1 - (vel / c)**2) /(m_n * vel)


def neutron_wavelength2vel(wavelength):
    # log.debug('neutron_wavelength2vel %g %s %f', wavelength,
    #           type(wavelength), 3.95603401958e-7 / wavelength)
    # def wavelength2vel(wavelength):
    #     vel = hc / (math.sqrt(c2mn2 * wavelength **2 + h2))
    try:
        # TODO: A lot of useless statements and ZeroDivisionError's
        # wavelength[0]
        # 1 / 0  # MP 27.04.2018 08:46:50
        # wavelength = np.array(wavelength)
        pass
    except (IndexError, TypeError):
        if wavelength == 0:
            # raises ZeroDivisionError
            # 1 / 0  # MP 27.04.2018 08:46:50
            return None
            # return s.Inf
    return h / (mn * wavelength)


def chopper_resolution(chopper2_pos, D):
    """Calculates the choper resolution.

    :param int chopper2_pos: Translation position of the chopper2
    :param float D: Real flight path distance in m
    :ret: Resolution in percent
    :rtype: float
    """
    # res = d_MCo / (D - d_MCo / 2.)
    d_MCo = chopper_pos[chopper2_pos]
    d_MCo_h = d_MCo / 2.

    # denominator and numerator should be increased by half of Detectordepth
    # Detectordepth_h = 65 / .5  # [40,65]
    # numerator = d_MCo_h  # + Detectordepth_h
    numerator = d_MCo_h  # + Detectordepth_h
    denominator = D - d_MCo_h  # + Detectordepth_h
    return round(numerator / denominator * 100, 3)
