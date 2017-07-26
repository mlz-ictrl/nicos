description = 'Beam stop device'

group = 'optional'

taco_base = '//phys.treff.frm2/treff/'

devices = dict(
    beambus      = device('nicos_mlz.treff.devices.ipc.IPCModBusTacoJPB',
                          tacodevice = taco_base + 'goett/490',
                          lowlevel = True,
                         ),
    beamstop_mot = device('nicos_mlz.treff.devices.ipc.Motor',
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
    beamstop     = device('nicos.devices.generic.Axis',
                          description = 'Beamstop position',
                          motor = 'beamstop_mot',
                          coder = 'beamstop_mot',
                          backlash = 0.11,
                          precision = 0.01,
                          fmtstr = '%.3f',
                         ),
)
