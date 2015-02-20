#  -*- coding: utf-8 -*-

description = '15T magnet from Panda with labview-control'

includes = ['alias_T', 'alias_B']

group = 'optional'

devices = dict(

    moxa_mono_port2 = device('panda.mcc2.TacoSerial',
                             tacodevice = 'panda/network/mxmono_p2',
                             lowlevel = True,
                            ),

    sth_15t_coder = device('panda.mcc2.MCC2Coder',
                           bus = 'moxa_mono_port2',
                           channel = 'Y',
                           addr = 0,
                           slope = -1024,
                           zerosteps = 720000,
                           codertype = 'ssi-gray', #oneof('none','incremental','ssi-binary','ssi-gray')
                           coderbits = 24,
                           unit = 'deg',
                           lowlevel = True,
                          ),
    sth_15t_step = device('panda.mcc2.MCC2Motor',
                          bus = 'moxa_mono_port2',
                          channel = 'Y',
                          addr = 0,
                          slope = 50,
                          precision = 0.01,
                          fmtstr = '%.3f',
                          abslimits = (-360,360),
                          userlimits = (0,360),
                          unit = 'deg',
                          accel = 0.01,       # physical units !!!
                          speed = 2,        # physical units !!!
                          microstep = 2,
                          idlecurrent = 0.5,
                          rampcurrent = 2.5,
                          movecurrent = 2.3,
                          lowlevel = True,
                         ),
   sth_15t = device('devices.generic.Axis',
                    description = 'rotational axis inside 15T magnet: samplestick or dilution',
                    motor = 'sth_15t_step',
                    coder = 'sth_15t_coder',
                    obs = [],
                    precision = 0.001,
                    backlash = -0.25,
                   ),
#~   sth_15t_kelvinox_coder = device('panda.mcc2.MCC2Coder',
                                  #~ bus='moxa_mono_port2',
                                  #~ channel='Y',
                                  #~ addr=0,
                                  #~ slope=1024*4,
                                  #~ zerosteps=720000*2,
                                  #~ codertype='ssi-binary', #oneof('none','incremental','ssi-binary','ssi-gray')
                                  #~ coderbits=26,
                                  #~ unit='deg',
                                  #~ lowlevel=True,
                                 #~ ),
#~   sth_15t_kelvinox_step = device('panda.mcc2.MCC2Motor',
                                 #~ bus='moxa_mono_port2',
                                 #~ channel='Y',
                                 #~ addr=0,
                                 #~ slope=1000,
                                 #~ precision=0.01,
                                 #~ fmtstr='%.3f',
                                 #~ abslimits=(0,360),
                                 #~ unit='deg',
                                 #~ accel=0.01,       # physical units !!!
                                 #~ speed=2,        # physical units !!!
                                 #~ microstep=2,
                                 #~ idlecurrent=0.4,
                                 #~ rampcurrent=1.5,
                                 #~ movecurrent=1.2,
                                 #~ lowlevel=True,
                                #~ ),
#~   sth = device('devices.generic.Axis',
               #~ motor = 'sth_15t_kelvinox_step',
               #~ coder = 'sth_15t_kelvinox_coder',
               #~ obs = [],
               #~ precision = 0.001,
               #~ backlash = -0.5,
              #~ ),

# DONT change names below or the labview part wont work anymore !!!!!

    vti         = device('devices.generic.cache.CacheWriter',
                         description = 'variable Temperature Insert',
                         userlimits = ( 1, 200 ),
                         abslimits = (0, 311 ),
                         fmtstr = '%.3f',
                         unit = 'K',
                         loopdelay = 5,
                         window = 60,
                         maxage = 30,
                         precision = 0.2,
                        ),
    sTs         = device('devices.generic.cache.CacheReader',
                         description = 'Sample Temperature',
                         fmtstr = '%.3f',
                         unit = 'K',
                         maxage = 30,
                        ),
    LN2         = device('devices.generic.cache.CacheReader',
                         description = 'Level of Liquid Nitrogen',
                         fmtstr = '%.1f',
                         unit = '%',
                         maxage = 300,
                        ),
    LHe         = device('devices.generic.cache.CacheReader',
                         description = 'Level of Liquid Helium',
                         fmtstr = '%.1f',
                         unit = '%',
                         maxage = 900,
                        ),
    NV          = device('devices.generic.cache.CacheReader',
                         description = 'Position of Needlevalve controlling cooling of vti',
                         fmtstr = '%.1f',
                         unit = '%',
                         maxage = 30,
                        ),
    B15T = device('devices.generic.cache.CacheWriter',
                  description = 'Magnetic field',
                  userlimits=( -12, 12 ),
                  abslimits = ( -15, 15 ),
                  warnlimits = ( -13, 13 ), # needs lambda-stage
                  fmtstr = '%.2f',
                  unit = 'T',
                  setkey = 'target',
                  window = 10,
                  maxage = 30,
                  precision = 0.001,
                 ),
)

startupcode = '''
B.alias='B15T'
T.alias='vti'
Ts.alias='sTs'
sth.alias='sth_15T'
'''
