description = 'Beam stop device'

group = 'optional'

taco_base = '//phys.treff.frm2/treff/'

excludes = ['virtual_beamstop']

devices = dict(
    beambus      = device('treff.ipc.IPCModBusTacoJPB',
                          tacodevice = taco_base + 'goett/490',
                          lowlevel = True,
                         ),
    beamstop_mot = device('treff.ipc.Motor',
                          description = 'Beam stop motor',
                          bus = 'beambus',
                          addr = 0,
                          abslimits = (-0.1, 42),
                          slope = 1821.41,
                          zerosteps = 420496,
                          speed = 130,
                          refsteps = 495478,
                          limitdist = 900,
                          refspeed = 110,
                          unit = 'mm',
                          lowlevel = True,
                         ),
    beamstop     = device('devices.generic.Axis',
                          description = 'Beamstop position',
                          motor = 'beamstop_mot',
                          coder = 'beamstop_mot',
                          backlash = 0.11,
                          precision = 0.01,
                          fmtstr = '%.3f',
                         ),
)
