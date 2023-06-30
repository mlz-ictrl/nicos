#  -*- coding: utf-8 -*-

description = 'Capacity box %s' % setupname
group = 'optional'

tango_base = 'tango://%s:10000/reseda/%s/' % (configdata('gconfigs.tango_host'), setupname)

includes = ['rte1104']

devices = {
    '%s_fg_freq' % setupname:
        device('nicos_mlz.reseda.devices.RTE1104TimescaleSetting',
            description = 'Frequency setting chain of subdevices: setting timescale',
            io = 'rte1104_io',
            freqgen = device('nicos.devices.entangle.AnalogOutput',
                description = 'Frequency generator frequency',
                tangodevice = tango_base + 'fg_frequency',
                pollinterval = 30,
                fmtstr = '%.4g',
                unit = 'Hz',
               ),
        ),
     '%s_reg_amp' % setupname:
        device('nicos_mlz.reseda.devices.RTE1104YScaleSetting',
            description = 'amplitude setting chain of subdevices: setting channel 2',
            io = 'rte1104_io',
            channel = 2,
            regulator = device('nicos_mlz.reseda.devices.Regulator',
                description = 'Auto regulating amplitude',
                sensor = '%s_coil_rms' % setupname,
                moveable = '%s_fg_amp' % setupname,
                loopdelay = 1.0,
                maxstep = 0.1,
                minstep = 0.005,
                maxage = 11.0,
                pollinterval = 5.0,
                stepfactor = 0.3,
                unit = 'V',
               ),
        ),
    '%s_fg_amp' % setupname:
        device('nicos.devices.entangle.AnalogOutput',
            description = 'Frequency generator amplitude',
            tangodevice = tango_base + 'fg_amplitude',
            # abslimits have to be set in res file!
            pollinterval = 5,
            unit = 'V',
        ),
    '%s_fwdp' % setupname:
        device('nicos.devices.entangle.AnalogInput',
            description = 'Power amplifier forward power',
            tangodevice = tango_base + 'pa_fwdp',
            pollinterval = 10,
            unit = 'W',
        ),
    '%s_revp' % setupname:
        device('nicos.devices.entangle.AnalogInput',
            description = 'Power amplifier reverse power',
            tangodevice = tango_base + 'pa_revp',
            pollinterval = 10,
            unit = 'W',
        ),
    '%s' % setupname:
        device('nicos_mlz.reseda.devices.CBoxResonanceFrequency',
            pollinterval = 30,
            description = 'CBox',
            unit = 'Hz',
            power_divider = device('nicos.devices.entangle.DigitalOutput',
                description = 'Power divider to split the power for both coils',
                tangodevice = tango_base + 'plc_power_divider',
                visibility = ('devlist',),  # temporary due to inaccurate auto tune
                unit = '',
                fmtstr = '%.0f',
            ),
            highpass = device('nicos.devices.entangle.DigitalOutput',
                description = 'Highpass filter to smooth the signal',
                tangodevice = tango_base + 'plc_highpass',
                visibility = ('devlist',),  # temporary due to inaccurate auto tune
                unit = '',
                fmtstr = '%.0f',
            ),
            pa_fwdp = '%s_fwdp' % setupname,
            pa_revp = '%s_revp' % setupname,
            fg = '%s_fg_freq' % setupname,
            coil_amp = '%s_coil_rms' % setupname,
            diplexer = device('nicos.devices.entangle.DigitalOutput',
                description =
                'Lowpass filter to smooth the signal (enable for low frequency, disable for high frequency)',
                tangodevice = tango_base + 'plc_diplexer',
                visibility = ('devlist',),  # temporary due to inaccurate auto tune
                unit = '',
                fmtstr = '%.0f',
            ),
            coil1_c1 = device('nicos.devices.entangle.DigitalOutput',
                description = 'Coil 1: Capacitor bank 1',
                tangodevice = tango_base + 'plc_a_c1',
                visibility = ('devlist',),  # temporary due to inaccurate auto tune
                unit = '',
                fmtstr = '%.0f',
            ),
            coil1_c2 = device('nicos.devices.entangle.DigitalOutput',
                description = 'Coil 1: Capacitor bank 2',
                tangodevice = tango_base + 'plc_a_c2',
                visibility = ('devlist',),  # temporary due to inaccurate auto tune
                unit = '',
                fmtstr = '%.0f',
            ),
            coil1_c3 = device('nicos.devices.entangle.DigitalOutput',
                description = 'Coil 1: Capacitor bank 3',
                tangodevice = tango_base + 'plc_a_c3',
                visibility = ('devlist',),  # temporary due to inaccurate auto tune
                unit = '',
                fmtstr = '%.0f',
            ),
            coil1_c1c2serial = device('nicos.devices.entangle.DigitalOutput',
                description =
                'Coil 1: Use c1 and c2 in serial instead of parallel',
                tangodevice = tango_base + 'plc_a_c1c2serial',
                visibility = ('devlist',),  # temporary due to inaccurate auto tune
                unit = '',
                fmtstr = '%.0f',
            ),
            coil1_transformer = device('nicos.devices.entangle.DigitalOutput',
                description =
                'Coil 1: Used to manipulate the coil resistance to match the power amplifier resistance',
                tangodevice = tango_base + 'plc_a_transformer',
                visibility = ('devlist',),  # temporary due to inaccurate auto tune
                unit = '',
                fmtstr = '%.0f',
            ),
            coil2_c1 = device('nicos.devices.entangle.DigitalOutput',
                description = 'Coil 2: Capacitor bank 1',
                tangodevice = tango_base + 'plc_b_c1',
                visibility = ('devlist',),  # temporary due to inaccurate auto tune
                unit = '',
                fmtstr = '%.0f',
            ),
            coil2_c2 = device('nicos.devices.entangle.DigitalOutput',
                description = 'Coil 2: Capacitor bank 2',
                tangodevice = tango_base + 'plc_b_c2',
                visibility = ('devlist',),  # temporary due to inaccurate auto tune
                unit = '',
                fmtstr = '%.0f',
            ),
            coil2_c3 = device('nicos.devices.entangle.DigitalOutput',
                description = 'Coil 2: Capacitor bank 3',
                tangodevice = tango_base + 'plc_b_c3',
                visibility = ('devlist',),  # temporary due to inaccurate auto tune
                unit = '',
                fmtstr = '%.0f',
            ),
            coil2_c1c2serial = device('nicos.devices.entangle.DigitalOutput',
                description =
                'Coil 2: Use c1 and c2 in serial instead of parallel',
                tangodevice = tango_base + 'plc_b_c1c2serial',
                visibility = ('devlist',),  # temporary due to inaccurate auto tune
                unit = '',
                fmtstr = '%.0f',
            ),
            coil2_transformer = device('nicos.devices.entangle.DigitalOutput',
                description =
                'Coil 2: Used to manipulate the coil resistance to match the power amplifier resistance',
                tangodevice = tango_base + 'plc_b_transformer',
                visibility = ('devlist',),  # temporary due to inaccurate auto tune
                unit = '',
                fmtstr = '%.0f',
            ),
        ),
    '%s_coil_rms' % setupname: device('nicos_mlz.reseda.devices.RTE1104',
       description = 'rms Coil voltage (Input Channel 2)',
       io = 'rte1104_io',
       channel = 2,
       unit = 'V',
    ),
}
