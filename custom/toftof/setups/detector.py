description = 'TOF counter device'

includes = ['system']

devices = dict(
    det = device('nicos.toftof.tofcounter.TofCounter',
                 pollinterval = 0),
)
