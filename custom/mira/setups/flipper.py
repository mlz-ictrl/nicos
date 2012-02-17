description = 'RF circuit devices for adiabatic flipper'
group = 'optional'

devices = dict(
    amp1     = device('nicos.mira.rfcircuit.GeneratorDevice',
                      tacodevice = 'mira/hp33220a_1/amp',
                      abslimits = (0, 1)),

    freq1    = device('nicos.mira.rfcircuit.GeneratorDevice',
                      tacodevice = 'mira/hp33220a_1/freq',
                      fmtstr = '%.0f',
                      abslimits = (0, 80000000)),
)
