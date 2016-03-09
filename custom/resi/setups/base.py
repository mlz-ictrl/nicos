description = 'RESI NICOS startup setup'
group = 'basic'
includes = ['system']#, 'lakeshore', 'cascade', 'detector']
modules = ['nicos.resi.scan']
devices = dict(
    resi = device('resi.residevice.ResiDevice',
                  description = 'main RESI device',
                  unit = 'special',
                 ),
    theta = device('resi.residevice.ResiVAxis',
                   description = 'theta axis',
                   basedevice = 'resi',
                   mapped_axis = 'theta',
                   unit='degree',
                  ),
    omega = device('resi.residevice.ResiVAxis',
                   description = 'omega axis',
                   basedevice = 'resi',
                   mapped_axis = 'omega',
                   unit='degree',
                  ),
    phi = device('resi.residevice.ResiVAxis',
                 description = 'phi axis',
                 basedevice = 'resi',
                 mapped_axis = 'phi',
                 unit='degree',
                ),
    chi = device('resi.residevice.ResiVAxis',
                 description = 'chi axis',
                 basedevice = 'resi',
                 mapped_axis = 'chi',
                 unit='degree',
                ),

    Sample = device('resi.residevice.ResiSample',
                    description = 'currently used sample',
                    basedevice = 'resi',
                   ),
)

startupcode = '''
hw = resi._hardware
'''
