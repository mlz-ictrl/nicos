description = 'Multiplexer device'

group = 'lowlevel'

servername = 'VME'

nameservice = 'stressictrl.stressi.frm2'

devices = dict(
    mux = device('nicos.devices.vendor.caress.MUX',
                 description = 'The famous MUX',
                 nameserver = '%s' % (nameservice,),
                 objname = '%s' % (servername),
                 config = 'MUX3 38 4 ttyS1 1',
                 lowlevel = True,
                 initsleep = 0,
                ),
)
