description = 'sample table (external control)'
group = 'lowlevel'

devices = dict(
    phi      = device('devices.taco.HoveringAxis',
                      description = 'sample two-theta angle',
                      tacodevice = '//mirasrv/mira/axis/phi_ext',
                      abslimits = (-120, 120),
                      startdelay = 1,
                      stopdelay = 2,
                      switch = 'air_sample_ana',
                      switchvalues = (0, 1),
                      fmtstr = '%.3f',
                     ),

    air_mono  = device('devices.generic.ManualMove',
                       abslimits = (0, 1),
                       unit = '',
                       lowlevel = True,
                      ),

    air_sample_ana = device('devices.taco.MultiDigitalOutput',
                         outputs = ['air_sample', 'air_ana'],
                         unit = '',
                         lowlevel = True,
                        ),

    air_sample   = device('mira.refcountio.RefcountDigitalOutput',
                        tacodevice = '//mirasrv/mira/phytronio/air_ana_ext',
                        lowlevel = True,
                       ),

    air_ana   = device('devices.taco.DigitalOutput',
                        tacodevice = '//mirasrv/mira/phytronio/air_det_ext',
                        lowlevel = True,
                       ),
)
