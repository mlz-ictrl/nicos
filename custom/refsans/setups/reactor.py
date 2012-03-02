description = 'FRM-II reactor information'

nethost = '//tacodb.taco.frm2/'

devices = dict(
        power = device('nicos.taco.io.AnalogInput',
                       tacodevice = nethost + 'frm2/reactor/power',
                      ),
)
