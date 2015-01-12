description = 'RF circuit devices for adiabatic flipper on second table'
group = 'optional'

devices = dict(
    amp2     = device('mira.rfcircuit.GeneratorDevice',
                      tacodevice = '//mirasrv/mira/hp33220a_2/amp',
                      abslimits = (0, 1)),

    freq2    = device('mira.rfcircuit.GeneratorDevice',
                      tacodevice = '//mirasrv/mira/hp33220a_2/freq',
                      fmtstr = '%.0f',
                      abslimits = (0, 80000000)),

    fp2      = device('devices.taco.AnalogInput',
                      tacodevice = '//mirasrv/mira/ag1016/fp2'),
    rp2      = device('devices.taco.AnalogInput',
                      tacodevice = '//mirasrv/mira/ag1016/rp2',
                      warnlimits = (0, 20)),

    Cbox2    = device('mira.beckhoff.DigitalOutput',
                      tacodevice = '//mirasrv/mira/modbus/beckhoff',
                      startoffset = 40,
                      bitwidth = 32),
)
