description = 'Sample position 2 motorization'

display_order = 30

pvprefix = 'SQ:NEUTRA:turboPmacSample:'
devices = dict(
    focus_maxi = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Camera box translation',
        motorpv = pvprefix + 'camera',
    ),
    xray_tx = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'X-ray, Translation X',
        motorpv = pvprefix + 'xray_tx',
    ),
    xray_tx_switch = device('nicos.devices.generic.Switcher',
        description = 'Selected neutron aperture',
        moveable = 'xray_tx',
        mapping = {
            'Fully in beam': 530,
            'Fully out of beam': 0,
        },
        fallback = 'in-between',
        precision = 0.2,
    ),

)
