group = 'optional'
description = 'HPE 3631/3 power supplies'

devices = dict(
    Ipol1 = device('mira.heinzinger.HPECurrent',
                   tacodevice = 'mira/network/rs10_6',
                   abslimits = (0, 10),
                  ),
    Ipol2 = device('mira.heinzinger.HPECurrent',
                   tacodevice = 'mira/network/rs10_4',
                   abslimits = (0, 10),
                  ),
)
