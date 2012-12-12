description = 'RESI NICOS startup setup'
group = 'basic'
includes = ['system']#, 'lakeshore', 'cascade', 'detector']

devices = dict(
    Sample = device('devices.tas.TASSample'),

    resi = device('resi.residevice.ResiDevice',
                      unit = 'special'
                      ),
)

startupcode = 'hw=resi._hardware'
