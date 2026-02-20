description = 'Setup for the standard sample table'

pvprefix = 'SQ:SANS-LLB:turboPmac1:'

group = 'lowlevel'

devices = dict(
    stom = device('nicos_sinq.devices.epics.motor.SinqMotor',
        epicstimeout = 3.0,
        description = 'Sample table rotation around Y',
        motorpv = pvprefix + 'stom',
    ),
    stx = device('nicos_sinq.devices.epics.motor.SinqMotor',
        epicstimeout = 3.0,
        description = 'Sample translation X  (horizontal, perpendicular to beam)',
        motorpv = pvprefix + 'stx',
    ),
    stz = device('nicos.devices.generic.manual.ManualMove',
        description = 'Sample translation Z (along the beam, fixed)',
        unit = 'mm',
        abslimits = (0, 350)
    ),
    stgn = device('nicos_sinq.devices.epics.motor.SinqMotor',
        epicstimeout = 3.0,
        description = 'Sample table goniometer (rotation around X)',
        motorpv = pvprefix + 'stgn',
    ),
    sty = device('nicos_sinq.devices.epics.motor.SinqMotor',
        epicstimeout = 3.0,
        description = 'Sample translation Y (vertical)',
        motorpv = pvprefix + 'sty',
    ),
    spos = device('nicos_sinq.devices.epics.motor.SinqMotor',
        epicstimeout = 3.0,
        description = 'Sample chnager position',
        motorpv = pvprefix + 'spos',
    ),
    schanger = device('nicos_sinq.sans_llb.devices.sample_switcher.SampleSwitcher',
        description = 'Sample ID to select',
        switch_axis = 'spos',
        perp_axis = 'sty',
        mapping = {},
        # this defines the spos/sty location of the first sample in each sample holder
        adjusted_positions = {
            'mfu':   [469.0, 0.],
            'qs110': [469.0, 0.],
            'qs120': [469.0, 0.],
            'qs404': [469.0, 0.],
            'solid': [469.0, 0.],
            'olaf':  [469.0, 0.]
            },
    ),
)
