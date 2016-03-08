description = 'sample table (external control)'
group = 'lowlevel'

excludes = ['sample']

tango_base = 'tango://mira1.mira.frm2:10000/mira/'

devices = dict(
    co_stt   = device('devices.tango.Sensor',
                      lowlevel = True,
                      tangodevice = tango_base + 'sample/phi_ext_enc',
                      unit = 'deg',
                     ),
    mo_stt   = device('devices.tango.Motor',
                      lowlevel = True,
                      tangodevice = tango_base + 'sample/phi_ext_mot',
                      abslimits = (-120, 120),
                      unit = 'deg',
                      precision = 0.002,
                     ),
    stt      = device('mira.axis.HoveringAxis',
                      description = 'sample two-theta angle',
                      abslimits = (-120, 120),
                      motor = 'mo_stt',
                      coder = 'co_stt',
                      obs = [],
                      startdelay = 1,
                      stopdelay = 2,
                      switch = 'air_sample_ana',
                      switchvalues = (0, 1),
                      fmtstr = '%.3f',
                      precision = 0.002,
                     ),

    air_mono  = device('devices.generic.ManualMove',
                       abslimits = (0, 1),
                       unit = '',
                       lowlevel = True,
                      ),

    air_sample_ana = device('mira.refcountio.MultiDigitalOutput',
                         outputs = ['air_sample', 'air_ana'],
                         unit = '',
                         lowlevel = True,
                        ),

    air_sample   = device('mira.refcountio.RefcountDigitalOutput',
                        tangodevice = tango_base + 'air/sample_ext',
                        lowlevel = True,
                       ),

    air_ana   = device('devices.tango.DigitalOutput',
                        tangodevice = tango_base + 'air/det_ext',
                        lowlevel = True,
                       ),
)
