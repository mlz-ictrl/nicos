description = 'TOF counter device'

group = 'lowlevel'

includes = []

devices = dict(
    det = device('toftof.tofcounter.TofCounter',
                 description = 'TOF detector',
                 pollinterval = None,
                ),
)
