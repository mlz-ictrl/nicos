description = 'reactor status devices'

devices = dict(
    Power    = device('devices.taco.AnalogInput',
                      description = 'FRM II reactor power',
                      tacodevice = '//tacodb/frm2/reactor/power',
                      tacotimeout = 0.5,
                      pollinterval = 30,
                      maxage = 3600,
                      fmtstr = '%.1f',
                      unit = 'MW'),
)
