description = 'analyzer table'
group = 'lowlevel'

tango_base = 'tango://mira1.mira.frm2:10000/mira/'

includes = ['sample']

devices = dict(
    co_ath   = device('devices.tango.Sensor',
                      tangodevice = tango_base + 'detector/ath_enc',
                      lowlevel = True,
                      unit = 'deg',
                     ),
    mo_ath   = device('devices.tango.Motor',
                      tangodevice = tango_base + 'detector/ath_mot',
                      abslimits = (-180, 180),
                      lowlevel = True,
                      unit = 'deg',
                      precision = 0.005,
                     ),
    ath      = device('devices.generic.Axis',
                      description = 'analyzer theta angle',
                      coder = 'co_ath',
                      motor = 'mo_ath',
                      obs = [],
                      precision = 0.005,
                     ),

    co_att   = device('devices.tango.Sensor',
                      tangodevice = tango_base + 'detector/att_enc',
                      lowlevel = True,
                      unit = 'deg',
                     ),
    mo_att   = device('devices.tango.Motor',
                      tangodevice = tango_base + 'detector/att_mot',
                      abslimits = (-90 -135, -90 + 135),
                      lowlevel = True,
                      unit = 'deg',
                      precision = 0.01,
                     ),
    att      = device('mira.stargate.ATT',
                      description = 'analyzer two-theta angle',
                      stargate = 'stargate',
                      abslimits = (-90 - 135, -90 + 135),
                      motor = 'mo_att',
                      coder = 'co_att',
                      obs = [],
                      startdelay = 1,
                      stopdelay = 2,
                      switch = 'air_ana',
                      switchvalues = (0, 1),
                      fmtstr = '%.3f',
                      precision = 0.01,
                     ),

    ana      = device('devices.tas.Monochromator',
                      description = 'analyzer unit (see ana.unit for setting new unit)',
                      unit = 'A-1',
                      theta = 'ath',
                      twotheta = 'att',
                      focush = None,
                      focusv = None,
                      abslimits = (0.1, 10),
                      dvalue = 3.355,
                      scatteringsense = -1,
                     ),

    stargate = device('mira.stargate.Stargate',
                      description = 'Mira-Stargate (i.e. analyser shielding blocks)',
                      tangodevice = tango_base + 'anablocks/mb1',
                      offset_out = 40003,
                      offset_in = 45395,
                      chevron_att_angles =
                      [
                          [],               # 1
                          [150, 78.5],      # 2,  mid: 120.5
                          [120.5, 62.5],    # 3,  mid: 78.5
                          [78.5, 32.5],     # 4,  mid: 62.5
                          [62.5, 2.],       # 5,  mid: 32.5
                          [32.5, -28],      # 6,  mid: 2
                          [2., -59.5],      # 7,  mid: -28
                          [-28, -90],       # 8,  mid: -59.5
                          [-59.5, -120.5],  # 9,  mid: -90
                          [-90., -150.],    # 10, mid: -120.5
                          [],
                      ],
                     ),
)
