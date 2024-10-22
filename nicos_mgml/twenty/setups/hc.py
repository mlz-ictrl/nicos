description = 'Reading Keithley multimeter as a counter'

group = 'optional'

includes = ['busk6221']

devices = dict(
    HC = device('nicos_mgml.devices.heatcap.HCmeter',
        description = 'HC meater',
        fmtstr = '%.8f',
        k6221temp = 'busk6221',
        k6221heater = 'busk6221heat',
    ),
)
