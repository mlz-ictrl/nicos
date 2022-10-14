description = 'monochromator setup for high intensity with PG crystal'

group = 'lowlevel'

excludes = ['monochromator', 'monochromator_2', 'monochromator_3']

tango_base = 'tango://lahn:10000/andes/'

devices = dict(
    crystal_m=device('nicos.devices.entangle.Motor',
                     description='monochromator exchange translation',
                     tangodevice=tango_base + 'exchange/z',
                     userlimits=(150, 150),
                     visibility=(),
                     ),
    crystal=device('nicos.devices.generic.Switcher',
                   description='monochromator exchange',
                   moveable='crystal_m',
                   mapping={
                       'PG': 150,
                   },
                   precision=0.1,
                   fmtstr='%.1f',
                   requires={'level': 'admin'},
                   ),
    mtt=device('nicos.devices.entangle.Motor',
               description='2 theta axis moving sample table arm',
               tangodevice=tango_base + 'monochromator/mtt',
               fmtstr='%.2f',
               requires={'level': 'admin'},
               uselimits=(42, 42),
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
maw(crystal, 'PG', mtt, 42)
'''
