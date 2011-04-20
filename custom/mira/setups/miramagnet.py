name = 'MIRA electromagnet'

devices = dict(
    I_plus   = device('nicos.io.DigitalOutput',
                      tacodevice = '//magnet2/magnet/switch/on',
                      lowlevel=True),
    I_minus  = device('nicos.io.DigitalOutput',
                      tacodevice = '//magnet2/magnet/switch/pol',
                      lowlevel=True),
    I        = device('nicos.mira.ess.ESSController',
                      tacodevice = '//magnet2/magnet/ess/current',
                      plusswitch = 'I_plus',
                      minusswitch = 'I_minus'),
)
