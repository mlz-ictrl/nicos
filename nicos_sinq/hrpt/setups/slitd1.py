description = 'D1 Slit at HRPT'

pvprefix = 'SQ:HRPT:motb:'

devices = dict(
    d1r = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'D1 Slit Right Blade',
        motorpv = pvprefix + 'D1R',
        errormsgpv = pvprefix + 'D1R-MsgTxt',
        precision = 0.01,
    ),
    d1l = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'D1 Slit Left Blade',
        motorpv = pvprefix + 'D1L',
        errormsgpv = pvprefix + 'D1L-MsgTxt',
        precision = 0.01,
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
    slit1_width=device('nicos.devices.generic.ParamDevice',
                       parameter = 'width',
                       device = 'slit1',
                       description = 'Slit1 width',
                       copy_status = True
    ),
)
