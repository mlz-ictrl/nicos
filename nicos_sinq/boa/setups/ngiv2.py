description = 'NIAG NGIV2'

pvprefix = 'SQ:BOA:ngiv2:'

devices = dict(
    sgtx = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'XinGI sample movement X',
        motorpv = pvprefix + 'sgtx',
        errormsgpv = pvprefix + 'sgtx-MsgTxt',
        precision = 0.001
    ),
    sgty = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'XinGI sample movement Y',
        motorpv = pvprefix + 'sgty',
        errormsgpv = pvprefix + 'sgty-MsgTxt',
        precision = 0.001
    ),
    sgtz = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'XinGI sample movement Z',
        motorpv = pvprefix + 'sgtz',
        errormsgpv = pvprefix + 'sgtz-MsgTxt',
        precision = 0.001
    ),
    sgry = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'XinGI sample rotation Y',
        motorpv = pvprefix + 'sgry',
        errormsgpv = pvprefix + 'sgry-MsgTxt',
        precision = 0.001
    ),
    g1tzl = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'XinGI G1 translation Z (long range)',
        motorpv = pvprefix + 'g1tzl',
        errormsgpv = pvprefix + 'g1tzl-MsgTxt',
        precision = 0.001
    ),
    g1tz = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'XinGI G1 translation Z',
        motorpv = pvprefix + 'g1tz',
        errormsgpv = pvprefix + 'g1tz-MsgTxt',
        precision = 0.001
    ),
    g1rz = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'XinGI G1 rotation Z',
        motorpv = pvprefix + 'g1rz',
        errormsgpv = pvprefix + 'g1rz-MsgTxt',
        precision = 0.001
    ),
    g2rz = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'XinGI G2 rotation Z',
        motorpv = pvprefix + 'g2rz',
        errormsgpv = pvprefix + 'g2rz-MsgTxt',
        precision = 0.001
    ),
)
