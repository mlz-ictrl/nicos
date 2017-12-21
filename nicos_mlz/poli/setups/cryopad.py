description = 'Cryopad'

group = 'basic'

includes = ['nutator', 'cryopad_currents', 'hecells', 'table_lifting_virtual']

devices = dict(
    Cryopad = device('nicos_mlz.poli.devices.cryopad.SXTalCryopad',
        description = 'Main cryopad device',
        sxtal = 'POLI',
        ttheta = 'gamma',
        nut_in = 'nutator1',
        prec_in = 'pc1',
        nut_out = 'nutator2',
        prec_out = 'pc2',
        unit = 'deg',
    ),
    Pin = device('nicos_mlz.poli.devices.cryopad.CryopadPol',
        description = 'Incoming polarization direction',
        cryopad = 'Cryopad',
        side = 'in'
    ),
    Fin = device('nicos_mlz.poli.devices.cryopad.CryopadFlip',
        description = 'Incoming flipping by nutator current',
        moveable = 'nutator1c',
        mapping = {'on': -1.75,
                   'off': 1.75},
        precision = 0.02,
        fallback = 'unknown',
    ),
    Pout = device('nicos_mlz.poli.devices.cryopad.CryopadPol',
        description = 'Outgoing polarization direction',
        cryopad = 'Cryopad',
        side = 'out'
    ),
    Fout = device('nicos_mlz.poli.devices.cryopad.CryopadFlip',
        description = 'Outgoing flipping by nutator current',
        moveable = 'nutator2c',
        mapping = {'on': -1.75,
                   'off': 1.75},
        precision = 0.02,
        fallback = 'unknown',
    ),
)
