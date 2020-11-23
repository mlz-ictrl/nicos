description = 'Neutron Aperture (NAP) Device'

group = 'lowlevel'

display_order = 5

devices = dict(
    na_selector_pos = device('nicos_ess.devices.epics.motor.HomingProtectedEpicsMotor',
        epicstimeout = 3.0,
        description = 'Rotary position of neutron aperture selector',
        motorpv = 'SQ:ICON:board5:NA',
        errormsgpv = 'SQ:ICON:board5:NA-MsgTxt',
        lowlevel = True,
    ),
    na_selector = device('nicos.devices.generic.Switcher',
        description = 'Selected neutron aperture',
        moveable = 'na_selector_pos',
        mapping = {
            '20 mm (Be filter)': 332000,
            '01 mm': 265500,
            '10 mm': 197000,
            'closed': 163500,
            '20 mm': 130000,
            '40 mm': 63000,
            '80 mm': -4000,
        },
        fallback = 'interstage',
        precision = 10,
    ),
)
