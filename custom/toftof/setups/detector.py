description = 'TOF counter device'

includes = ['system']

devices = dict(
    det = device('toftof.tofcounter.TofCounter',
                 pollinterval = None),
)
