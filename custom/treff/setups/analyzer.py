description = 'Analyzer device'

group = 'optional'

taco_base = '//phys.treff.frm2/treff/'

devices = dict(
    anabus          = device('nicos_mlz.treff.devices.ipc.IPCModBusTacoJPB',
                             tacodevice = taco_base + 'goett/480',
                             lowlevel = True,
                            ),
    analyz_tilt_mot = device('nicos.devices.vendor.ipc.Motor',
                             description = 'Analyzer tilt motor',
                             bus = 'anabus',
                             addr = 0,
                             abslimits = (-0.81, 1.9433),
                             unit = 'deg',
                             slope = 30000,
                             speed = 30,
                             zerosteps = 526300,
                             precision = 0.01,
                             lowlevel = True,
                            ),
    analyzer_tilt   = device('nicos.devices.generic.Axis',
                             description = 'Analyzer tilt',
                             motor = 'analyz_tilt_mot',
                             coder = 'analyz_tilt_mot',
                             backlash = 0.007,
                             precision = 0.01,
                             fmtstr = '%.3f',
                            ),
)
