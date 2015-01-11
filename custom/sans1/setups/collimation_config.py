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

description = 'Vacuum sensors of collimation tube'

includes = ['system']

excludes = ['collimation']

group = 'lowlevel' # should not be visible to users

nethost = 'sans1srv.sans1.frm2'

devices = dict(
    col_2a_m = device('sans1.collimotor.Sans1ColliMotorAllParams',
                      description = 'CollimatorMotor 2a',
                      # IP-adresse: 172.16.17.7
                      tacodevice='//%s/sans1/coll/col-2m'% (nethost, ),
                      address = 0x4020+1*10,
                      slope = 200*4, # FULL steps per turn * turns per mm
                      microsteps = 8,
                      unit = 'mm',
                      refpos = -8.,
                      abslimits = (-400, 600),
                      #hw_disencfltr = 'enabled',
                      autozero = 20,
                      autopower =1,
                     ),


    #~ at = device('sans1.collimotor.Sans1ColliMotorAllParams',
                #~ description = 'Attenuator',
                #~ # IP-adresse: 172.16.17.1
                #~ tacodevice='//%s/sans1/coll/ng-pol'% (nethost, ),
                #~ address = 0x4020+0*10,
                #~ slope = 200*4, # FULL steps per turn * turns per mm
                #~ microsteps = 8,
                #~ unit = 'mm',
                #~ refpos = -23.0,
                #~ abslimits = (-400, 600),
                #~ mapping = dict( P1=0, P2=117, P3=234, P4=351, OPEN=0, x10=117, x100=234, x1000=351 ),
               #~ ),
    #~ ng_pol = device('sans1.collimotor.Sans1ColliMotorAllParams',
                    #~ description = 'Neutronguide polariser',
                    #~ # IP-adresse: 172.16.17.1
                    #~ tacodevice='//%s/sans1/coll/ng-pol'% (nethost, ),
                    #~ address = 0x4020+1*10,
                    #~ slope = 200*4, # FULL steps per turn * turns per mm
                    #~ microsteps = 8,
                    #~ unit = 'mm',
                    #~ refpos = -4.5,
                    #~ abslimits = (-400, 600),
                    #~ mapping = dict( P1=0, P2=117, P3=234, P4=351, NG=0, POL1=117, POL2=234, LASER=351 ),
                   #~ ),
    #~ col_20a = device('sans1.collimotor.Sans1ColliMotorAllParams',
                     #~ description = 'CollimatorMotor 20a',
                     #~ # IP-adresse: 172.16.17.2
                     #~ tacodevice='//%s/sans1/coll/col-20m'% (nethost, ),
                     #~ address = 0x4020+0*10,
                     #~ slope = 200*4, # FULL steps per turn * turns per mm
                     #~ microsteps = 8,
                     #~ unit = 'mm',
                     #~ refpos = -5.39,
                     #~ abslimits = (-400, 600),
                     #~ mapping = dict( P1=0, P2=117, P3=234, P4=351, NG=0, COL=117, FREE=234, LASER=351 ),
                    #~ ),
    #~ col_20b = device('sans1.collimotor.Sans1ColliMotorAllParams',
                     #~ description = 'CollimatorMotor 20b',
                     #~ # IP-adresse: 172.16.17.2
                     #~ tacodevice='//%s/sans1/coll/col-20m'% (nethost, ),
                     #~ address = 0x4020+1*10,
                     #~ slope = 200*4, # FULL steps per turn * turns per mm
                     #~ microsteps = 8,
                     #~ unit = 'mm',
                     #~ refpos = -5.28,
                     #~ abslimits = (-400, 600),
                     #~ mapping = dict( P1=0, P2=117, P3=234, P4=351, NG=0, COL=117, FREE=234, LASER=351 ),
                    #~ ),
    #~ bg1 = device('sans1.collimotor.Sans1ColliMotorAllParams',
                 #~ description = 'Background slit1 motor',
                 #~ # IP-adresse: 172.16.17.3
                 #~ tacodevice='//%s/sans1/coll/col-16m'% (nethost, ),
                 #~ address = 0x4020+0*10,
                 #~ slope = 200*0.16, # FULL steps per turn * turns per mm
                 #~ microsteps = 8,
                 #~ unit = 'mm',
                 #~ refpos = -28.85,
                 #~ abslimits = (-40, 300),
                 #~ mapping = {'P1':0, 'P2':90, 'P3':180, 'P4':270,
                            #~ '50mm':0, 'OPEN':90, '20mm':180, '42mm':270 },
                #~ ),
    #~ col_16a = device('sans1.collimotor.Sans1ColliMotorAllParams',
                     #~ description = 'CollimatorMotor 16a',
                     #~ # IP-adresse: 172.16.17.3
                     #~ tacodevice='//%s/sans1/coll/col-16m'% (nethost, ),
                     #~ address = 0x4020+1*10,
                     #~ slope = 200*4, # FULL steps per turn * turns per mm
                     #~ microsteps = 8,
                     #~ unit = 'mm',
                     #~ refpos = -4.29,
                     #~ abslimits = (-400, 600),
                     #~ mapping = dict( P1=0, P2=117, P3=234, P4=351, NG=0, COL=117, FREE=234, LASER=351 ),
                    #~ ),
    #~ col_16b = device('sans1.collimotor.Sans1ColliMotorAllParams',
                     #~ description = 'CollimatorMotor 16b',
                     #~ # IP-adresse: 172.16.17.3
                     #~ tacodevice='//%s/sans1/coll/col-16m'% (nethost, ),
                     #~ address = 0x4020+2*10,
                     #~ slope = 200*4, # FULL steps per turn * turns per mm
                     #~ microsteps = 8,
                     #~ unit = 'mm',
                     #~ refpos = -2.31,
                     #~ abslimits = (-400, 600),
                     #~ mapping = dict( P1=0, P2=117, P3=234, P4=351, NG=0, COL=117, FREE=234, LASER=351 ),
                    #~ ),
    #~ col_12a = device('sans1.collimotor.Sans1ColliMotorAllParams',
                     #~ description = 'CollimatorMotor 12a',
                     #~ # IP-adresse: 172.16.17.4
                     #~ tacodevice='//%s/sans1/coll/col-12m'% (nethost, ),
                     #~ address = 0x4020+0*10,
                     #~ slope = 200*4, # FULL steps per turn * turns per mm
                     #~ microsteps = 8,
                     #~ unit = 'mm',
                     #~ refpos = -1.7,
                     #~ abslimits = (-400, 600),
                     #~ mapping = dict( P1=0, P2=117, P3=234, P4=351, NG=0, COL=117, FREE=234, LASER=351 ),
                    #~ ),
    #~ col_12b = device('sans1.collimotor.Sans1ColliMotorAllParams',
                     #~ description = 'CollimatorMotor 12b',
                     #~ # IP-adresse: 172.16.17.4
                     #~ tacodevice='//%s/sans1/coll/col-12m'% (nethost, ),
                     #~ address = 0x4020+1*10,
                     #~ slope = 200*4, # FULL steps per turn * turns per mm
                     #~ microsteps = 8,
                     #~ unit = 'mm',
                     #~ refpos = -9.999, #XXX: Angabe fehlt in Doku !!!
                     #~ abslimits = (-400, 600),
                     #~ mapping = dict( P1=0, P2=117, P3=234, P4=351, NG=0, COL=117, FREE=234, LASER=351 ),
                    #~ ),
    #~ bg2 = device('sans1.collimotor.Sans1ColliMotorAllParams',
                 #~ description = 'Background slit2',
                 #~ # IP-adresse: 172.16.17.5
                 #~ tacodevice='//%s/sans1/coll/col-8m'% (nethost, ),
                 #~ address = 0x4020+0*10,
                 #~ slope = 200*0.16, # FULL steps per turn * turns per mm
                 #~ microsteps = 8,
                 #~ unit = 'mm',
                 #~ refpos = -1.5,
                 #~ abslimits = (-40, 300),
                 #~ mapping = {'P1':0, 'P2':90, 'P3':180, 'P4':270,
                            #~ '28mm':0, '20mm':90, '12mm':180, 'OPEN':270 },
                #~ ),
    #~ col_8a = device('sans1.collimotor.Sans1ColliMotorAllParams',
                    #~ description = 'CollimatorMotor 8a',
                    #~ # IP-adresse: 172.16.17.5
                    #~ tacodevice='//%s/sans1/coll/col-8m'% (nethost, ),
                    #~ address = 0x4020+1*10,
                    #~ slope = 200*4, # FULL steps per turn * turns per mm
                    #~ microsteps = 8,
                    #~ unit = 'mm',
                    #~ refpos = -3.88,
                    #~ abslimits = (-400, 600),
                    #~ mapping = dict( P1=0, P2=117, P3=234, P4=351, NG=0, COL=117, FREE=234, LASER=351 ),
                   #~ ),
    #~ col_8b = device('sans1.collimotor.Sans1ColliMotorAllParams',
                    #~ description = 'CollimatorMotor 8b',
                    #~ # IP-adresse: 172.16.17.5
                    #~ tacodevice='//%s/sans1/coll/col-8m'% (nethost, ),
                    #~ address = 0x4020+2*10,
                    #~ slope = 200*4, # FULL steps per turn * turns per mm
                    #~ microsteps = 8,
                    #~ unit = 'mm',
                    #~ refpos = -4.13,
                    #~ abslimits = (-400, 600),
                    #~ mapping = dict( P1=0, P2=117, P3=234, P4=351, NG=0, COL=117, FREE=234, LASER=351 ),
                   #~ ),
    #~ col_4a = device('sans1.collimotor.Sans1ColliMotorAllParams',
                    #~ description = 'CollimatorMotor 4a',
                    #~ # IP-adresse: 172.16.17.6
                    #~ tacodevice='//%s/sans1/coll/col-4m'% (nethost, ),
                    #~ address = 0x4020+1*10,
                    #~ slope = 200*4, # FULL steps per turn * turns per mm
                    #~ microsteps = 8,
                    #~ unit = 'mm',
                    #~ refpos = -9.37,
                    #~ abslimits = (-400, 600),
                    #~ mapping = dict( P1=0, P2=117, P3=234, P4=351, NG=0, COL=117, FREE=234, LASER=351 ),
                   #~ ),
    #~ col_4b = device('sans1.collimotor.Sans1ColliMotorAllParams',
                    #~ description = 'CollimatorMotor 4b',
                    #~ # IP-adresse: 172.16.17.6
                    #~ tacodevice='//%s/sans1/coll/col-4m'% (nethost, ),
                    #~ address = 0x4020+2*10,
                    #~ slope = 200*4, # FULL steps per turn * turns per mm
                    #~ microsteps = 8,
                    #~ unit = 'mm',
                    #~ refpos = -9.35,
                    #~ abslimits = (-400, 600),
                    #~ mapping = dict( P1=0, P2=117, P3=234, P4=351, NG=0, COL=117, FREE=234, LASER=351 ),
                   #~ ),
    #~ col_sa1 = device('sans1.collimotor.Sans1ColliMotorAllParams',
                     #~ description = 'attenuation slits',
                     #~ # IP-adresse: 172.16.17.7
                     #~ tacodevice='//%s/sans1/coll/col-2m'% (nethost, ),
                     #~ address = 0x4020+0*10,
                     #~ slope = 200*4, # FULL steps per turn * turns per mm
                     #~ microsteps = 8,
                     #~ unit = 'mm',
                     #~ refpos = -34.7,
                     #~ abslimits = (-40, 300),
                     #~ mapping = {'P1':0, 'P2':70, 'P3':140, 'P4':210,
                                #~ '50x50':0, '30mm':70, '20mm':140, '10mm':210 },
                    #~ ),
    #~ col_2b = device('sans1.collimotor.Sans1ColliMotorAllParams',
                    #~ description = 'CollimatorMotor 2b',
                    #~ # IP-adresse: 172.16.17.7
                    #~ tacodevice='//%s/sans1/coll/col-2m'% (nethost, ),
                    #~ address = 0x4020+2*10,
                    #~ slope = 200*4, # FULL steps per turn * turns per mm
                    #~ microsteps = 8,
                    #~ unit = 'mm',
                    #~ refpos = -9.,
                    #~ abslimits = (-400, 600),
                    #~ mapping = dict( P1=0, P2=117, P3=234, P4=351, NG=0, COL=117, FREE=234, LASER=351 ),
                   #~ ),
# pump devices of 172.17.17.10 are at modbus-tacodevice //sans1srv.sans.frm2/sans1/coll/pump
)

