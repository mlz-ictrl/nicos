description = 'RF circuit devices for adiabatic flipper on first table'

group = 'optional'

excludes = ['mieze']

devices = dict(
    amp1     = device('mira.rfcircuit.GeneratorDevice',
                      description = 'amplitude of first function generator',
                      tacodevice = '//mirasrv/mira/hp33220a_1/amp',
                      abslimits = (0, 1),
                     ),

    freq1    = device('mira.rfcircuit.GeneratorDevice',
                      description = 'frequency of first function generator',
                      tacodevice = '//mirasrv/mira/hp33220a_1/freq',
                      fmtstr = '%.0f',
                      abslimits = (0, 80000000),
                     ),

    fp1      = device('devices.taco.AnalogInput',
                      description = 'forward power in first RF amplifier',
                      tacodevice = '//mirasrv/mira/ag1016/fp1',
                     ),
    rp1      = device('devices.taco.AnalogInput',
                      description = 'reverse power in first RF amplifier',
                      tacodevice = '//mirasrv/mira/ag1016/rp1',
                      warnlimits = (0, 20),
                     ),

    Cbox1    = device('mira.beckhoff.DigitalOutput',
                      description = 'first capacitor box',
                      tangodevice = 'tango://mira1.mira.frm2:10000/mira/beckhoff/beckhoff1',
                      startoffset = 8,
                      bitwidth = 32,
                     ),
)
