description = 'D1 Slit at HRPT'

pvprefix = 'SQ:HRPT:motb:'

devices = dict(
    d1r = device('nicos.devices.epics.pyepics.motor.EpicsMotor',
        description = 'D1 Slit Right Blade',
        motorpv = pvprefix + 'D1R',
        errormsgpv = pvprefix + 'D1R-MsgTxt',
        precision = 0.01,
        abslimits = (0.0, 341.0),
    ),
    d1l = device('nicos.devices.epics.pyepics.motor.EpicsMotor',
        description = 'D1 Slit Left Blade',
        motorpv = pvprefix + 'D1L',
        errormsgpv = pvprefix + 'D1L-MsgTxt',
        precision = 0.01,
        abslimits = (0, 341.0),
    ),
    slit1 = device('nicos_sinq.hrpt.devices.slit.Gap',
        description = 'Slit 1 controller',
        left = 'd1l',
        right = 'd1r',
        unit = 'mm',
        opmode = 'centered',
        coordinates = 'opposite',
        conversion_factor = 22.66
    ),
    slit1_width = device('nicos.core.device.DeviceAlias',
        description = 'slit  1 width',
        alias = 'slit1.width',
        devclass = 'nicos_sinq.hrpt.devices.slit.WidthGapAxis'
    ),
)

startupcode = """
slit1_width.alias='slit1.width'
"""
