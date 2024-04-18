description = 'Stretch4 testing setup'
group = 'plugplay'

tango_base = 'tango://stretch4.kws2.frm2.tum.de:10000/box/'
s7_motor = tango_base + 's7_motor/stretch4_'
s7_io = tango_base + 's7_io/stretch4_'

devices = {
    f'{setupname}_signal': device('nicos.devices.entangle.AnalogOutput',
        description = 'Frequency of detector sync signal for all devices',
        tangodevice = tango_base + 'mux/mmperstep',
        unit = 'mm/pulse',
        fmtstr = '%.1f',
    )
}

for i in range(1, 5):
    devices[f'{setupname}_s{i}_b'] = device('nicos.devices.entangle.MotorAxis',
        description = f'Bottom axis of stretching device {i}',
        visibility = (),
        tangodevice = s7_motor + f'm{i}b',
    )
    devices[f'{setupname}_s{i}_t'] = device('nicos.devices.entangle.MotorAxis',
        description = f'Top axis of stretching device {i}',
        visibility = (),
        tangodevice = s7_motor + f'm{i}t',
    )
    devices[f'{setupname}_s{i}'] = device('nicos_mlz.kws2.devices.stretch.StretchGap',
        description = f'Stretching device {i}',
        opmode = 'centered',
        coordinates = 'opposite',
        parallel_ref = True,
        bottom = f'{setupname}_s{i}_b',
        top = f'{setupname}_s{i}_t',
    )
    devices[f'{setupname}_s{i}_signal'] = device('nicos.devices.entangle.AnalogOutput',
        description = 'Frequency of detector sync signal',
        tangodevice = s7_io + f'mmperstepm{i}',
        visibility = (),
    )
