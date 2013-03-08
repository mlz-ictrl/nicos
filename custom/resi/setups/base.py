description = 'RESI NICOS startup setup'
group = 'basic'
includes = ['system']#, 'lakeshore', 'cascade', 'detector']

devices = dict(
    resi = device('resi.residevice.ResiDevice',
                      unit = 'special'),

    Sample = device('resi.residevice.ResiSample',
                            basedevice = 'resi'),
)

startupcode = 'hw=resi._hardware'
