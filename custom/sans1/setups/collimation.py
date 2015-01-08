#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#   Andreas Wilhelm <andreas.wilhelm@frm2.tum.de>
#
# *****************************************************************************

description = 'collimation tube'

includes = ['system']

excludes = ['collimation_config']

# included by sans1
group = 'lowlevel'

nethost = 'sans1srv.sans1.frm2'

devices = dict(
    col        = device('nicos.devices.generic.LockedDevice',
                        description = 'sans1 primary collimation',
                        lock = 'att',
                        device = 'col_sw',
                        #lockvalue = None,     # go back to previous value
                        unlockvalue = 'x1000',
                        #keepfixed = False,	# dont fix attenuator after movement
                        lowlevel = False,
                        pollinterval = 15,
                        maxage = 60,
                       ),
    col_sw     = device('devices.generic.MultiSwitcher',
                        description = 'collimator switching device',
                        precision = None,
                        blockingmove = False,
                        unit = 'm',
                        fmtstr = '%.1f',
                        fallback = 'undefined',
                        moveables = ['col_20a', 'col_20b', 'col_16a', 'col_16b', 'col_12a', 'col_12b',
                        'col_8a', 'col_8b', 'col_4a', 'col_4b', 'col_2a', 'col_2b'],
                        # col_2b disabled !!!
                        mapping = {
                            #~ 1:   ['NG',  'NG',  'NG',  'NG',  'NG',  'NG',  'NG',  'NG',  'NG',  'NG',  'NG',  'NG'],
                            1.5: ['NG',  'NG',  'NG',  'NG',  'NG',  'NG',  'NG',  'NG',  'NG',  'NG',  'NG',  'COL'],
                            2:   ['NG',  'NG',  'NG',  'NG',  'NG',  'NG',  'NG',  'NG',  'NG',  'NG',  'COL', 'COL'],
                            3:   ['NG',  'NG',  'NG',  'NG',  'NG',  'NG',  'NG',  'NG',  'NG',  'COL', 'COL', 'COL'],
                            4:   ['NG',  'NG',  'NG',  'NG',  'NG',  'NG',  'NG',  'NG',  'COL', 'COL', 'COL', 'COL'],
                            6:   ['NG',  'NG',  'NG',  'NG',  'NG',  'NG',  'NG',  'COL', 'COL', 'COL', 'COL', 'COL'],
                            8:   ['NG',  'NG',  'NG',  'NG',  'NG',  'NG',  'COL', 'COL', 'COL', 'COL', 'COL', 'COL'],
                            10:  ['NG',  'NG',  'NG',  'NG',  'NG',  'COL', 'COL', 'COL', 'COL', 'COL', 'COL', 'COL'],
                            12:  ['NG',  'NG',  'NG',  'NG',  'COL', 'COL', 'COL', 'COL', 'COL', 'COL', 'COL', 'COL'],
                            14:  ['NG',  'NG',  'NG',  'COL', 'COL', 'COL', 'COL', 'COL', 'COL', 'COL', 'COL', 'COL'],
                            16:  ['NG',  'NG',  'COL', 'COL', 'COL', 'COL', 'COL', 'COL', 'COL', 'COL', 'COL', 'COL'],
                            18:  ['NG',  'COL', 'COL', 'COL', 'COL', 'COL', 'COL', 'COL', 'COL', 'COL', 'COL', 'COL'],
                            20:  ['COL', 'COL', 'COL', 'COL', 'COL', 'COL', 'COL', 'COL', 'COL', 'COL', 'COL', 'COL'],
                            },
                        lowlevel = True,
                       ),


    att        = device('sans1.collimotor.Sans1ColliSwitcher',
                        description = 'Attenuator',
                        #mapping = dict(OPEN=0, x1000=117, x100=234, x10=351), old 4 position att
                        mapping = dict(OPEN=0, x1000=95, x100=190, x10=285, dia10=380), #new 5 position att
                        moveable = 'att_m',
                        blockingmove = False,
                        pollinterval = 15,
                        maxage = 60,
                       ),
    att_m      = device('sans1.collimotor.Sans1ColliMotor',
                        description = 'Attenuator motor',
                        # IP-adresse: 172.16.17.1 alt
                        # IP-adresse: 172.25.49.107 neu
                        tacodevice='//%s/sans1/coll/ng-pol'% (nethost,),
                        address = 0x4020+0*10,
                        slope = 200*4, # FULL steps per turn * turns per mm
                        microsteps = 8,
                        unit = 'mm',
                        #refpos = -23.0, old 4 position att
                        refpos = -4.0, #new 5 position att
                        abslimits = (-400, 600),
                        lowlevel = True,
                        autozero = 80,
                       ),


    ng_pol     = device('sans1.collimotor.Sans1ColliSwitcher',
                        description = 'Neutronguide polariser',
                        mapping = dict(NG=0, POL1=117, POL2=234, LAS=354),
                        moveable = 'ng_pol_m',
                        pollinterval = 15,
                        maxage = 60,
                       ),
    #~ ng_pol_a   = device('devices.generic.Axis',
                        #~ description = 'Neutronguide polariser axis',
                        #~ motor = 'ng_pol_m',
                        #~ coder = 'ng_pol_c',
                        #~ dragerror = 1,
                        #~ precision = 0.001,
                        #~ lowlevel = True,
                       #~ ),
    ng_pol_m   = device('sans1.collimotor.Sans1ColliMotor',
                        description = 'Neutronguide polariser motor',
                        # IP-adresse: 172.16.17.1 alt
                        # IP-adresse: 172.25.49.107 neu
                        tacodevice='//%s/sans1/coll/ng-pol'% (nethost,),
                        address = 0x4020+1*10,
                        slope = 200*4, # FULL steps per turn * turns per mm
                        microsteps = 8,
                        unit = 'mm',
                        refpos = -4.5,
                        abslimits = (-400, 600),
                        autozero = 100,
                        #~ autozero = None, # no auto referencing with an axis !!!
                        lowlevel = True,
                       ),
    ng_pol_c   = device('sans1.collimotor.Sans1ColliCoder',
                        description = 'Neutronguide polariser coder',
                        # IP-adresse: 172.16.17.1 alt
                        # IP-adresse: 172.25.49.107 neu
                        tacodevice='//%s/sans1/coll/ng-pol'% (nethost,),
                        address = 0x40c8,
                        #~ address = 0x40cD, // docu page 8 specifies both, which is correct?
                        slope = 1000000, # resolution = nm, we want mm
                        zeropos = -13.191,
                        unit = 'mm',
                        lowlevel = True,
                       ),


    col_20a    = device('sans1.collimotor.Sans1ColliSwitcher',
                        description = 'Collimotor 20a',
                        mapping = dict(NG=0, COL=117, free=234, LAS=351),
                        moveable = 'col_20a_m',
                        blockingmove = False,
                        pollinterval = 15,
                        maxage = 60,
                        lowlevel = True,
                       ),
    #~ col_20a_a  = device('devices.generic.Axis',
                        #~ description = 'Collimotor 20a',
                        #~ motor = 'col_20a_m',
                        #~ coder = 'col_20a_c',
                        #~ dragerror = 1,
                        #~ precision = 0.001,
                        #~ lowlevel = True,
                       #~ ),
    col_20a_m  = device('sans1.collimotor.Sans1ColliMotor',
                        description = 'Collimotor 20a motor',
                        # IP-adresse: 172.16.17.2 alt
                        # IP-adresse: 172.25.49.108 neu
                        tacodevice='//%s/sans1/coll/col-20m'% (nethost,),
                        address = 0x4020+0*10,
                        slope = 200*4, # FULL steps per turn * turns per mm
                        microsteps = 8,
                        unit = 'mm',
                        refpos = -5.39,
                        abslimits = (-400, 600),
                        autozero = 100,
                        #~ autozero = None, # no auto referencing with an axis !!!
                        lowlevel = True,
                       ),
    col_20a_c  = device('sans1.collimotor.Sans1ColliCoder',
                        description = 'Collimotor 20a coder',
                        # IP-adresse: 172.16.17.2 alt
                        # IP-adresse: 172.25.49.108 neu
                        tacodevice='//%s/sans1/coll/col-20m'% (nethost,),
                        address = 0x40c8,  # docu page 9
                        slope = 1000000, # resolution = nm, we want mm
                        zeropos = 0, # unspecified in docu page 9
                        unit = 'mm',
                        lowlevel = True,
                       ),


    col_20b    = device('sans1.collimotor.Sans1ColliSwitcher',
                        description = 'Collimotor 20b',
                        mapping = dict(NG=0, COL=117, free=234, LAS=351),
                        moveable = 'col_20b_m',
                        blockingmove = False,
                        pollinterval = 15,
                        maxage = 60,
                        lowlevel = True,
                       ),
    #~ col_20b_a  = device('devices.generic.Axis',
                        #~ description = 'Collimotor 20b',
                        #~ motor = 'col_20b_m',
                        #~ coder = 'col_20b_c',
                        #~ dragerror = 1,
                        #~ precision = 0.001,
                        #~ lowlevel = True,
                       #~ ),
    col_20b_m  = device('sans1.collimotor.Sans1ColliMotor',
                        description = 'Collimotor 20b',
                        # IP-adresse: 172.16.17.2 alt
                        # IP-adresse: 172.25.49.108 neu
                        tacodevice='//%s/sans1/coll/col-20m'% (nethost,),
                        address = 0x4020+1*10,
                        slope = 200*4, # FULL steps per turn * turns per mm
                        microsteps = 8,
                        unit = 'mm',
                        refpos = -5.28,
                        abslimits = (-400, 600),
                        autozero = 100,
                        #~ autozero = None, # no auto referencing with an axis !!!
                        lowlevel = True,
                       ),
    col_20b_c  = device('sans1.collimotor.Sans1ColliCoder',
                        description = 'Collimotor 20b coder',
                        # IP-adresse: 172.16.17.2 alt
                        # IP-adresse: 172.25.49.108 neu
                        tacodevice='//%s/sans1/coll/col-20m'% (nethost,),
                        address = 0x40cd,  # docu page 10
                        slope = 1000000, # resolution = nm, we want mm
                        zeropos = 0, # unspecified in docu page 10
                        unit = 'mm',
                        lowlevel = True,
                       ),


    col_16a    = device('sans1.collimotor.Sans1ColliSwitcher',
                        description = 'Collimotor 16a',
                        mapping = dict(NG=0, COL=117, free=234, LAS=351),
                        moveable = 'col_16a_m',
                        blockingmove = False,
                        pollinterval = 1,
                        maxage = 60,
                        lowlevel = True,
                       ),
    #~ col_16a_a  = device('devices.generic.Axis',
                        #~ description = 'Collimotor 16a',
                        #~ motor = 'col_16a_m',
                        #~ coder = 'col_16a_c',
                        #~ dragerror = 1,
                        #~ precision = 0.001,
                        #~ lowlevel = True,
                       #~ ),
    col_16a_m  = device('sans1.collimotor.Sans1ColliMotor',
                        description = 'Collimotor 16a motor',
                        # IP-adresse: 172.16.17.3 alt
                        # IP-adresse: 172.25.49.111 neu
                        tacodevice='//%s/sans1/coll/col-16m'% (nethost,),
                        address = 0x4020+1*10,
                        slope = 200*4, # FULL steps per turn * turns per mm
                        microsteps = 8,
                        unit = 'mm',
                        refpos = -4.29,
                        abslimits = (-400, 600),
                        autozero = 100,
                        #~ autozero = None, # no auto referencing with an axis !!!
                        lowlevel = True,
                       ),
    col_16a_c  = device('sans1.collimotor.Sans1ColliCoder',
                        description = 'Collimotor 16a coder',
                        # IP-adresse: 172.16.17.3 alt
                        # IP-adresse: 172.25.49.111 neu
                        tacodevice='//%s/sans1/coll/col-16m'% (nethost,),
                        address = 0x40c8,  # docu page 12
                        slope = 1000000, # resolution = nm, we want mm
                        zeropos = 0, # unspecified in docu page 12
                        unit = 'mm',
                        lowlevel = True,
                       ),


    bg1        = device('sans1.collimotor.Sans1ColliSlit',
                        description = 'Background slit1',
                        mapping = {'50mm':0, 'OPEN':90, '20mm':180, '42mm':270 },
                        moveable = 'bg1_m',
                        table = 'col_16a',
                        activeposition = 'COL',
                        pollinterval = 15,
                        maxage = 60,
                       ),
    #~ bg1        = device('sans1.collimotor.Sans1ColliSwitcher',
                        #~ description = 'Background slit1',
                        #~ mapping = {'P1':0, 'P2':90, 'P3':180, 'P4':270,
                        #~ '50mm':0, 'OPEN':90, '20mm':180, '42mm':270 },
                        #~ moveable = 'col_bg1_m',
                        #~ ),
    bg1_m      = device('sans1.collimotor.Sans1ColliMotor',
                        description = 'Background slit1 motor',
                        # IP-adresse: 172.16.17.3 alt
                        # IP-adresse: 172.25.49.111 neu
                        tacodevice='//%s/sans1/coll/col-16m'% (nethost,),
                        address = 0x4020+0*10,
                        slope = 200*0.16, # FULL steps per turn * turns per mm
                        microsteps = 8,
                        unit = 'deg',
                        refpos = -28.85,
                        abslimits = (-40, 300),
                        lowlevel = True,
                        autozero = 400,
                       ),


    col_16b    = device('sans1.collimotor.Sans1ColliSwitcher',
                        description = 'Collimotor 16b',
                        mapping = dict(NG=0, COL=117, free=234, LAS=351),
                        moveable = 'col_16b_m',
                        blockingmove = False,
                        pollinterval = 15,
                        maxage = 60,
                        lowlevel = True,
                       ),
    #~ col_16b_a  = device('devices.generic.Axis',
                        #~ description = 'Collimotor 16a',
                        #~ motor = 'col_16b_m',
                        #~ coder = 'col_16b_c',
                        #~ dragerror = 1,
                        #~ precision = 0.001,
                        #~ lowlevel = True,
                       #~ ),
    col_16b_m  = device('sans1.collimotor.Sans1ColliMotor',
                        description = 'Collimotor 16b motor',
                        # IP-adresse: 172.16.17.3 alt
                        # IP-adresse: 172.25.49.111 neu
                        tacodevice='//%s/sans1/coll/col-16m'% (nethost,),
                        address = 0x4020+2*10,
                        slope = 200*4, # FULL steps per turn * turns per mm
                        microsteps = 8,
                        unit = 'mm',
                        refpos = -2.31,
                        abslimits = (-400, 600),
                        autozero = 100,
                        #~ autozero = None, # no auto referencing with an axis !!!
                        lowlevel = True,
                       ),
    col_16b_c  = device('sans1.collimotor.Sans1ColliCoder',
                        description = 'Collimotor 16b coder',
                        # IP-adresse: 172.16.17.3 alt
                        # IP-adresse: 172.25.49.111 neu
                        tacodevice='//%s/sans1/coll/col-16m'% (nethost,),
                        address = 0x40cd,  # docu page 13
                        slope = 1000000, # resolution = nm, we want mm
                        zeropos = 0, # unspecified in docu page 13
                        unit = 'mm',
                        lowlevel = True,
                       ),


    col_12a    = device('sans1.collimotor.Sans1ColliSwitcher',
                        description = 'Collimotor 12a',
                        mapping = dict(NG=0, COL=117, free=234, LAS=351),
                        moveable = 'col_12a_m',
                        blockingmove = False,
                        pollinterval = 15,
                        maxage = 60,
                        lowlevel = True,
                       ),
    #~ col_12a_a  = device('devices.generic.Axis',
                        #~ description = 'Collimotor 12a',
                        #~ motor = 'col_12a_m',
                        #~ coder = 'col_12a_c',
                        #~ dragerror = 1,
                        #~ precision = 0.001,
                        #~ lowlevel = True,
                       #~ ),
    col_12a_m  = device('sans1.collimotor.Sans1ColliMotor',
                        description = 'Collimotor 12a motor',
                        # IP-adresse: 172.16.17.4 alt
                        # IP-adresse: 172.25.49.112 neu
                        tacodevice='//%s/sans1/coll/col-12m'% (nethost,),
                        address = 0x4020+0*10,
                        slope = 200*4, # FULL steps per turn * turns per mm
                        microsteps = 8,
                        unit = 'mm',
                        refpos = -1.7,
                        abslimits = (-400, 600),
                        autozero = 100,
                        #~ autozero = None, # no auto referencing with an axis !!!
                        lowlevel = True,
                       ),
    col_12a_c  = device('sans1.collimotor.Sans1ColliCoder',
                        description = 'Collimotor 12a coder',
                        # IP-adresse: 172.16.17.4 alt
                        # IP-adresse: 172.25.49.112 neu
                        tacodevice='//%s/sans1/coll/col-12m'% (nethost,),
                        address = 0x40c8,  # docu page 14
                        slope = 1000000, # resolution = nm, we want mm
                        zeropos = 0, # unspecified in docu page 14
                        unit = 'mm',
                        lowlevel = True,
                       ),


    col_12b    = device('sans1.collimotor.Sans1ColliSwitcher',
                        description = 'Collimotor 12b',
                        mapping = dict(NG=0, COL=117, free=234, LAS=351),
                        moveable = 'col_12b_m',
                        blockingmove = False,
                        pollinterval = 15,
                        maxage = 60,
                        lowlevel = True,
                       ),
    #~ col_12b_a  = device('devices.generic.Axis',
                        #~ description = 'Collimotor 12b',
                        #~ motor = 'col_12b_m',
                        #~ coder = 'col_12b_c',
                        #~ dragerror = 1,
                        #~ precision = 0.001,
                        #~ lowlevel = True,
                       #~ ),
    col_12b_m  = device('sans1.collimotor.Sans1ColliMotor',
                        description = 'Collimotor 12b motor',
                        # IP-adresse: 172.16.17.4 alt
                        # IP-adresse: 172.25.49.112 neu
                        tacodevice='//%s/sans1/coll/col-12m'% (nethost,),
                        address = 0x4020+1*10,
                        slope = 200*4, # FULL steps per turn * turns per mm
                        microsteps = 8,
                        unit = 'mm',
                        refpos = -5.14, #needs to be checked by O. Frank !!!
                        abslimits = (-400, 600),
                        autozero = 100,
                        #~ autozero = None, # no auto referencing with an axis !!!
                        lowlevel = True,
                       ),
    col_12b_c  = device('sans1.collimotor.Sans1ColliCoder',
                        description = 'Collimotor 12b coder',
                        # IP-adresse: 172.16.17.4 alt
                        # IP-adresse: 172.25.49.112 neu
                        tacodevice='//%s/sans1/coll/col-12m'% (nethost,),
                        address = 0x40cd,  # docu page 15
                        slope = 1000000, # resolution = nm, we want mm
                        zeropos = 0, # unspecified in docu page 15
                        unit = 'mm',
                        lowlevel = True,
                       ),


    col_8a     = device('sans1.collimotor.Sans1ColliSwitcher',
                        description = 'Collimotor 8a',
                        mapping = dict(NG=0, COL=117, free=234, LAS=351),
                        moveable = 'col_8a_m',
                        blockingmove = False,
                        pollinterval = 15,
                        maxage = 60,
                        lowlevel = True,
                       ),
    #~ col_8a_a   = device('devices.generic.Axis',
                        #~ description = 'Collimotor 8a',
                        #~ motor = 'col_8a_m',
                        #~ coder = 'col_8a_c',
                        #~ dragerror = 1,
                        #~ precision = 0.001,
                        #~ lowlevel = True,
                       #~ ),
    col_8a_m   = device('sans1.collimotor.Sans1ColliMotor',
                        description = 'Collimotor 8a motor',
                        # IP-adresse: 172.16.17.5 alt
                        # IP-adresse: 172.25.49.113 neu
                        tacodevice='//%s/sans1/coll/col-8m'% (nethost,),
                        address = 0x4020+1*10,
                        slope = 200*4, # FULL steps per turn * turns per mm
                        microsteps = 8,
                        unit = 'mm',
                        refpos = -3.88,
                        abslimits = (-400, 600),
                        autozero = 100,
                        #~ autozero = None, # no auto referencing with an axis !!!
                        lowlevel = True,
                       ),
    col_8a_c   = device('sans1.collimotor.Sans1ColliCoder',
                        description = 'Collimotor 8a coder',
                        # IP-adresse: 172.16.17.5 alt
                        # IP-adresse: 172.25.49.113 neu
                        tacodevice='//%s/sans1/coll/col-8m'% (nethost,),
                        address = 0x40c8,  # docu page 17
                        slope = 1000000, # resolution = nm, we want mm
                        zeropos = 0, # unspecified in docu page 17
                        unit = 'mm',
                        lowlevel = True,
                       ),


    col_8b     = device('sans1.collimotor.Sans1ColliSwitcher',
                        description = 'Collimotor 8b',
                        mapping = dict(NG=0, COL=117, free=234, LAS=351),
                        moveable = 'col_8b_m',
                        blockingmove = False,
                        pollinterval = 15,
                        maxage = 60,
                        lowlevel = True,
                       ),
    #~ col_8b_a   = device('devices.generic.Axis',
                        #~ description = 'Collimotor 8b',
                        #~ motor = 'col_8b_m',
                        #~ coder = 'col_8b_c',
                        #~ dragerror = 1,
                        #~ precision = 0.001,
                        #~ lowlevel = True,
                       #~ ),
    col_8b_m   = device('sans1.collimotor.Sans1ColliMotor',
                        description = 'Collimotor 8b motor',
                        # IP-adresse: 172.16.17.5 alt
                        # IP-adresse: 172.25.49.113 neu
                        tacodevice='//%s/sans1/coll/col-8m'% (nethost,),
                        address = 0x4020+2*10,
                        slope = 200*4, # FULL steps per turn * turns per mm
                        microsteps = 8,
                        unit = 'mm',
                        refpos = -4.13,
                        abslimits = (-400, 600),
                        autozero = 100,
                        #~ autozero = None, # no auto referencing with an axis !!!
                        lowlevel = True,
                       ),
    col_8b_c   = device('sans1.collimotor.Sans1ColliCoder',
                        description = 'Collimotor 8b coder',
                        # IP-adresse: 172.16.17.5 alt
                        # IP-adresse: 172.25.49.113 neu
                        tacodevice='//%s/sans1/coll/col-8m'% (nethost,),
                        address = 0x40cd,  # docu page 18
                        slope = 1000000, # resolution = nm, we want mm
                        zeropos = 0, # unspecified in docu page 18
                        unit = 'mm',
                        lowlevel = True,
                       ),


    bg2        = device('sans1.collimotor.Sans1ColliSlit',
                        description = 'Background slit2',
                        mapping = {'28mm':0, '20mm':90, '12mm':180, 'OPEN':270 },
                        moveable = 'bg2_m',
                        table = 'col_8b',
                        activeposition = 'COL',
                        pollinterval = 15,
                        maxage = 60,
                       ),
#    bg2        = device('sans1.collimotor.Sans1ColliSwitcher',
#                        description = 'Background slit2',
#                        mapping = {'28mm':0, '20mm':90, '12mm':180, 'OPEN':270 },
#                        moveable = 'col_bg2_m',
#                       ),
    bg2_m      = device('sans1.collimotor.Sans1ColliMotor',
                        description = 'Background slit2 motor',
                        # IP-adresse: 172.16.17.5 alt
                        # IP-adresse: 172.25.49.113 neu
                        tacodevice='//%s/sans1/coll/col-8m'% (nethost,),
                        address = 0x4020+0*10,
                        slope = 200*0.16, # FULL steps per turn * turns per mm
                        microsteps = 8,
                        unit = 'deg',
                        refpos = -1.5,
                        abslimits = (-40, 300),
                        lowlevel = True,
                        autozero = 400,
                       ),


    col_4a     = device('sans1.collimotor.Sans1ColliSwitcher',
                        description = 'Collimotor 4a',
                        mapping = dict(NG=0, COL=117, free=234, LAS=351),
                        moveable = 'col_4a_m',
                        blockingmove = False,
                        pollinterval = 15,
                        maxage = 60,
                        lowlevel = True,
                       ),
    #~ col_4a_a   = device('devices.generic.Axis',
                        #~ description = 'Collimotor 4a',
                        #~ motor = 'col_4a_m',
                        #~ coder = 'col_4a_c',
                        #~ dragerror = 1,
                        #~ precision = 0.001,
                        #~ lowlevel = True,
                       #~ ),
    col_4a_m   = device('sans1.collimotor.Sans1ColliMotor',
                        description = 'Collimotor 4a motor',
                        # IP-adresse: 172.16.17.6 alt
                        # IP-adresse: 172.25.49.114 neu
                        tacodevice='//%s/sans1/coll/col-4m'% (nethost,),
                        address = 0x4020+1*10,
                        slope = 200*4, # FULL steps per turn * turns per mm
                        microsteps = 8,
                        unit = 'mm',
                        refpos = -9.37,
                        abslimits = (-400, 600),
                        autozero = 100,
                        #~ autozero = None, # no auto referencing with an axis !!!
                        lowlevel = True,
                       ),
    col_4a_c   = device('sans1.collimotor.Sans1ColliCoder',
                        description = 'Collimotor 4a coder',
                        # IP-adresse: 172.16.17.6 alt
                        # IP-adresse: 172.25.49.114 neu
                        tacodevice='//%s/sans1/coll/col-4m'% (nethost,),
                        address = 0x40c8,  # docu page 19
                        slope = 1000000, # resolution = nm, we want mm
                        zeropos = 0, # unspecified in docu page 19
                        unit = 'mm',
                        lowlevel = True,
                       ),


    col_4b     = device('sans1.collimotor.Sans1ColliSwitcher',
                        description = 'Collimotor 4b',
                        mapping = dict(NG=0, COL=117, free=234, LAS=351),
                        moveable = 'col_4b_m',
                        blockingmove = False,
                        pollinterval = 15,
                        maxage = 60,
                        lowlevel = True,
                       ),
    #~ col_4b_a   = device('devices.generic.Axis',
                        #~ description = 'Collimotor 4b',
                        #~ motor = 'col_4b_m',
                        #~ coder = 'col_4b_c',
                        #~ dragerror = 1,
                        #~ precision = 0.001,
                        #~ lowlevel = True,
                       #~ ),
    col_4b_m   = device('sans1.collimotor.Sans1ColliMotor',
                        description = 'Collimotor 4b motor',
                        # IP-adresse: 172.16.17.6 alt
                        # IP-adresse: 172.25.49.114 neu
                        tacodevice='//%s/sans1/coll/col-4m'% (nethost,),
                        address = 0x4020+2*10,
                        slope = 200*4, # FULL steps per turn * turns per mm
                        microsteps = 8,
                        unit = 'mm',
                        refpos = -9.35,
                        abslimits = (-400, 600),
                        autozero = 100,
                        #~ autozero = None, # no auto referencing with an axis !!!
                        lowlevel = True,
                       ),
    col_4b_c   = device('sans1.collimotor.Sans1ColliCoder',
                        description = 'Collimotor 4b coder',
                        # IP-adresse: 172.16.17.6 alt
                        # IP-adresse: 172.25.49.114 neu
                        tacodevice='//%s/sans1/coll/col-4m'% (nethost,),
                        address = 0x40cd,  # docu page 20
                        slope = 1000000, # resolution = nm, we want mm
                        zeropos = 0, # unspecified in docu page 20
                        unit = 'mm',
                        lowlevel = True,
                       ),


    col_2a     = device('sans1.collimotor.Sans1ColliSwitcher',
                        description = 'Collimotor 2a',
                        mapping = dict(NG=0, COL=117, free=234, LAS=351),
                        moveable = 'col_2a_m',
                        blockingmove = False,
                        pollinterval = 15,
                        maxage = 60,
                        lowlevel = True,
                       ),
    #~ col_2a_a   = device('devices.generic.Axis',
                        #~ description = 'Collimotor 2a',
                        #~ motor = 'col_2a_m',
                        #~ coder = 'col_2a_c',
                        #~ dragerror = 1,
                        #~ precision = 0.001,
                        #~ lowlevel = True,
                       #~ ),
    col_2a_m   = device('sans1.collimotor.Sans1ColliMotor',
                        description = 'Collimotor 2a motor',
                        # IP-adresse: 172.16.17.7 alt
                        # IP-adresse: 172.25.49.115 neu
                        tacodevice='//%s/sans1/coll/col-2m'% (nethost,),
                        address = 0x4020+1*10,
                        slope = 200*4, # FULL steps per turn * turns per mm
                        microsteps = 8,
                        unit = 'mm',
                        refpos = -8.,
                        abslimits = (-400, 600),
                        autopower = 'on',
                        autozero = 100,
                        #~ autozero = None, # no auto referencing with an axis !!!
                        lowlevel = True,
                       ),
    col_2a_c   = device('sans1.collimotor.Sans1ColliCoder',
                        description = 'Collimotor 2a coder',
                        # IP-adresse: 172.16.17.7 alt
                        # IP-adresse: 172.25.49.115 neu
                        tacodevice='//%s/sans1/coll/col-2m'% (nethost,),
                        address = 0x40c8,  # docu page 22
                        slope = 1000000, # resolution = nm, we want mm
                        zeropos = 0, # unspecified in docu page 22
                        unit = 'mm',
                        lowlevel = True,
                       ),


    col_2b     = device('sans1.collimotor.Sans1ColliSwitcher',
                        description = 'Collimotor 2b',
                        mapping = dict(NG=0, COL=117, free=234, LAS=351),
                        moveable = 'col_2b_m',
                        blockingmove = False,
                        pollinterval = 15,
                        maxage = 60,
                        lowlevel = True,
                       ),
    #~ col_2b_a   = device('devices.generic.Axis',
                        #~ description = 'Collimotor 4b',
                        #~ motor = 'col_2b_m',
                        #~ coder = 'col_2b_c',
                        #~ dragerror = 1,
                        #~ precision = 0.001,
                        #~ lowlevel = True,
                       #~ ),
    col_2b_m   = device('sans1.collimotor.Sans1ColliMotor',
                        description = 'Collimotor 2b motor',
                        # IP-adresse: 172.16.17.7 alt
                        # IP-adresse: 172.25.49.115 neu
                        tacodevice='//%s/sans1/coll/col-2m'% (nethost,),
                        address = 0x4020+2*10,
                        slope = 200*4, # FULL steps per turn * turns per mm
                        microsteps = 8,
                        unit = 'mm',
                        refpos = -9.,
                        abslimits = (-400, 600),
                        fixed = 'unreliable, do not use !',
                        fixedby = ('setupfile', 99),      # deny release!
                        autozero = 100,
                        #~ autozero = None, # no auto referencing with an axis !!!
                        lowlevel = True,
                       ),
    col_2b_c   = device('sans1.collimotor.Sans1ColliCoder',
                        description = 'Collimotor 2b coder',
                        # IP-adresse: 172.16.17.7 alt
                        # IP-adresse: 172.25.49.115 neu
                        tacodevice='//%s/sans1/coll/col-2m'% (nethost,),
                        address = 0x40cd,  # docu page 23
                        slope = 1000000, # resolution = nm, we want mm
                        zeropos = 0, # unspecified in docu page 23
                        unit = 'mm',
                        lowlevel = True,
                       ),


    sa1        = device('sans1.collimotor.Sans1ColliSwitcher',
                        description = 'attenuation slits',
                        mapping = {'P1':0, 'P2':70, 'P3':140, 'P4':210,
                        '50x50':0, '10mm':70, '20mm':140, 'N.A.':210 },
                        moveable = 'sa1_m',
                        blockingmove = False,
                        pollinterval = 15,
                        maxage = 60,
                       ),
    sa1_m      = device('sans1.collimotor.Sans1ColliMotor',
                        description = 'attenuation slits motor',
                        # IP-adresse: 172.16.17.7 alt
                        # IP-adresse: 172.25.49.115 neu
                        tacodevice='//%s/sans1/coll/col-2m'% (nethost,),
                        address = 0x4020+0*10,
                        slope = 200*4, # FULL steps per turn * turns per mm
                        microsteps = 8,
                        unit = 'mm',
                        refpos = -34.7,
                        abslimits = (-40, 300),
                        lowlevel = True,
                        autozero = 400,
                       ),
# pump devices of 172.17.17.10 are at modbus-tacodevice //sans1srv.sans.frm2/sans1/coll/pump
)
