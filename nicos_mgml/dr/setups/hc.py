description = 'Reading Keithley multimeter as a counter'

group = 'optional'

tango_base = 'tango://localhost:10000/dr/'

includes = ['busk6221']

devices = dict(
    busk6221heat = device('nicos.devices.entangle.StringIO',
        tangodevice = tango_base + 'k6221-heater/io',
        loglevel = 'info',
        visibility = (),
    ),
    HC = device('nicos_mgml.devices.heatcap.HCmeter',
        description = 'HC meter',
        fmtstr = '%.8f',
        k6221temp = 'busk6221',
        k6221heater = 'busk6221heat',
    ),
)
