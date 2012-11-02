description = 'MIRA 0.5 T electromagnet'
group = 'optional'

includes = ['base']

devices = dict(
    I_plus   = device('devices.taco.DigitalOutput',
                      tacodevice = '//magnet2/magnet/switch/on',
                      lowlevel=True),
    I_minus  = device('devices.taco.DigitalOutput',
                      tacodevice = '//magnet2/magnet/switch/pol',
                      lowlevel=True),
    I        = device('mira.ess.ESSController',
                      description = 'magnet current',
                      tacodevice = '//magnet2/magnet/ess/current',
                      abslimits = (-250, 250),
                      plusswitch = 'I_plus',
                      minusswitch = 'I_minus',
                      fmtstr = '%.1f'),
)
