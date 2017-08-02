description = 'Polarizer devices in the SINQ AMOR.'

devices = dict(
    pby=device('nicos_sinq.amor.devices.epics_amor_magnet.EpicsAmorMagnet',
               epicstimeout=3.0,
               description='Polarizer magnet',
               basepv='SQ:AMOR:PBY',
               pvdelim=':',
               switchpvs={'read': 'SQ:AMOR:PBY:PowerStatusRBV',
                          'write': 'SQ:AMOR:PBY:PowerStatus'},
               switchstates={'on': 1, 'off': 0},
               precision=0.1,
               timeout=None,
               window=5.0,
               ),
)
