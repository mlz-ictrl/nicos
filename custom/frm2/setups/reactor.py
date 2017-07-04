description = 'FRM II reactor status devices'

group = 'lowlevel'

tango_base = 'tango://ictrlfs.ictrl.frm2:10000/frm2/'

devices = dict(
    ReactorPower = device('devices.tango.AnalogInput',
                          description = 'FRM II reactor power',
                          tangodevice = tango_base + 'reactor/power',
                          warnlimits = (19, 21),
                          fmtstr = '%.1f',
                          pollinterval = 60,
                          maxage = 3600,
                          unit = 'MW'),
)
