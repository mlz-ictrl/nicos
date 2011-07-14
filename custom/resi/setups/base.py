includes = ['system']#, 'lakeshore', 'cascade', 'detector']

devices = dict(
    Sample   = device('nicos.tas.TASSample'),

    resi     = device('nicos.resi.residevice.ResiDevice',
                      unit = 'special'
                      ),
)
