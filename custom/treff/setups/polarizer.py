# -*- coding: utf-8 -*-

description = 'Polarizer motor devices and flipper'
group = 'optional'

taco_base = '//phys.treff.frm2/treff/'
tango_base = 'tango://phys.treff.frm2:10000/treff/'

excludes = ["virtual_polarizer"]

devices = dict(
    pflipper       = device('devices.tango.NamedDigitalOutput',
                            description = "Flipper",
                            tangodevice = tango_base + 'FZJDP_Digital/pflipper',
                            mapping = {
                                      'up': 0,
                                      'down': 1,
                                      }
                           ),
    polbus1        = device('treff.ipc.IPCModBusTacoJPB',
                            tacodevice = taco_base + 'goett/340',
                            lowlevel = True,
                           ),
    pol_tilt_mot   = device('devices.vendor.ipc.Motor',
                            description = 'Polarizer tilt motor',
                            bus = 'polbus1',
                            addr = 0,
                            abslimits = (-6.40001, 3.59999),
                            slope = -1821.41,
                            zerosteps = 497450,
                            speed = 20,
                            unit = 'deg',
                            precision = 0.01,
                            lowlevel = True,
                           ),
    polarizer_tilt = device('devices.generic.Axis',
                            description = 'Polarizer tilt',
                            motor = 'pol_tilt_mot',
                            coder = 'pol_tilt_mot',
                            backlash = 0.494,
                            precision = 0.01,
                            fmtstr = '%.3f',
                           ),
    polbus2        = device('treff.ipc.IPCModBusTacoJPB',
                            tacodevice = taco_base + 'goett/330',
                            lowlevel = True,
                           ),
    pol_y_mot      = device('treff.ipc.Motor',
                            description = 'Polarizer y translation motor',
                            abslimits = (-36.0, 57.),
                            bus = 'polbus2',
                            addr = 0,
                            slope = 100,
                            zerosteps = 500000,
                            speed = 16,
                            refsteps = 500000,
                            limitdist = 1000,
                            refspeed = 10,
                            precision = 0.01,
                            unit = 'mm',
                            lowlevel = True,
                           ),
    polarizer_y    = device('devices.generic.Axis',
                            description = 'Polarizer y translation',
                            motor = 'pol_y_mot',
                            coder = 'pol_y_mot',
                            backlash = 0.5,
                            precision = 0.01,
                            fmtstr = '%.2f',
                           ),
)
