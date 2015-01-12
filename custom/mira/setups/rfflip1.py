description = 'RF circuit devices for adiabatic flipper on first table'
group = 'optional'

devices = dict(
    amp1     = device('mira.rfcircuit.GeneratorDevice',
                      tacodevice = '//mirasrv/mira/hp33220a_1/amp',
                      abslimits = (0, 1),
                     ),

    freq1    = device('mira.rfcircuit.GeneratorDevice',
                      tacodevice = '//mirasrv/mira/hp33220a_1/freq',
                      fmtstr = '%.0f',
                      abslimits = (0, 80000000),
                     ),

    fp1      = device('devices.taco.AnalogInput',
                      tacodevice = '//mirasrv/mira/ag1016/fp1',
                     ),
    rp1      = device('devices.taco.AnalogInput',
                      tacodevice = '//mirasrv/mira/ag1016/rp1',
                      warnlimits = (0, 20),
                     ),

    Cbox1    = device('mira.beckhoff.DigitalOutput',
                      tacodevice = '//mirasrv/mira/modbus/beckhoff',
                      startoffset = 8,
                      bitwidth = 32,
                     ),
)
