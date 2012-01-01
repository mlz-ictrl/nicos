name = 'MIRA electromagnet'

includes = ['base']

devices = dict(
    I_plus   = device('nicos.taco.DigitalOutput',
                      tacodevice = '//magnet2/magnet/switch/on',
                      lowlevel=True),
    I_minus  = device('nicos.taco.DigitalOutput',
                      tacodevice = '//magnet2/magnet/switch/pol',
                      lowlevel=True),
    I        = device('nicos.mira.ess.ESSController',
                      tacodevice = '//magnet2/magnet/ess/current',
                      abslimits = (-250, 250),
                      plusswitch = 'I_plus',
                      minusswitch = 'I_minus'),
)
