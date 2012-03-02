description = 'FRM-II reactor information'

nethost = '//tacodb.taco.frm2/'

devices = dict(
        power = device('nicos.taco.io.AnalogInput',
                       description = 'FRM II reactor power',
                       tacodevice = nethost + 'frm2/reactor/power',
                       tacotimeout = 0.5,
                       pollinterval = 600,
                       maxage = 3600,
                       fmtstr = '%.1f',
                       unit = 'MW'
                      ),
)
