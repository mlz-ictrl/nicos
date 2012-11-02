description = 'FRM-II FAK40 information'

nethost = '//tacodb.taco.frm2/'

devices = dict(
        fak40cap = device('devices.taco.io.AnalogInput',
                       tacodevice = nethost + 'frm2/fak40/capacity',
                       lowlevel = False,
                      ),
        fak40press = device('devices.taco.io.AnalogInput',
                       tacodevice = nethost + 'frm2/fak40/pressure',
                       lowlevel = False,
                      ),
#        fak40 = device('refsans.fak40',
#                       capacity =
#                       pressure =
#                      )
)
