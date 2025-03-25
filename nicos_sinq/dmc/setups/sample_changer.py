description = 'Sample changer devices for SINQ DMC.'

pvprefix = 'SQ:DMC:turboPmac2:'

devices = dict(
    chmot = device('nicos_sinq.dmc.devices.changermot.ChangerMotor',
        description = 'Sample changer motor motor',
        motorpv = f'{pvprefix}CHPOS',
        errormsgpv = f'{pvprefix}CHPOS-MsgTxt',
        can_disable = True,
    ),
    chpos = device('nicos.devices.generic.switcher.Switcher',
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
        description = 'Sample changer stick motor',
        motorpv = f'{pvprefix}STICK',
        errormsgpv = f'{pvprefix}STICK-MsgTxt',
        can_disable = True,
    ),
)
