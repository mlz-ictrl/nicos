description = 'Radialcollimator CARESS HWB xDevices'

group = 'optional'

tango_base = 'tango://motorbox03.stressi.frm2.tum.de:10000/box/'

devices = dict(
    rcdet_m = device('nicos.devices.tango.Motor',
        tangodevice = tango_base + 'channel7/motor',
        fmtstr = '%.3f',
	lowlevel = True,
    ),
    rcdet_c = device('nicos.devices.tango.Sensor',
        tangodevice = tango_base + 'channel7/coder',
        fmtstr = '%.3f',
        lowlevel = True,
    ),
    rcdet = device('nicos.devices.generic.Axis',
        description = 'RadColli=ZE',
        fmtstr = '%.3f',
        motor = 'rcdet_m',
        coder = 'rcdet_c',
        precision = 0.01,
    ),
    rad_fwhm = device('nicos.devices.generic.ManualMove',
        description = 'FWHM Radialcollimator',
        fmtstr = '%.1f',
        default = 5,
        unit = 'mm',
        abslimits = (0, 20),
        requires = {'level': 'admin'},
    ),
)
