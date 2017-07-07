description = 'RF circuit devices for adiabatic flipper on second table'

group = 'optional'

excludes = ['mieze']

tango_base = 'tango://mira1.mira.frm2:10000/mira/'

devices = dict(
    amp2     = device('nicos_mlz.mira.rfcircuit.GeneratorDevice',
                      description = 'amplitude of second function generator',
                      tacodevice = '//mirasrv/mira/hp33220a_2/amp',
                      abslimits = (0, 1),
                     ),

    freq2    = device('nicos_mlz.mira.rfcircuit.GeneratorDevice',
                      description = 'frequency of second function generator',
                      tacodevice = '//mirasrv/mira/hp33220a_2/freq',
                      fmtstr = '%.0f',
                      abslimits = (0, 80000000),
                     ),

    fp2      = device('nicos.devices.taco.AnalogInput',
                      description = 'forward power in second RF amplifier',
                      tacodevice = '//mirasrv/mira/ag1016/fp2',
                     ),

    rp2      = device('nicos.devices.taco.AnalogInput',
                      description = 'reverse power in second RF amplifier',
                      tacodevice = '//mirasrv/mira/ag1016/rp2',
                      warnlimits = (0, 20),
                     ),

    Cbox2    = device('nicos_mlz.mira.beckhoff.DigitalOutput',
                      description = 'second capacitor box',
                      tangodevice = tango_base + 'beckhoff/beckhoff1',
                      startoffset = 40,
                      bitwidth = 32,
                     ),
)
