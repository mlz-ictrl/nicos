description = 'RESI NICOS startup setup'
group = 'basic'
includes = ['system']#, 'lakeshore', 'cascade', 'detector']
modules = ['nicos_mlz.resi.scan']
devices = dict(
    resi = device('nicos_mlz.resi.devices.residevice.ResiDevice',
                  description = 'main RESI device',
                  unit = 'special',
                 ),
    theta = device('nicos_mlz.resi.devices.residevice.ResiVAxis',
                   description = 'theta axis',
                   basedevice = 'resi',
                   mapped_axis = 'theta',
                   unit='degree',
                  ),
    omega = device('nicos_mlz.resi.devices.residevice.ResiVAxis',
                   description = 'omega axis',
                   basedevice = 'resi',
                   mapped_axis = 'omega',
                   unit='degree',
                  ),
    phi = device('nicos_mlz.resi.devices.residevice.ResiVAxis',
                 description = 'phi axis',
                 basedevice = 'resi',
                 mapped_axis = 'phi',
                 unit='degree',
                ),
    chi = device('nicos_mlz.resi.devices.residevice.ResiVAxis',
                 description = 'chi axis',
                 basedevice = 'resi',
                 mapped_axis = 'chi',
                 unit='degree',
                ),

    Sample = device('nicos_mlz.resi.devices.residevice.ResiSample',
                    description = 'currently used sample',
                    basedevice = 'resi',
                   ),
)

startupcode = '''
hw = resi._hardware
'''
