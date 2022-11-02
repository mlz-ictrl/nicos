description = 'monochromator setup for half resolution'

group = 'lowlevel'

excludes = ['monochromator', 'monochromator_3', 'monochromator_4']

tango_base = 'tango://lahn:10000/andes/'

devices = dict(
    mtt=device('nicos.devices.entangle.Motor',
               description='2 theta axis moving sample table arm',
               tangodevice=tango_base + 'monochromator/mtt',
               fmtstr='%.2f',
               requires={'level': 'admin'},
               userlimits=(70, 110),
               ),
    wavelength=device('nicos_mlz.stressi.devices.wavelength.Wavelength',
                      description='the incoming wavelength',
                      omgm='omgm',
                      base='mtt',
                      crystal='crystal',
                      plane='511',
                      unit='AA',
                      fmtstr='%.2f',
                      abslimits=(1.25, 1.54),
                      requires={'level': 'admin'},
                      ),
)

startupcode = '''
maw(mtt, 70)
'''
