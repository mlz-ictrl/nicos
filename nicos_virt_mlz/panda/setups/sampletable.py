description = 'Sampletable complete'

includes = ['system']

group = 'lowlevel'

devices = dict(
    stt_step = device('nicos.devices.generic.VirtualMotor',
        unit = 'deg',
        abslimits = (-100, 130),
        speed = 4,
        visibility = (),
    ),
    stt_enc = device('nicos.devices.generic.VirtualCoder',
        motor = 'stt_step',
        unit = 'deg',
        visibility = (),
    ),
    stt = device('nicos.devices.generic.Axis',
        description = 'sample two theta',
        motor = 'stt_step',
        coder = 'stt_enc',
        precision = 0.025,
        # offset = -0.925,
        offset = -1.045,
    ),

    sth_st_step = device('nicos.devices.generic.VirtualMotor',
        unit = 'deg',
        abslimits = (1, 359),
        speed = 4,
        visibility = (),
    ),
    sth_st_enc = device('nicos.devices.generic.VirtualCoder',
        motor = 'sth_st_step',
        unit = 'deg',
        visibility = (),
    ),
    sth_st = device('nicos.devices.generic.Axis',
        description = 'sth mounted on sampletable',
        motor = 'sth_st_step',
        coder = 'sth_st_enc',
        precision = 0.02,
    ),

    sgx_step = device('nicos.devices.generic.VirtualMotor',
        unit = 'deg',
        abslimits = (-15.1, 15.1),
        speed = 1,
        visibility = (),
    ),
    sgx_enc = device('nicos.devices.generic.VirtualCoder',
        motor = 'sgx_step',
        unit = 'deg',
        visibility = (),
    ),
    sgx = device('nicos.devices.generic.Axis',
        description = 'sample goniometer around X',
        motor = 'sgx_step',
        coder = 'sgx_enc',
        precision = 0.05,
        # rotary = True,
    ),

    sgy_step = device('nicos.devices.generic.VirtualMotor',
        unit = 'deg',
        abslimits = (-15.1, 15.1),
        speed = 1,
        visibility = (),
    ),
    sgy_enc = device('nicos.devices.generic.VirtualCoder',
        motor = 'sgy_step',
        unit = 'deg',
        visibility = (),
    ),
    sgy = device('nicos.devices.generic.Axis',
        description = 'sample goniometer around Y',
        motor = 'sgy_step',
        coder = 'sgy_enc',
        precision = 0.05,
        # rotary = True,
    ),

    vg1 = device('nicos.devices.tas.VirtualGonio',
        description = 'Gonio along orient1 reflex',
        cell = 'Sample',
        gx = 'sgx',
        gy = 'sgy',
        axis = 1,
        unit = 'deg',
    ),
    vg2 = device('nicos.devices.tas.VirtualGonio',
        description = 'Gonio along orient2 reflex',
        cell = 'Sample',
        gx = 'sgx',
        gy = 'sgy',
        axis = 2,
        unit = 'deg',
    ),

    stx_step = device('nicos.devices.generic.VirtualMotor',
        unit = 'mm',
        abslimits = (-20, 20),
        speed = 1,
        visibility = (),
    ),
    stx_poti = device('nicos.devices.generic.VirtualCoder',
        motor = 'stx_step',
        unit = 'mm',
        visibility = (),
    ),
    stx = device('nicos.devices.generic.Axis',
        description = 'sample translation along X',
        motor = 'stx_step',
        obs = ['stx_poti'],
        precision = 0.05,
        fmtstr = '%.1f',
    ),

    sty_step = device('nicos.devices.generic.VirtualMotor',
        unit = 'mm',
        abslimits = (-15, 15),
        speed = 1,
        visibility = (),
    ),
    sty_poti = device('nicos.devices.generic.VirtualCoder',
        motor = 'sty_step',
        unit = 'mm',
        visibility = (),
    ),
    sty = device('nicos.devices.generic.Axis',
        description = 'sample translation along Y',
        motor = 'sty_step',
        obs = ['sty_poti'],
        precision = 0.05,
        fmtstr = '%.1f',
    ),

    stz_step = device('nicos.devices.generic.VirtualMotor',
        unit = 'mm',
        abslimits = (-20, 20),
        userlimits = (-15, 15),
        speed = 0.5,
        visibility = (),
    ),

    stz = device('nicos.devices.generic.Axis',
        description = 'vertical sample translation',
        motor = 'stz_step',
        precision = 0.1,
        fmtstr = '%.3f',
    ),
)

alias_config = {
    'sth': {'sth_st': 10},
}
