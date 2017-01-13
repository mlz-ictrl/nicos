description = 'SPODI setup'

group = 'lowlevel'

servername = 'VMESPODI'

nameservice = 'spodisrv'

devices = dict(
     mux = device('devices.vendor.caress.MUX',
                  description = 'The famous MUX',
                  nameserver = '%s' % (nameservice,),
                  objname = '%s' % (servername),
                  config = 'MUX3 38 4 ttyS1 1',
                  lowlevel = False,
                 ),
)
