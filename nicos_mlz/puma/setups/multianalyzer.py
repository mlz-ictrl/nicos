description = 'Multi analyzer devices'

group = 'lowlevel'

includes = ['motorbus10']

devices = dict(
    ra1 = device('nicos.devices.generic.Axis',
        description = 'Rotation crystal 1',
        motor = device('nicos_mlz.puma.devices.ipc_puma.Motor',
            bus = 'motorbus10',
            addr = 91,
            slope = 4061.72,
            unit = 'deg',
            fmtstr = '%.3f',
            abslimits = (-90., 5.),
            zerosteps = 0,
            timeout = 600,
            # 'refdir': 'high',  # direction of ref switch
            # 'refstep': 200,  # increment for reference switch search
            # 'refmove': 100,  # goal position for reference drive
            # 'refpos': 1000,  # reference position
            # 'refcounter': 120000,  # position from where the reference process starts towards the reference switch
            # 'backlash': 0,  # backlash of axis
        ),
        unit= 'deg',
        fmtstr = '%6.3f',
        precision = 0.01,
        # 'general_reset': 0,
        # 'stepperoffset':500000,
        # 'refswitch':'high',
        # 'refpos': 500000,
        # 'refspeed':21,
        # 'refstep': 10000,
        # 'offset': 14.372,
        # 'pos_side':'high',
        # 'parkpos': -14.372,
        # 'resetconf': 0,
        # 'timeout': 300,
        # 'chkmotiontime': 1,
        # 'delta': 0,
    )
)
