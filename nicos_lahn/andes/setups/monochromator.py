description = 'monochromator setup for tension scanner'

group = 'lowlevel'

excludes = ['monochromator_2', 'monochromator_3', 'monochromator_4']

tango_base = 'tango://lahn:10000/andes/'

devices = dict(
    mtt=device('nicos.devices.entangle.Motor',
               description='2 theta axis moving sample table arm',
               tangodevice=tango_base + 'monochromator/mtt',
               fmtstr='%.2f',
               requires={'level': 'admin'},
               userlimits=(40, 95),
               ),
    wavelength=device('nicos_mlz.stressi.devices.wavelength.Wavelength',
                      description='the incoming wavelength',
                      omgm='omgm',
                      base='mtt',
                      crystal='crystal',
                      plane='400',
                      unit='AA',
                      fmtstr='%.2f',
                      abslimits=(1.5, 1.9),
                      requires={'level': 'admin'},
                      ),
)

startupcode = '''
maw(mtt, 40)
'''
