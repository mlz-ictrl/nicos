description = 'Various devices for diaphragms in AMOR'

devices = dict(
    xs = device('test.utils.TestDevice',
        description = 'xs motor',
        # precision = .1,
        unit = 'mm',
        abslimits = (-20, 20),
    ),
    d1t = device('nicos.devices.generic.VirtualMotor',
        description = 'Slit 1 top',
        precision = .1,
        unit = 'mm',
        abslimits = (-20, 20),
    ),
    d1b = device('nicos.devices.generic.VirtualMotor',
        description = 'Slit 1 bottom',
        precision = .1,
        unit = 'mm',
        abslimits = (-20, 20),
    ),
    d1r = device('nicos.devices.generic.VirtualMotor',
        description = 'Slit 1 right',
        precision = .1,
        unit = 'mm',
        abslimits = (-20, 20),
    ),
    d1l = device('nicos.devices.generic.VirtualMotor',
        description = 'Slit 1 left',
        precision = .1,
        unit = 'mm',
        abslimits = (-20, 20),
    ),
    slit1 = device('nicos.devices.generic.slit.Slit',
        description = 'Slit 1 with left, right, bottom and top motors',
        opmode = '4blades',
        left = 'd1l',
        right = 'd1r',
        top = 'd1t',
        bottom = 'd1b',
    ),
    d2t = device('nicos.devices.generic.VirtualMotor',
        description = 'Slit 2 top',
        precision = .1,
        unit = 'mm',
        abslimits = (-20, 20),
    ),
    d2b = device('nicos.devices.generic.VirtualMotor',
        description = 'Slit 2 bottom',
        precision = .1,
        unit = 'mm',
        abslimits = (-20, 20),
    ),
    d2r = device('nicos.devices.generic.VirtualMotor',
        description = 'Slit 2 right',
        precision = .1,
        unit = 'mm',
        abslimits = (-20, 20),
    ),
    d2l = device('nicos.devices.generic.VirtualMotor',
        description = 'Slit 2 left',
        precision = .1,
        unit = 'mm',
        abslimits = (-20, 20),
    ),
    d2z = device('nicos.devices.generic.VirtualMotor',
        description = 'Slit 2 z',
        precision = .1,
        unit = 'mm',
        abslimits = (-20, 20),
    ),
    slit2 = device('nicos.devices.generic.slit.Slit',
        description = 'Slit 2 with left, right, bottom and top motors',
        opmode = '4blades',
        left = 'd2l',
        right = 'd2r',
        top = 'd2t',
        bottom = 'd2b',
    ),
    controller_slm = device('nicos_sinq.amor.devices.slit.AmorSlitHandler',
        description = 'Logical motors controller',
        xs = 'xs',
        slit1 = 'slit1',
        slit2 = 'slit2',
        visibility = (),
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
    d2v = device('nicos_sinq.amor.devices.slit.AmorSlitLogicalMotor',
        description = 'Logical motor vertical divergence',
        motortype = 'd2v',
        controller = 'controller_slm',
        unit = 'mm'
    ),
    d2d = device('nicos_sinq.amor.devices.slit.AmorSlitLogicalMotor',
        description = 'Logical motor ',
        motortype = 'd2d',
        controller = 'controller_slm',
        unit = 'mm'
    ),
    d2h = device('nicos_sinq.amor.devices.slit.AmorSlitLogicalMotor',
        description = 'Logical motor horizontal divergence',
        motortype = 'd2h',
        controller = 'controller_slm',
        unit = 'mm'
    ),
)
