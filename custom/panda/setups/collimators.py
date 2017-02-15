#  -*- coding: utf-8 -*-

description = 'Setup for the CA1 lift in primary beam and CA2 adjustment motor'

includes = ['monoturm', 'sampletable']
group = 'optional'

# BUS 5 (monoturm)
# channel 1   2   3   4   5   6   7   8
#         ca1 mgx mtx mty mth mtt ms1 saph
#                                     saphire is in saph setup
#             mono stuff is in monoturm setup

# BUS 4 (spare one)
# channel  1     2   3   4   5   6   7   8
#        sth_st  --- --- --- --- --- --- ca2

# eases address settings: 0x5.. = stepper, 0x6.. = poti, 0x7.. = coder ; .. = channel
MOTOR = lambda x: 0x50 + x
POTI = lambda x: 0x60 + x
CODER = lambda x: 0x70 + x

# eases confbyte settings for IPC-coder cards:
ENDAT = 0x80
SSI = 0

GRAY = 0x40
BINARY = 0

P_NONE = 0x20
P_EVEN = 0

TOTALBITS = lambda x: x & 0x1f

devices = dict(
    ca1_mot  = device('devices.vendor.ipc.Motor',
                      description = 'Stepper motor to move the collimator lift',
                      bus = 'bus5',
                      addr = 81,
                      slope = 200.0,
                      unit = 'mm',
                      abslimits = (-1, 760),
                      # negative limit switch was used to reference,
                      zerosteps = 500000,
                      confbyte = 11,
                      speed = 50,
                      accel = 250,
                      microstep = 1,
                      min = 499800,
                      max = 651200,
                     ),
    ca1      = device('devices.generic.Switcher',
                      description = 'Collimator CA1 lift',
                      moveable = 'ca1_mot',
                      mapping = {'none': 0, '20m': 310, '60m': 540, '40m': 755},
                      blockingmove = True,
                      precision = 1,
                     ),


    ca2_mot  = device('devices.vendor.ipc.Motor',
                      description = 'Stepper motor to adjust CA2 collimator',
                      bus = 'bus4',
                      addr = MOTOR(8),
                      slope = 164.0,  #0.0061 mm/1.8deg
                      unit = 'mm',
                      abslimits = (-1, 760),
                      # negative limit switch was used to reference,
                      zerosteps = 500000,
                      confbyte = 11,
                      speed = 50,
                      accel = 250,
                      microstep = 1,
                      min = 400000,
                      max = 600000,
                     ),
)
