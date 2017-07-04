description = 'Setup for the pressure cell'

group = 'optional'

excludes = ['pressure']

tango_base = 'tango://tofhw.toftof.frm2:10000/toftof/'

devices = dict(
    P = device('nicos.devices.tango.Sensor',
               description = 'Sample cell pressure',
               tangodevice = tango_base + 'samplecell/pressure',
               fmtstr = '%.0f',
              ),
)
