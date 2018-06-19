description = "DoubleSlit [slit k1] between nok6 and nok7"

group = 'lowlevel'

includes = ['nok_ref', 'nokbus3']
global_values = configdata('global.GLOBAL_Values')

nethost = 'refsanssrv.refsans.frm2'

devices = dict(
    zb3 = device('nicos_mlz.refsans.devices.slits.DoubleSlit',
        description = 'ZB3 slit',
        slit_r = 'zb3r',
        slit_s = 'zb3s',
        fmtstr = 'opening: %.3f mm, zpos: %.3f mm',
        unit = '',
    ),
    zb3_mode = device('nicos.devices.generic.ReadonlyParamDevice',
        description = 'zb3 mode',
        device = 'zb3',
        parameter = 'mode',
    ),

    zb3r = device('nicos_mlz.refsans.devices.slits.SingleSlit',
        description = 'ZB3 slit, reactor side',
        motor = 'zb3r_m',
        nok_start = 8837.5,
        nok_length = 13.0,
        nok_end = 8850.5,
        nok_gap = 1.0,
        masks = {
            'slit': -1.0,
            'point': 0,
            'gisans': -110,
        },
        unit = 'mm',
        lowlevel = True,
    ),
    zb3s = device('nicos_mlz.refsans.devices.slits.SingleSlit',
        description = 'ZB3 slit, sample side',
        motor = 'zb3s_m',
        nok_start = 8837.5,
        nok_length = 13.0,
        nok_end = 8850.5,
        nok_gap = 1.0,
        masks = {
            'slit': 1.0,
            'point': 0,
            'gisans': 0,
        },
        unit = 'mm',
        lowlevel = True,
    ),

    zb3r_m = device('nicos_mlz.refsans.devices.nok_support.NOKMotorIPC',
        description = 'IPC controlled Motor of ZB3, reactor side',
        abslimits = (-221.0, 95.0),
        bus = 'nokbus3',     # from ipcsms_*.res
        addr = 0x57,     # from resources.inf
        slope = 800.0,   # FULL steps per physical unit
        speed = 50,
        accel = 50,
        confbyte = 32,
        ramptype = 2,
        microstep = 1,
        refpos = 105.837,    # from ipcsms_*.res
        zerosteps = int(677.125 * 800),  # offset * slope
        lowlevel = global_values['hide_poti'],
    ),
    zb3s_m = device('nicos_mlz.refsans.devices.nok_support.NOKMotorIPC',
        description = 'IPC controlled Motor of ZB3, sample side',
        abslimits = (-106.0, 113.562),
        bus = 'nokbus3',     # from ipcsms_*.res
        addr = 0x58,     # from resources.inf
        slope = 800.0,   # FULL steps per physical unit
        speed = 50,
        accel = 50,
        confbyte = 32,
        ramptype = 2,
        microstep = 1,
        refpos = 72.774,     # from ipcsms_*.res
        zerosteps = int(644.562 * 800),  # offset * slope
        lowlevel = global_values['hide_poti'],
    ),
    zb3r_acc = device('nicos_mlz.refsans.devices.nok_support.MotorEncoderDifference',
         description = 'calc error Motor and poti',
         motor = 'zb3r_m',
         analog = 'zb3r_obs',
         lowlevel = global_values['hide_acc'],
         unit = 'mm'
    ),
    zb3r_obs = device('nicos_mlz.refsans.devices.nok_support.NOKPosition',
        description = 'Position sensing for ZB3, reactor side',
        reference = 'nok_refc1',
        measure = 'zb3r_poti',
        poly = [-140.539293, 1004.824 / 1.92],   # off, mul * 1000 / sensitivity, higher orders...
        serial = 7778,
        length = 500.0,
        lowlevel = global_values['hide_poti'],
    ),
    zb3r_poti = device('nicos_mlz.refsans.devices.nok_support.NOKMonitoredVoltage',
        description = 'Poti for ZB3, reactor side',
        tacodevice = '//%s/test/wb_c/1_2' % nethost,
        scale = -1,  # mounted from top
        lowlevel = True,
    ),
    zb3s_acc = device('nicos_mlz.refsans.devices.nok_support.MotorEncoderDifference',
         description = 'calc error Motor and poti',
         motor = 'zb3s_m',
         analog = 'zb3s_obs',
         lowlevel = global_values['hide_acc'],
         unit = 'mm'
    ),
    zb3s_obs = device('nicos_mlz.refsans.devices.nok_support.NOKPosition',
        description = 'Position sensing for ZB3, sample side',
        reference = 'nok_refc1',
        measure = 'zb3s_poti',
        poly = [118.68, 1000. / 1.921],    # off, mul * 1000 / sensitivity, higher orders...
        serial = 7781,
        length = 500.0,
        lowlevel = global_values['hide_poti'],
    ),
    zb3s_poti = device('nicos_mlz.refsans.devices.nok_support.NOKMonitoredVoltage',
        description = 'Poti for ZB3, sample side',
        tacodevice = '//%s/test/wb_c/1_3' % nethost,
        scale = 1,   # mounted from bottom
        lowlevel = True,
    ),
)
