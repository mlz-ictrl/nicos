description = 'Vacuum sensors of sample chamber'

# group = 'vacuum'
group = 'basic'

# includes = ['system']
includes = []

nethost = 'pgaasrv.pgaa.frm2'

devices = dict(
    chamber_pressure = device('devices.taco.AnalogInput',
                              description = 'vacuum sensor in sample chamber',
                              tacodevice = '//%s/pgaa/sample/vacuum' % (nethost,),
                              fmtstr = '%9.2E',
                              pollinterval = 15,
                              maxage = 60,
                              warnlimits = (None, 1),
                             ),
)
