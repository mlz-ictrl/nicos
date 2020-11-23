description = 'nGI XinGI setup: Gratings'

group = 'lowlevel'

pvprefix = 'SQ:ICON:ngiX:'

display_order = 35

excludes = ['ngi_backpack']

devices = dict(
    g1_rz = device('nicos_ess.devices.epics.motor.HomingProtectedEpicsMotor',
        epicstimeout = 3.0,
        description = 'nGI Interferometer Grating Rotation G1 (XinGI)',
        motorpv = pvprefix + 'g1rz',
        errormsgpv = pvprefix + 'g1rz-MsgTxt',
        precision = 0.01,
    ),
    g1_tz = device('nicos_ess.devices.epics.motor.HomingProtectedEpicsMotor',
        epicstimeout = 3.0,
        description = 'nGI Interferometer Grating Talbot G1 (XinGI)',
        motorpv = pvprefix + 'g1tz',
        errormsgpv = pvprefix + 'g1tz-MsgTxt',
        precision = 0.01,
    ),
    g1_tzl = device('nicos_ess.devices.epics.motor.HomingProtectedEpicsMotor',
        epicstimeout = 3.0,
        description =
        'nGI Interferometer Grating Talbot G1 - long range  (XinGI)',
        motorpv = pvprefix + 'g1tzl',
        errormsgpv = pvprefix + 'g1tzl-MsgTxt',
        precision = 0.01,
    ),
    g2_rz = device('nicos_ess.devices.epics.motor.HomingProtectedEpicsMotor',
        epicstimeout = 3.0,
        description = 'nGI Interferometer Grating Rotation G2 (XinGI)',
        motorpv = pvprefix + 'g2rz',
        errormsgpv = pvprefix + 'g2rz-MsgTxt',
        precision = 0.01,
    ),
)
