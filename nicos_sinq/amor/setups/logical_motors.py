description = 'Various virtual/logical motors in AMOR'

group = 'lowlevel'

devices = dict(
    controller_slm = device('nicos_sinq.amor.devices.slit.AmorSlitHandler',
        description = 'Logical motors controller',
        xs = 'xs',
        slit1 = 'slit1',
        slit2 = 'slit2',
        slit2z = 'slit2z',
        slit3 = 'slit3',
        slit3z = 'slit3z',
        lowlevel = True
    ),
)
