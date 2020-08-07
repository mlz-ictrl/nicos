description = 'Devices for the emagnet SANS sample holder'

pvprefix = 'SQ:SANS:mota:'

excludes = ['sample']

devices = dict(
    mz = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Sample Table Height',
        motorpv = pvprefix + 'mz',
        errormsgpv = pvprefix + 'mz-MsgTxt',
        precision = 0.01,
    ),
    mom = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Sample table Rotation',
        motorpv = pvprefix + 'mom',
        errormsgpv = pvprefix + 'mom-MsgTxt',
        precision = 0.01,
    ),
)
