description = 'Beam stop device'

group = 'optional'

tango_base = 'tango://phys.treff.frm2:10000/treff/FZJS7/'

devices = dict(
    beamstop = device('nicos.devices.tango.Motor',
                      description = 'Beamstop position',
                      tangodevice = tango_base + 'beamstop',
                      precision = 0.01,
                      unit = 'mm',
                      fmtstr = '%.3f',
                     ),
)
