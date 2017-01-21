description = 'Cryopad'

group = 'optional'

includes = ['nutator', 'poli', 'cryopad_currents']

devices = dict(
    Cryopad   = device('poli.cryopad.SXTalCryopad',
                       description = 'Main cryopad device',
                       sxtal = 'POLI',
                       ttheta = 'gamma',
                       nut_in = 'nutator1',
                       prec_in = 'pc1',
                       nut_out = 'nutator2',
                       prec_out = 'pc2',
                       unit = 'deg',
                      ),

    Pin       = device('poli.cryopad.CryopadPol',
                       description = 'Incoming polarization direction',
                       cryopad = 'Cryopad',
                       side = 'in'
                      ),
    Fin       = device('poli.cryopad.CryopadFlip',
                       description = 'Incoming flipping by nutator current',
                       moveable = 'nutator1c',
                       mapping = {'on': -1.75, 'off': 1.75},
                       precision = 0.02,
                       fallback = 'unknown',
                      ),

    Pout      = device('poli.cryopad.CryopadPol',
                       description = 'Outgoing polarization direction',
                       cryopad = 'Cryopad',
                       side = 'out'
                      ),
    Fout      = device('poli.cryopad.CryopadFlip',
                       description = 'Outgoing flipping by nutator current',
                       moveable = 'nutator2c',
                       mapping = {'on': -1.75, 'off': 1.75},
                       precision = 0.02,
                       fallback = 'unknown',
                      ),
)
