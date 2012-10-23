description = 'Newport sample stick rotator'

includes = ['system']

nethost = "//newport01.toftof.frm2/"
# nethost = "//toftofsrv.toftof.frm2/"

devices = dict(
    stick = device('nicos.taco.Motor',
#                   tacodevice = nethost + 'toftof/stick/motor'),
                   tacodevice = nethost + 'newport/newportmc/motor'),
)
