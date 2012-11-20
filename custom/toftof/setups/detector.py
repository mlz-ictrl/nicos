description = 'TOF counter device'

group = 'basic'

includes = ['system']

devices = dict(
    det = device('toftof.tofcounter.TofCounter',
                 pollinterval = None,
                ),
)
