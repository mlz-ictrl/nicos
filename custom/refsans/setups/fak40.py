description = 'FRM-II FAK40 information'

nethost = '//tacodb.taco.frm2/'

devices = dict(
        fak40cap = device('nicos.taco.io.AnalogInput',
                       tacodevice = nethost + 'frm2/fak40/capacity',
                       lowlevel = False,
                      ),
        fak40press = device('nicos.taco.io.AnalogInput',
                       tacodevice = nethost + 'frm2/fak40/pressure',
                       lowlevel = False,
                      ),
#        fak40 = device('nicos.refsans.fak40',
#                       capacity =
#                       pressure =
#                      )
)
