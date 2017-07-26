#  -*- coding: utf-8 -*-

description = 'Capacity box'
group = 'optional'

tango_base = 'tango://resedahw2.reseda.frm2:10000/reseda'

devices = dict(
    osci_pk2pk = device('nicos.devices.tango.AnalogInput',
        description = 'Osci at coil, peak to peak measurement',
        tangodevice = '%s/cbox/osci_pk2pk' % tango_base,
        pollinterval = 1,
    ),
    fg_frequency = device('nicos.devices.tango.AnalogOutput',
        description = 'Frequency generator amplitude',
        tangodevice = '%s/cbox/fg_freq' % tango_base,
        pollinterval = 1,
    ),
    fg_amplitude = device('nicos.devices.tango.AnalogOutput',
        description = 'Frequency generator amplitude',
        tangodevice = '%s/cbox/fg_amplitude' % tango_base,
        pollinterval = 1,
    ),
    pa_fwdp = device('nicos.devices.tango.AnalogInput',
        description = 'Power amplifier forward power',
        tangodevice = '%s/cbox/pa_fwdp' % tango_base,
        pollinterval = 1,
    ),
    pa_revp = device('nicos.devices.tango.AnalogInput',
        description = 'Power amplifier reverse power',
        tangodevice = '%s/cbox/pa_revp' % tango_base,
        pollinterval = 1,
    ),
    pa_temp = device('nicos.devices.tango.AnalogInput',
        description = 'Power amplifier temperature',
        tangodevice = '%s/cbox/pa_temp' % tango_base,
        pollinterval = 1,
    ),
    pa_gain = device('nicos.devices.tango.AnalogOutput',
        description = 'Power amplifier gain',
        tangodevice = '%s/cbox/pa_gain' % tango_base,
        pollinterval = 1,
    ),
    cbox = device('nicos_mlz.reseda.devices.cbox.CBoxResonanceFrequency',
        pollinterval = 1,
        description = 'CBox',
        unit = 'Hz',
        power_divider = device('nicos.devices.tango.DigitalOutput',
            description = 'Power divider to split the power for both coils',
            tangodevice = '%s/cbox/plc_power_divider' % tango_base
        ),
        highpass = device('nicos.devices.tango.DigitalOutput',
            description = 'Highpass filter to smooth the signal',
            tangodevice = '%s/cbox/plc_highpass' % tango_base
        ),
        pa_fwdp = 'pa_fwdp',
        pa_revp = 'pa_revp',
        fg = 'fg_frequency',
        diplexer = device('nicos.devices.tango.DigitalOutput',
            description = 'Lowpass filter to smooth the signal (enable for low frequency, disable for high frequency)',
            tangodevice = '%s/cbox/plc_diplexer' % tango_base
        ),
        coil1_c1 = device('nicos.devices.tango.DigitalOutput',
            description = 'Coil 1: Capacitor bank 1',
            tangodevice = '%s/cbox/plc_a_c1' % tango_base
        ),
        coil1_c2 = device('nicos.devices.tango.DigitalOutput',
            description = 'Coil 1: Capacitor bank 2',
            tangodevice = '%s/cbox/plc_a_c2' % tango_base
        ),
        coil1_c3 = device('nicos.devices.tango.DigitalOutput',
            description = 'Coil 1: Capacitor bank 3',
            tangodevice = '%s/cbox/plc_a_c3' % tango_base
        ),
        coil1_c1c2serial = device('nicos.devices.tango.DigitalOutput',
            description = 'Coil 1: Use c1 and c2 in serial instead of parallel',
            tangodevice = '%s/cbox/plc_a_c1c2serial' % tango_base
        ),
        coil1_transformer = device('nicos.devices.tango.DigitalOutput',
            description = 'Coil 1: Used to manipulate the coil resistance to match the power amplifier resistance',
            tangodevice = '%s/cbox/plc_a_transformer' % tango_base
        ),
        coil2_c1 = device('nicos.devices.tango.DigitalOutput',
            description = 'Coil 2: Capacitor bank 1',
            tangodevice = '%s/cbox/plc_b_c1' % tango_base
        ),
        coil2_c2 = device('nicos.devices.tango.DigitalOutput',
            description = 'Coil 2: Capacitor bank 2',
            tangodevice = '%s/cbox/plc_b_c2' % tango_base
        ),
        coil2_c3 = device('nicos.devices.tango.DigitalOutput',
            description = 'Coil 2: Capacitor bank 3',
            tangodevice = '%s/cbox/plc_b_c3' % tango_base
        ),
        coil2_c1c2serial = device('nicos.devices.tango.DigitalOutput',
            description = 'Coil 2: Use c1 and c2 in serial instead of parallel',
            tangodevice = '%s/cbox/plc_b_c1c2serial' % tango_base
        ),
        coil2_transformer = device('nicos.devices.tango.DigitalOutput',
            description = 'Coil 2: Used to manipulate the coil resistance to match the power amplifier resistance',
            tangodevice = '%s/cbox/plc_b_transformer' % tango_base
        ),
    ),
)
