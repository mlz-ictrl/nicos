description = 'chopper vacuum readout'
includes = ['system']

devices = dict(
    vacbus = device('nicos.toftof.toni.ModBus',
                    tacodevice = '//toftofsrv/toftof/rs232/ifvacuumcontrol',
                    lowlevel = True),
    vac0   = device('nicos.toftof.toni.Vacuum',
                    bus = 'vacbus',
                    addr = 0xF0,
                    channel = 0),
    vac1   = device('nicos.toftof.toni.Vacuum',
                    bus = 'vacbus',
                    addr = 0xF0,
                    channel = 1),
    vac2   = device('nicos.toftof.toni.Vacuum',
                    bus = 'vacbus',
                    addr = 0xF0,
                    channel = 2),
    vac3   = device('nicos.toftof.toni.Vacuum',
                    bus = 'vacbus',
                    addr = 0xF0,
                    channel = 3),
)
