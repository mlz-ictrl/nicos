description = 'nGI backpack setup at ICON.'

display_order = 35

pvprefix = 'SQ:ICON:ngiB:'

includes = ['ngi_g0']
excludes = ['ngi_xingi_gratings']

devices = dict(
    g1_rz = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'nGI Interferometer Grating Rotation G1 (Backpack)',
        motorpv = pvprefix + 'g1rz',
        errormsgpv = pvprefix + 'g1rz-MsgTxt',
        precision = 0.01,
    ),
    g1_tz = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'nGI Interferometer Grating Talbot G1 (Backpack)',
        motorpv = pvprefix + 'g1tz',
        errormsgpv = pvprefix + 'g1tz-MsgTxt',
        precision = 0.01,
    ),
    g2_rz = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'nGI Interferometer Grating Rotation G2 (Backpack)',
        motorpv = pvprefix + 'g2rz',
        errormsgpv = pvprefix + 'g2rz-MsgTxt',
        precision = 0.01,
    )
)
