#  -*- coding: utf-8 -*-

description = 'PANDA-version of a setup for the FRM2 7T5 Magnet'

includes = ['alias_B']

excludes = ['7T5']

group = 'optional'

TACOBASE = '//magnet.panda.frm2/magnet/'

devices = dict(
# overrides only needed stuff from frm2/magnt75.py
    # Magnet power supply. it is supposed to be able to switch polarity....

    B_m7T5 = device('panda.misc.PrecisionAnalogOut',
                    description = '7.5T magnet field drive',
                    precision = 0.02,
                    tacodevice = TACOBASE + 'smc120/t',
                    userlimits=( 0, 7.0 ),
                    abslimits = (-7.5, 7.5 ),
                    fmtstr = '%.2f',
                    unit = 'T',
                    pollinterval = 15,
                   ),

#~   B_m7T5 =device('devices.taco.AnalogOutput',
                 #~ tacodevice = TACOBASE+'smc120/t',
                 #~ description = '7.5T magnet field drive',
                 #~ userlimits=( 0, 7.0 ),
                 #~ abslimits = (-7.5, 7.5 ),
                 #~ fmtstr = '%.2f',
                 #~ unit = 'T',
                 #~ pollinterval=15,
                #~ ),

    # Nicos based access to phytron in magnet rack
#~   magnetmotorbus = device('panda.mcc2.TacoSerial',
                          #~ tacodevice=TACOBASE+'rs232/phytron',     # new value as of 2012-07-30 EF
                         #~ ),

#~   sth_B7T5_step = device('panda.mcc2.MCC2Motor',
                         #~ bus='magnetmotorbus',
                         #~ precision=0.01,
                         #~ fmtstr='%.3f',
                         #~ tacodevice=TACOBASE+'rs232/phytron',
                         #~ description = '7.5T magnet sample rotation MOTOR using only the RS232 TACOSERVER and talking to mcc2',
                         #~ channel='Y',
                         #~ addr=0,
                         #~ #slope=-480000.0/(360.0*6),
                         #~ slope=-75000.0/(360.0),
                         #~ abslimits=(-360,360),
                         #~ userlimits=(0,120),
                         #~ unit='deg',
                         #~ idlecurrent=0.4,
                         #~ movecurrent=1.0,
                         #~ rampcurrent=1.2,
                         #~ microstep=8,
                         #~ speed=2.0,
                        #~ ),
#~   sth_B7T5_coder = device('panda.mcc2.MCC2Coder',
                          #~ bus='magnetmotorbus',
                          #~ fmtstr='%.3f',
                          #~ tacodevice=TACOBASE+'rs232/phytron',     # new value as of 2012-07-30 EF
                          #~ description = '7.5T magnet sample rotation CODER using only the RS232 TACOSERVER and talking to mcc2',
                          #~ channel='Y',
                          #~ addr=0,
                          #~ slope=-480000.0/360.0,
                          #~ abslimits=(-360,360),
                          #~ unit='deg',
                          #~ zerosteps=0,
                          #~ codertype='incremental',
                          #~ coderbits=25,
                         #~ ),
#~   sth_B7T5 = device('devices.generic.Axis',
                    #~ motor = 'sth_B7T5_step',
                    #~ coder = 'sth_B7T5_coder',
                    #~ obs = [],
                    #~ precision = 0.01,
                    #~ backlash = -1,
                   #~ ),


    # Phytron (TACO) controled cryo rotation....
    sth_B7T5_Taco_motor = device('devices.taco.Motor',
                                  tacodevice = TACOBASE + 'phytron/motor',
                                  description = '7.5T magnet sample rotation TACO-Motor',
                                  userlimits=( 0, 148.0 ),
                                  abslimits = (-1, 160 ),
                                  fmtstr = '%.3f',
                                  unit = 'deg',
                                ),
    sth_B7T5_Taco_coder = device('devices.taco.Coder',
                                 tacodevice = TACOBASE + 'phytron/encoder',
                                 description = '7.5T magnet sample rotation TACO-Coder',
                                 fmtstr = '%.3f',
                                 unit = 'deg',
                                ),
    sth_B7T5 = device('devices.generic.Axis',
                       description = 'sample/ccr rotation inside 7.5T magnet',
                       motor = 'sth_B7T5_Taco_motor',
                       coder = 'sth_B7T5_Taco_coder',     # Coder working
                       #~ coder = 'sth_B7T5_Taco_motor',     # Coder broken
                       obs = [],
                       precision = 0.01,
                       backlash = -1,
                       abslimits = (-1., 160. ),
                       userlimits=( 0., 148.0 ),
                      ),
)

startupcode = '''
B.alias = 'B_m7T5'
sth.alias = 'sth_B7T5'
'''
