description = 'FRM II neutron guide line 4a shutter'

group = 'lowlevel'

includes = ['guidehall']

nethost = 'tacodb.taco.frm2'

devices = dict(
    NL4a     = device('nicos.taco.NamedDigitalInput',
                      description = 'NL4a shutter status',
                      mapping = {0: 'closed', 1: 'open'},
                      pollinterval = 60,
                      maxage = 120,
                      tacodevice = '//%1/frm2/shutter/nl4a' % (nethost, ),
)
