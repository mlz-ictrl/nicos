description = 'power supplies'

group = 'optional'

tango_base = 'tango://phys.j-nse.frm2:10000/j-nse/'

devices = dict(
    temp_rack1 = device('nicos.devices.entangle.Sensor',
        description = 'PSU Temperature in Rack 1',
        tangodevice = tango_base + 'supply_temp/pow02',
        unit = 'degC',
    ),
    temp_rack2 = device('nicos.devices.entangle.Sensor',
        description = 'PSU Temperature in Rack 2',
        tangodevice = tango_base + 'supply_temp/pow23',
        unit = 'degC',
    ),
)

labels = [
    'solmain1', 'fpi21', 'fpi', 'fpi22', 'solsample_z', 'solpi21', 'solpi21a',
    'solpi22.3', 'solpic1', 'solpic2', '', 'solmain1s', '', '', '', 'cc1r1',
    'loop0yh', 'cc3r1', 'loop0z', 'solphase1', 'solphase2', 'solanalyzer',
    'solpolarizer', 'cc1y1', 'cc1y2', 'cc3y1', 'cc3y2', 'cc1z1', 'cc1z2',
    'cc3z1', 'solphase1s', 'solmain1h', 'solsample1', 'loop1z', 'loop1y',
    'loop2z', 'loop2y', '',
]
for i in range(1, 39):
    name = 'pow%02d' % i
    devices[name] = \
        device(
            'nicos_mlz.j_nse.devices.jnse.JNSEPowerSupply',
            description = 'Power Supply Port %02d' % i,
            label = labels[i - 1],
            tangodevice = tango_base + 'supply/' + name,
            unit = 'A',
            precision = 0.002,
        )
