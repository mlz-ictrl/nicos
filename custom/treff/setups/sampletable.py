description = 'Sample table setup'

group = 'lowlevel'

tango_base = 'tango://phys.treff.frm2:10000/treff'
tango_s7 = tango_base + '/FZJS7/'

excludes = ['virtual_sampletable']

devices = dict(
    sample_x = device('devices.tango.Motor',
                      description = 'Sample table x translation',
                      tangodevice = tango_s7 + 'sample_x',
                      precision = 0.01,
                      fmtstr = '%.2f',
                      unit = 'mm',
                     ),
    sample_y = device('devices.tango.Motor',
                      description = 'Sample table y translation',
                      tangodevice = tango_s7 + 'sample_y',
                      precision = 0.01,
                      fmtstr = '%.2f',
                      unit = 'mm',
                     ),
    sample_z = device('devices.tango.Motor',
                      description = 'Sample table z translation',
                      tangodevice = tango_s7 + 'sample_z',
                      precision = 0.01,
                      fmtstr = '%.2f',
                      unit = 'mm',
                     ),
    omega    = device('devices.tango.Motor',
                      description = 'Sample table omega rotation',
                      tangodevice = tango_s7 + 'omega',
                      precision = 0.01,
                      fmtstr = '%.2f',
                      unit = 'deg',
                     ),
    phi      = device('devices.tango.Motor',
                      description = 'Sample table phi rotation',
                      tangodevice = tango_s7 + 'phi',
                      precision = 0.01,
                      fmtstr = '%.2f',
                      unit = 'deg',
                     ),
    chi     = device('devices.tango.Motor',
                     description = 'Sample table chi rotation',
                     tangodevice = tango_s7 + 'chi',
                     precision = 0.01,
                     fmtstr = '%.2f',
                     unit = 'deg',
                    ),
)
