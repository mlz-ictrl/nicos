description = 'monochromator setup for high intensity with PG crystal'

group = 'lowlevel'

excludes = ['monochromator', 'monochromator_2', 'monochromator_3']

tango_base = 'tango://lahn:10000/andes/'

devices = dict(
    mtt=device('nicos.devices.entangle.Motor',
               description='2 theta axis moving sample table arm',
               tangodevice=tango_base + 'monochromator/mtt',
               fmtstr='%.2f',
               requires={'level': 'admin'},
               userlimits=(42, 42),
               ),
    wavelength=device('nicos_mlz.stressi.devices.wavelength.Wavelength',
                      description='the incoming wavelength',
                      omgm='omgm',
                      base='mtt',
                      crystal='crystal',
                      plane='200',
                      unit='AA',
                      fmtstr='%.2f',
                      abslimits=(2.4, 2.4),
                      requires={'level': 'admin'},
                      ),
)

startupcode = '''
maw(mtt, 42)
'''
