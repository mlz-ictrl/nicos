description = 'TOF counter device'

group = 'lowlevel'

includes = ['system']

devices = dict(
    det = device('toftof.tofcounter.TofCounter',
                 pollinterval = None,
                ),
)
