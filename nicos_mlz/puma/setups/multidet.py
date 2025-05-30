description = 'Multidetector motors'

includes = ['system', 'motorbus10', 'cad']

group = 'lowlevel'

modules = ['nicos_mlz.puma.commands']

inner_slope = 4061.72
outer_slope = 4709.53
rd_refswitch = 'high'
rd_refdirection = 'upper'
rd_zerosteps = 500000
rd_refstep = 500
rd_inner_speed = 65
rd_outer_speed = 77

rg_slope = -948
rg_refswitch = 'high'
rg_refdirection = 'lower'
rg_zerosteps = 500000
rg_refstep = 100

vis = ('metadata', 'devlist', 'namespace')

devices = dict(
    # Detectors
    st_rd11 = device('nicos_mlz.puma.devices.ReferenceMotor',
        bus = 'motorbus10',
        addr = 71,
        slope = inner_slope,
        unit = 'deg',
        abslimits = (-40.0, -13.0), #-40.0 # all rds decreased 2 deg absmin for neutron offset make up AM 08SEP2018
        refpos = 446036, # 446056
        zerosteps = rd_zerosteps,
        refswitch = rd_refswitch,
        refdirection = rd_refdirection,
        refstep = rd_refstep,
        speed = rd_inner_speed,
        visibility = (),
    ),
    st_rd10 = device('nicos_mlz.puma.devices.ReferenceMotor',
        bus = 'motorbus10',
        addr = 73,
        slope = outer_slope,
        unit = 'deg',
        abslimits = (-37.5, -10.6),
        refpos = 448958, # 448817
        zerosteps = rd_zerosteps,
        refswitch = rd_refswitch,
        refdirection = rd_refdirection,
        refstep = rd_refstep,
        speed = rd_outer_speed,
        visibility = (),
    ),
    st_rd9 = device('nicos_mlz.puma.devices.ReferenceMotor',
        bus = 'motorbus10',
        addr = 75,
        slope = inner_slope,
        unit = 'deg',
        abslimits = (-35.0, -8.2),
        refpos = 465934, # 465914
        zerosteps = rd_zerosteps,
        refswitch = rd_refswitch,
        refdirection = rd_refdirection,
        refstep = rd_refstep,
        speed = rd_inner_speed,
        visibility = (),
    ),
    st_rd8 = device('nicos_mlz.puma.devices.ReferenceMotor',
        bus = 'motorbus10',
        addr = 77,
        slope = outer_slope,
        unit = 'deg',
        abslimits = (-32.5, -5.8),
        refpos = 472096, # 472087
        zerosteps = rd_zerosteps,
        refswitch = rd_refswitch,
        refdirection = rd_refdirection,
        refstep = rd_refstep,
        speed = rd_outer_speed,
        visibility = (),
    ),
    st_rd7 = device('nicos_mlz.puma.devices.ReferenceMotor',
        bus = 'motorbus10',
        addr = 79,
        slope = inner_slope,
        unit = 'deg',
        abslimits = (-30.0, -3.4),
        refpos = 485248, # 485126
        zerosteps = rd_zerosteps,
        refswitch = rd_refswitch,
        refdirection = rd_refdirection,
        refstep = rd_refstep,
        speed = rd_inner_speed,
        visibility = (),
    ),
    st_rd6 = device('nicos_mlz.puma.devices.ReferenceMotor',
        bus = 'motorbus10',
        addr = 81,
        slope = outer_slope,
        unit = 'deg',
        abslimits = (-27.5, -1.0),
        refpos = 494443, # 494490
        zerosteps = rd_zerosteps,
        refswitch = rd_refswitch,
        refdirection = rd_refdirection,
        refstep = rd_refstep,
        speed = rd_outer_speed,
        visibility = (),
    ),
    st_rd5 = device('nicos_mlz.puma.devices.ReferenceMotor',
        bus = 'motorbus10',
        addr = 83,
        slope = inner_slope,
        unit = 'deg',
        abslimits = (-25.0, 1.4),
        refpos = 505008, # 505231
        zerosteps = rd_zerosteps,
        refswitch = rd_refswitch,
        refdirection = rd_refdirection,
        refstep = rd_refstep,
        speed = rd_inner_speed,
        visibility = (),
    ),
    st_rd4 = device('nicos_mlz.puma.devices.ReferenceMotor',
        bus = 'motorbus10',
        addr = 85,
        slope = outer_slope,
        unit = 'deg',
        abslimits = (-22.5, 3.8),
        refpos = 517369, # 517322
        zerosteps = rd_zerosteps,
        refswitch = rd_refswitch,
        refdirection = rd_refdirection,
        refstep = rd_refstep,
        speed = rd_outer_speed,
        visibility = (),
    ),
    st_rd3 = device('nicos_mlz.puma.devices.ReferenceMotor',
        bus = 'motorbus10',
        addr = 87,
        slope = inner_slope,
        unit = 'deg',
        refpos = 524436, # 525045
        abslimits = (-20.0, 6.2),
        zerosteps = rd_zerosteps,
        refswitch = rd_refswitch,
        refdirection = rd_refdirection,
        refstep = rd_refstep,
        speed = rd_inner_speed,
        visibility = (),
    ),
    st_rd2 = device('nicos_mlz.puma.devices.ReferenceMotor',
        bus = 'motorbus10',
        addr = 89,
        slope = outer_slope,
        unit = 'deg',
        abslimits = (-17.5, 8.6),
        refpos = 539951, #539904
        zerosteps = rd_zerosteps,
        # The card has firmware version 65 instead of 58 and it seems that the
        # limit switch order has been changed
        refswitch = rd_refswitch,
        refdirection = rd_refdirection,
        refstep = rd_refstep,
        speed = rd_outer_speed,
        visibility = (),
    ),
    st_rd1 = device('nicos_mlz.puma.devices.ReferenceMotor',
        bus = 'motorbus10',
        addr = 91,
        slope = inner_slope,
        unit = 'deg',
        abslimits = (-15.0, 10.9),
        refpos = 544273, # 544679
        zerosteps = rd_zerosteps,
        # The card has firmware version 65 instead of 58 and it seems that the
        # limit switch order has been changed
        refswitch = rd_refswitch,  # 'high',
        refdirection = rd_refdirection,
        refstep = rd_refstep,
        speed = rd_inner_speed,
        visibility = (),
    ),
    rd11 = device('nicos.devices.generic.Axis',
        description = 'Detector 11 position',
        motor = 'st_rd11',
        precision = 0.01,
        offset = 0,
        maxtries = 1,
        visibility = vis,
    ),
    rd10 = device('nicos.devices.generic.Axis',
        description = 'Detector 10 position',
        motor = 'st_rd10',
        precision = 0.01,
        offset = 0,
        maxtries = 1,
        visibility = vis,
    ),
    rd9 = device('nicos.devices.generic.Axis',
        description = 'Detector 9 position',
        motor = 'st_rd9',
        precision = 0.01,
        offset = 0,
        maxtries = 1,
        visibility = vis,
    ),
    rd8 = device('nicos.devices.generic.Axis',
        description = 'Detector 8 position',
        motor = 'st_rd8',
        precision = 0.01,
        offset = 0,
        maxtries = 1,
        visibility = vis,
    ),
    rd7 = device('nicos.devices.generic.Axis',
        description = 'Detector 7 position',
        motor = 'st_rd7',
        precision = 0.01,
        offset = 0,
        maxtries = 1,
        visibility = vis,
    ),
    rd6 = device('nicos.devices.generic.Axis',
        description = 'Detector 6 position',
        motor = 'st_rd6',
        precision = 0.01,
        offset = 0,
        maxtries = 1,
        visibility = vis,
    ),
    rd5 = device('nicos.devices.generic.Axis',
        description = 'Detector 5 position',
        motor = 'st_rd5',
        precision = 0.01,
        offset = 0,
        maxtries = 1,
        visibility = vis,
    ),
    rd4 = device('nicos.devices.generic.Axis',
        description = 'Detector 4 position',
        motor = 'st_rd4',
        precision = 0.01,
        offset = 0,
        maxtries = 1,
        visibility = vis,
    ),
    rd3 = device('nicos.devices.generic.Axis',
        description = 'Detector 3 position',
        motor = 'st_rd3',
        precision = 0.01,
        offset = 0,
        maxtries = 1,
        visibility = vis,
    ),
    rd2 = device('nicos.devices.generic.Axis',
        description = 'Detector 2 position',
        motor = 'st_rd2',
        precision = 0.01,
        offset = 0,
        maxtries = 1,
        visibility = vis,
    ),
    rd1 = device('nicos.devices.generic.Axis',
        description = 'Detector 1 position',
        motor = 'st_rd1',
        precision = 0.01,
        offset = 0,
        maxtries = 1,
        visibility = vis,
    ),
    # Guides
    st_rg11 = device('nicos_mlz.puma.devices.ReferenceMotor',
        bus = 'motorbus10',
        addr = 72,
        slope = rg_slope,
        unit = 'deg',
        abslimits = (-10, 20),
        refpos = 509072, # 509262
        zerosteps = rg_zerosteps,
        refswitch = rg_refswitch,
        refdirection = rg_refdirection,
        refstep = rg_refstep,
        visibility = (),
    ),
    st_rg10 = device('nicos_mlz.puma.devices.ReferenceMotor',
        bus = 'motorbus10',
        addr = 74,
        slope = rg_slope,
        unit = 'deg',
        abslimits = (-10, 20),
        refpos = 507906, # 508380
        zerosteps = rg_zerosteps,
        refswitch = rg_refswitch,
        refdirection = rg_refdirection,
        refstep = rg_refstep,
        visibility = (),
    ),
    st_rg9 = device('nicos_mlz.puma.devices.ReferenceMotor',
        bus = 'motorbus10',
        addr = 76,
        slope = rg_slope,
        unit = 'deg',
        abslimits = (-10, 20),
        refpos = 507802, # 507992
        zerosteps = rg_zerosteps,
        refswitch = rg_refswitch,
        refdirection = rg_refdirection,
        refstep = rg_refstep,
        visibility = (),
    ),
    st_rg8 = device('nicos_mlz.puma.devices.ReferenceMotor',
        bus = 'motorbus10',
        addr = 78,
        slope = rg_slope,
        unit = 'deg',
        abslimits = (-10, 20),
        refpos = 507878, # 508257
        zerosteps = rg_zerosteps,
        refswitch = rg_refswitch,
        refdirection = rg_refdirection,
        refstep = rg_refstep,
        visibility = (),
    ),
    st_rg7 = device('nicos_mlz.puma.devices.ReferenceMotor',
        bus = 'motorbus10',
        addr = 80,
        slope = rg_slope,
        unit = 'deg',
        abslimits = (-10, 20),
        refpos = 506200, # 506674
        zerosteps = rg_zerosteps,
        refswitch = rg_refswitch,
        refdirection = rg_refdirection,
        refstep = rg_refstep,
        visibility = (),
    ),
    st_rg6 = device('nicos_mlz.puma.devices.ReferenceMotor',
        bus = 'motorbus10',
        addr = 82,
        slope = rg_slope,
        unit = 'deg',
        abslimits = (-10, 20),
        refpos = 505755, # 506134
        zerosteps = rg_zerosteps,
        refswitch = rg_refswitch,
        refdirection = rg_refdirection,
        refstep = rg_refstep,
        visibility = (),
    ),
    st_rg5 = device('nicos_mlz.puma.devices.ReferenceMotor',
        bus = 'motorbus10',
        addr = 84,
        slope = rg_slope,
        unit = 'deg',
        abslimits = (-10, 20),
        refpos = 505508, # 505603
        zerosteps = rg_zerosteps,
        refswitch = rg_refswitch,
        refdirection = rg_refdirection,
        refstep = rg_refstep,
        visibility = (),
    ),
    st_rg4 = device('nicos_mlz.puma.devices.ReferenceMotor',
        bus = 'motorbus10',
        addr = 86,
        slope = rg_slope,
        unit = 'deg',
        abslimits = (-10, 20),
        refpos = 504853, # 505043
        zerosteps = rg_zerosteps,
        refswitch = rg_refswitch,
        refdirection = rg_refdirection,
        refstep = rg_refstep,
        visibility = (),
    ),
    st_rg3 = device('nicos_mlz.puma.devices.ReferenceMotor',
        bus = 'motorbus10',
        addr = 88,
        slope = rg_slope,
        unit = 'deg',
        abslimits = (-10, 20),
        refpos = 505062, # 505252
        zerosteps = rg_zerosteps,
        refswitch = rg_refswitch,
        refdirection = rg_refdirection,
        refstep = rg_refstep,
        visibility = (),
    ),
    st_rg2 = device('nicos_mlz.puma.devices.ReferenceMotor',
        bus = 'motorbus10',
        addr = 90,
        slope = rg_slope,
        unit = 'deg',
        refpos = 506987, # 507366
        abslimits = (-10, 20),
        zerosteps = rg_zerosteps,
        refswitch = rg_refswitch,
        refdirection = rg_refdirection,
        refstep = rg_refstep,
        visibility = (),
    ),
    st_rg1 = device('nicos_mlz.puma.devices.ReferenceMotor',
        bus = 'motorbus10',
        addr = 92,
        slope = rg_slope,
        unit = 'deg',
        refpos = 508466, # 508371
        abslimits = (-10, 20),
        zerosteps = rg_zerosteps,
        refswitch = rg_refswitch,
        refdirection = rg_refdirection,
        refstep = rg_refstep,
        visibility = (),
    ),
    rg11 = device('nicos.devices.generic.Axis',
        description = 'Rotation of the detector 11 guide',
        motor = 'st_rg11',
        precision = 0.01,
        offset = -0,
        maxtries = 2,
        visibility = vis,
    ),
    rg10 = device('nicos.devices.generic.Axis',
        description = 'Rotation of the detector 10 guide',
        motor = 'st_rg10',
        precision = 0.01,
        offset = -0,
        maxtries = 2,
        visibility = vis,
    ),
    rg9 = device('nicos.devices.generic.Axis',
        description = 'Rotation of the detector 9 guide',
        motor = 'st_rg9',
        precision = 0.01,
        offset = -0,
        maxtries = 2,
        visibility = vis,
    ),
    rg8 = device('nicos.devices.generic.Axis',
        description = 'Rotation of the detector 8 guide',
        motor = 'st_rg8',
        precision = 0.01,
        offset = -0,
        maxtries = 2,
        visibility = vis,
    ),
    rg7 = device('nicos.devices.generic.Axis',
        description = 'Rotation of the detector 7 guide',
        motor = 'st_rg7',
        precision = 0.01,
        offset = -0,
        maxtries = 2,
        visibility = vis,
    ),
    rg6 = device('nicos.devices.generic.Axis',
        description = 'Rotation of the detector 6 guide',
        motor = 'st_rg6',
        precision = 0.01,
        offset = -0,
        maxtries = 2,
        visibility = vis,
    ),
    rg5 = device('nicos.devices.generic.Axis',
        description = 'Rotation of the detector 5 guide',
        motor = 'st_rg5',
        precision = 0.01,
        offset = -0,
        maxtries = 2,
        visibility = vis,
    ),
    rg4 = device('nicos.devices.generic.Axis',
        description = 'Rotation of the detector 4 guide',
        motor = 'st_rg4',
        precision = 0.01,
        offset = -0,
        maxtries = 2,
        visibility = vis,
    ),
    rg3 = device('nicos.devices.generic.Axis',
        description = 'Rotation of the detector 3 guide',
        motor = 'st_rg3',
        precision = 0.01,
        offset = -0,
        maxtries = 2,
        visibility = vis,
    ),
    rg2 = device('nicos.devices.generic.Axis',
        description = 'Rotation of the detector 2 guide',
        motor = 'st_rg2',
        precision = 0.01,
        offset = -0,
        maxtries = 2,
        visibility = vis,
    ),
    rg1 = device('nicos.devices.generic.Axis',
        description = 'Rotation of the detector 1 guide',
        motor = 'st_rg1',
        precision = 0.01,
        offset = -0,
        maxtries = 2,
        visibility = vis,
    ),
    med = device('nicos_mlz.puma.devices.MultiDetectorLayout',
        description = 'PUMA multidetector',
        rotdetector = ['rd1', 'rd2', 'rd3', 'rd4', 'rd5', 'rd6', 'rd7', 'rd8',
                       'rd9', 'rd10', 'rd11'],
        rotguide = ['rg1', 'rg2', 'rg3', 'rg4', 'rg5', 'rg6', 'rg7', 'rg8',
                    'rg9', 'rg10', 'rg11'],
        refgap = 3.0,
        att = 'att_cad',
        parkpos = [-11., -13.75, -16.5, -19.25, -22., -24.75, -27.5, -30.25,
                   -33.00, -35.75, -38.5,
                   9.5, 9.5, 9.5, 9., 8., 7., 6., 5., 4., 3., 1.5],
    ),
)
