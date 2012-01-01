name = 'MIEZE devices'

includes = ['startup']
modules = ['nicos.mira.mieze']

devices = dict(

    mieze    = device('nicos.mira.mieze.MiezeMaster',
                      ),

    amp1     = device('nicos.generic.ManualMove',
                      unit = 'V',
                      abslimits = (0, 1)),
    amp2     = device('nicos.generic.ManualMove',
                      unit = 'V',
                      abslimits = (0, 1)),
    amp3     = device('nicos.generic.ManualMove',
                      unit = 'V',
                      abslimits = (0, 1)),

    freq1    = device('nicos.generic.ManualMove',
                      unit = 'Hz',
                      fmtstr = '%.0f',
                      abslimits = (0, 80000000)),
    freq2    = device('nicos.generic.ManualMove',
                      unit = 'Hz',
                      fmtstr = '%.0f',
                      abslimits = (0, 80000000)),
    freq3    = device('nicos.generic.ManualMove',
                      unit = 'Hz',
                      fmtstr = '%.0f',
                      abslimits = (0, 80000000)),

    pk2pk1   = device('nicos.generic.ManualMove',
                      unit = 'A',
                      abslimits = (0, 5)),
    pk2pk2   = device('nicos.generic.ManualMove',
                      unit = 'A',
                      abslimits = (0, 5)),

    curr1    = device('nicos.mira.rfcircuit.RFCurrent',
                      amplitude = 'amp1',
                      readout = 'pk2pk1',
                      abslimits = (0, 5)),
    curr2    = device('nicos.mira.rfcircuit.RFCurrent',
                      amplitude = 'amp2',
                      readout = 'pk2pk2',
                      abslimits = (0, 5)),

    dc1      = device('nicos.generic.ManualMove',
                      unit = 'A',
                      abslimits = (0, 100)),
    dc2      = device('nicos.generic.ManualMove',
                      unit = 'A',
                      abslimits = (0, 100)),

    Cbox1    = device('nicos.generic.ManualSwitch',
                      states = []),
    Cbox2    = device('nicos.generic.ManualSwitch',
                      states = []),

   # fp1       = device('nicos.taco.AnalogInput',
   #                    tacodevice = '//mira4/mira/ag1016/fp01'),
   # rp1       = device('nicos.taco.AnalogInput',
   #                    tacodevice = '//mira4/mira/ag1016/rp01'),
   # fp2       = device('nicos.taco.AnalogInput',
   #                    tacodevice = '//mira4/mira/ag1016/fp02'),
   # rp2       = device('nicos.taco.AnalogInput',
   #                    tacodevice = '//mira4/mira/ag1016/rp02'),
)
