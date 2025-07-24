description = 'Devices for the Beamstop'

group = 'lowlevel'

pvprefix = 'SQ:SANS:mota:'

devices = dict(
    bsy = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Beamstop Y Translation',
        motorpv = pvprefix + 'bsY',
        errormsgpv = pvprefix + 'bsY-MsgTxt',
        precision = 0.2,
    ),
    bsx = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Beamstop X Translation',
        motorpv = pvprefix + 'bsX',
        errormsgpv = pvprefix + 'bsX-MsgTxt',
        precision = 0.2,
    ),
    bs = device('nicos_sinq.sans.devices.beamstop.Beamstop',
        description = 'Device for moving the beamstop in/out',
        x = 'bsx',
        y = 'bsy'
    ),
    spsio = device('nicos_sinq.devices.epics.generic.EpicsArrayReadable',
        description = 'Digital Input from SPS',
        readpv = 'SQ:SANS:SPS1:DigitalInput',
        count = 3,
    ),
    bsc = device('nicos_sinq.sans.devices.beamstop.BeamstopChanger',
        description = 'Device for changing the beamstop',
        x = 'bsx',
        y = 'bsy',
        io = 'spsio'
    ),
)
