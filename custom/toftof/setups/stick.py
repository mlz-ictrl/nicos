description = 'Newport sample stick rotator'

group = 'optional'

includes = ['system']

nethost = 'newport01.toftof.frm2'
# nethost = 'toftofsrv.toftof.frm2'

devices = dict(
    stick = device('devices.taco.Motor',
#                  tacodevice = nethost + 'toftof/stick/motor'),
                   tacodevice = '//%s/newport/newportmc/motor' % (nethost,),
                  ),
)
