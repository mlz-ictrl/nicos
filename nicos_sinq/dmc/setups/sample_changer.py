description = 'Sample changer devices for SINQ DMC.'

pvprefix = 'SQ:DMC:turboPmac2'

devices = dict(
    chmot = device('nicos_sinq.devices.epics.sinqmotor_deprecated.SinqMotor',
        description = 'Sample changer motor motor',
        motorpv = f'{pvprefix}:CHPOS',
    ),
    chpos = device('nicos_sinq.dmc.devices.changermot.CHSwitcher',
        description = 'Sample changer choice',
        moveable = 'chmot',
        mapping = {
            '1': 0,
            '2': 72,
            '3': 144,
            '4': 216,
            '5': 288,
        },
        precision = 1,
    ),
    chstick = device('nicos_sinq.dmc.devices.changermot.StickMotor',
        description = 'Sample changer stick motor (Positioning Mode)',
        motorpv = f'{pvprefix}:STICK',
        switcher = 'stick_mode',
    ),
    chstickvelo = device('nicos_sinq.dmc.devices.changermot.StickMotorVelo',
        description = 'Sample changer stick motor (Velocity Mode)',
        motorpv = f'{pvprefix}:STICK',
    ),
    stick_mode = device('nicos_sinq.dmc.devices.changermot.StickModeSwitcher',
        description = 'Device to control switching between Positioning and Velocity mode.',
        position = 'chstick',
        velocity = 'chstickvelo',
    ),
)
