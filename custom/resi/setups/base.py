description = 'RESI NICOS startup setup'
group = 'basic'
includes = ['system']#, 'lakeshore', 'cascade', 'detector']
modules = ['nicos.resi.scan']
devices = dict(
    resi = device('resi.residevice.ResiDevice',
                  unit = 'special',
                 ),
    theta = device('resi.residevice.ResiVAxis',
                   basedevice = 'resi',
                   mapped_axis = 'theta',
                   unit='degree',
                  ),
    omega = device('resi.residevice.ResiVAxis',
                   basedevice = 'resi',
                   mapped_axis = 'omega',
                   unit='degree',
                  ),
    phi = device('resi.residevice.ResiVAxis',
                 basedevice = 'resi',
                 mapped_axis = 'phi',
                 unit='degree',
                ),
    chi = device('resi.residevice.ResiVAxis',
                 basedevice = 'resi',
                 mapped_axis = 'chi',
                 unit='degree',
                ),

    Sample = device('resi.residevice.ResiSample',
                    basedevice = 'resi',
                   ),
)

startupcode = 'hw=resi._hardware'
