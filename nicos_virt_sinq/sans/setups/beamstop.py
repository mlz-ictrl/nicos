description = 'Devices for the Beamstop'

group = 'lowlevel'

devices = dict(
    bsx = device('nicos.devices.generic.VirtualMotor',
        description = 'Beamstop X Translation',
        precision = 0.2,
        unit = 'mm',
        abslimits = (-471.5, 28.5),
        speed = 2000,
    ),
    bsy = device('nicos.devices.generic.VirtualMotor',
        description = 'Beamstop Y Translation',
        precision = 0.2,
        unit = 'mm',
        abslimits = (-551.313, 274.687),
        speed = 2000,
    ),
    bs = device('nicos_sinq.sans.devices.beamstop.Beamstop',
        description = 'Device for moving the beamstop in/out',
        x = 'bsx',
        y = 'bsy'
    ),
    spsio = device('nicos_virt_sinq.devices.io.ArrayReadable',
        description = 'Digital Input from SPS',
        count = 3,
    ),
    bsc = device('nicos_sinq.sans.devices.beamstop.BeamstopChanger',
        description = 'Device for changing the beamstop',
        x = 'bsx',
        y = 'bsy',
        io = 'spsio',
        fmtstr = '%d',
    ),
)
