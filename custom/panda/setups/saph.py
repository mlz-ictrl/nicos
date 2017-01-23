#  -*- coding: utf-8 -*-

description = 'Setup for the Saphire Filter in primary beam'

includes = ['monoturm']
group = 'optional'


devices = dict(
    saph_mot = device('devices.vendor.ipc.Motor',
                      description = 'Motor to move the saphire filter',
                      bus = 'bus5',
                      #addr = 66, #old rack, old connectors
                      addr = 88,
                      slope = 412.8,
                      unit = 'mm',
                      abslimits = (-133.4, 120),
                      # negative limit switch was used to reference,
                      # reference position is -133.4
                      # almost certainly the positive limit switch comes around 120mm + \epsilon
                      # so one can check if microsteps + slope is set correctly...
                      zerosteps = 500000,
                      confbyte = 8, # read out from card
                      speed = 80,# read out from card
                      accel = 20,# read out from card
                      microstep = 2,# read out from card
                      min = 444930, # lower refpos. taken from old config
                      max = 520640, # read out from card
                     ),
    saph = device('devices.generic.Switcher',
                  description = 'saphire filter',
                  moveable = 'saph_mot',
                  mapping = { 'in' : -133, 'out' : -8},
                  blockingmove = True,
                  precision = 1,
                 ),
)
