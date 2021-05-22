description = 'Slit 1 devices in the SINQ AMOR.'

pvprefix = 'SQ:AMOR:motc:'

includes = ['logical_motors']

devices = dict(
    d1l = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Slit 1 left motor',
        motorpv = pvprefix + 'd1l',
        # errormsgpv=pvprefix + 'd1l-MsgTxt',
        lowlevel = True,
    ),
    d1r = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Slit 1 right motor',
        motorpv = pvprefix + 'd1r',
        # errormsgpv=pvprefix + 'd1r-MsgTxt',
        lowlevel = True,
    ),
    d1t = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Slit 1 opening motor',
        motorpv = pvprefix + 'd1t',
        # errormsgpv=pvprefix + 'd1t-MsgTxt',
        lowlevel = True,
    ),
    d1b = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Slit 1 z position (lower edge) motor',
        motorpv = pvprefix + 'd1b',
        # errormsgpv=pvprefix + 'd1b-MsgTxt',
        lowlevel = True,
    ),
    slit1 = device('nicos.devices.generic.slit.Slit',
        description = 'Slit 1 with left, right, bottom and top motors',
        opmode = '4blades',
        left = 'd1l',
        right = 'd1r',
        top = 'd1t',
        bottom = 'd1b',
        lowlevel = True
    ),
    div = device('nicos_sinq.amor.devices.slit.AmorSlitLogicalMotor',
        description = 'Logical motor vertical divergence',
        motortype = 'div',
        controller = 'controller_slm',
        unit = 'mm'
    ),
    did = device('nicos_sinq.amor.devices.slit.AmorSlitLogicalMotor',
        description = 'Logical motor ',
        motortype = 'did',
        controller = 'controller_slm',
        unit = 'mm'
    ),
    dih = device('nicos_sinq.amor.devices.slit.AmorSlitLogicalMotor',
        description = 'Logical motor horizontal divergence',
        motortype = 'dih',
        controller = 'controller_slm',
        unit = 'mm'
    ),
)
