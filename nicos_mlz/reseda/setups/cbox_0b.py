#  -*- coding: utf-8 -*-

description = 'Capacity box %s' % setupname
group = 'optional'

tango_base = 'tango://resedahw2.reseda.frm2:10000/reseda'

devices = {
    '%s_coil_amp' % setupname:
        device('nicos.devices.tango.Sensor',
            description = 'Measured amplitude at coil',
            tangodevice = '%s/%s/coil_voltage' % (tango_base, setupname),
            unit = 'V',
        ),
    '%s_fg_freq' % setupname:
        device('nicos.devices.tango.AnalogOutput',
            description = 'Frequency generator frequency',
            tangodevice = '%s/%s/fg_frequency' % (tango_base, setupname),
            pollinterval = 3,
            fmtstr = '%.3g'
        ),
     '%s_reg_amp' % setupname:
        device('nicos_mlz.reseda.devices.regulator.Regulator',
            description = 'Auto regulating amplitude',
            sensor = '%s_coil_amp' % setupname,
            moveable = '%s_fg_amp' % setupname,
        ),
    '%s_fg_amp' % setupname:
        device('nicos.devices.tango.AnalogOutput',
            description = 'Frequency generator amplitude',
            tangodevice = '%s/%s/fg_amplitude' % (tango_base, setupname),
            pollinterval = 3,
        ),
    '%s_fwdp' % setupname:
        device('nicos.devices.tango.AnalogInput',
            description = 'Power amplifier forward power',
            tangodevice = '%s/%s/pa_fwdp' % (tango_base, setupname),
            pollinterval = 3,
        ),
    '%s_revp' % setupname:
        device('nicos.devices.tango.AnalogInput',
            description = 'Power amplifier reverse power',
            tangodevice = '%s/%s/pa_revp' % (tango_base, setupname),
            pollinterval = 3,
        ),
#    '%s_gain' % setupname:
#        device('nicos.devices.tango.AnalogOutput',
#            description = 'Power amplifier gain',
#            tangodevice = '%s/%s/pa_gain' % (tango_base, setupname),
#            pollinterval = 3,
#        ),
    '%s' % setupname:
        device('nicos_mlz.reseda.devices.cbox.CBoxResonanceFrequency',
            pollinterval = 3,
            description = 'CBox',
            unit = 'Hz',
            power_divider = device('nicos.devices.tango.DigitalOutput',
                description = 'Power divider to split the power for both coils',
                tangodevice = '%s/%s/plc_power_divider' %
                (tango_base, setupname),
                lowlevel = False,  # temporary due to inaccurate auto tune
            ),
            highpass = device('nicos.devices.tango.DigitalOutput',
                description = 'Highpass filter to smooth the signal',
                tangodevice = '%s/%s/plc_highpass' % (tango_base, setupname),
                lowlevel = False,  # temporary due to inaccurate auto tune
            ),
            pa_fwdp = '%s_fwdp' % setupname,
            pa_revp = '%s_revp' % setupname,
            fg = '%s_fg_freq' % setupname,
            coil_amp = '%s_coil_amp' % setupname,
            diplexer = device('nicos.devices.tango.DigitalOutput',
                description =
                'Lowpass filter to smooth the signal (enable for low frequency, disable for high frequency)',
                tangodevice = '%s/%s/plc_diplexer' % (tango_base, setupname),
                lowlevel = False,  # temporary due to inaccurate auto tune
            ),
            coil1_c1 = device('nicos.devices.tango.DigitalOutput',
                description = 'Coil 1: Capacitor bank 1',
                tangodevice = '%s/%s/plc_a_c1' % (tango_base, setupname),
                lowlevel = False,  # temporary due to inaccurate auto tune
            ),
            coil1_c2 = device('nicos.devices.tango.DigitalOutput',
                description = 'Coil 1: Capacitor bank 2',
                tangodevice = '%s/%s/plc_a_c2' % (tango_base, setupname),
                lowlevel = False,  # temporary due to inaccurate auto tune
            ),
            coil1_c3 = device('nicos.devices.tango.DigitalOutput',
                description = 'Coil 1: Capacitor bank 3',
                tangodevice = '%s/%s/plc_a_c3' % (tango_base, setupname),
                lowlevel = False,  # temporary due to inaccurate auto tune
            ),
            coil1_c1c2serial = device('nicos.devices.tango.DigitalOutput',
                description =
                'Coil 1: Use c1 and c2 in serial instead of parallel',
                tangodevice = '%s/%s/plc_a_c1c2serial' %
                (tango_base, setupname),
                lowlevel = False,  # temporary due to inaccurate auto tune
            ),
            coil1_transformer = device('nicos.devices.tango.DigitalOutput',
                description =
                'Coil 1: Used to manipulate the coil resistance to match the power amplifier resistance',
                tangodevice = '%s/%s/plc_a_transformer' %
                (tango_base, setupname),
                lowlevel = False,  # temporary due to inaccurate auto tune
            ),
            coil2_c1 = device('nicos.devices.tango.DigitalOutput',
                description = 'Coil 2: Capacitor bank 1',
                tangodevice = '%s/%s/plc_b_c1' % (tango_base, setupname),
                lowlevel = False,  # temporary due to inaccurate auto tune
            ),
            coil2_c2 = device('nicos.devices.tango.DigitalOutput',
                description = 'Coil 2: Capacitor bank 2',
                tangodevice = '%s/%s/plc_b_c2' % (tango_base, setupname),
                lowlevel = False,  # temporary due to inaccurate auto tune
            ),
            coil2_c3 = device('nicos.devices.tango.DigitalOutput',
                description = 'Coil 2: Capacitor bank 3',
                tangodevice = '%s/%s/plc_b_c3' % (tango_base, setupname),
                lowlevel = False,  # temporary due to inaccurate auto tune
            ),
            coil2_c1c2serial = device('nicos.devices.tango.DigitalOutput',
                description =
                'Coil 2: Use c1 and c2 in serial instead of parallel',
                tangodevice = '%s/%s/plc_b_c1c2serial' %
                (tango_base, setupname),
                lowlevel = False,  # temporary due to inaccurate auto tune
            ),
            coil2_transformer = device('nicos.devices.tango.DigitalOutput',
                description =
                'Coil 2: Used to manipulate the coil resistance to match the power amplifier resistance',
                tangodevice = '%s/%s/plc_b_transformer' %
                (tango_base, setupname),
                lowlevel = False,  # temporary due to inaccurate auto tune
            ),
        ),
}
