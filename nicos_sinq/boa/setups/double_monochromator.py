description = 'BOA Double Monochromator'

pvprefix = 'SQ:BOA:turboPmac2:'

excludes = [
    'imaging_double_mono',
]

devices = dict(
    mth1 = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Double Monochromator Blade 1 Rotation',
        motorpv = pvprefix + 'MTH1',
    ),
    mth2 = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Double Monochromator Blade 2 Rotation',
        motorpv = pvprefix + 'MTH2',
    ),
    mtx = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Double Monochromator Translation',
        motorpv = pvprefix + 'MTX',
    ),
    wavelength = device('nicos_sinq.devices.doublemono.DoubleMonochromator',
        description = 'SINQ Double Monochromator',
        unit = 'A',
        safe_position = 20.,
        dvalue = 3.335,
        distance = 100.,
        abslimits = (2.4, 6.2),
        mth1 = 'mth1',
        mth2 = 'mth2',
        mtx = 'mtx',
        precision = .01,
    ),
)
