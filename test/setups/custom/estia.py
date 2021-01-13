devices = dict(
    temperature_sensor = device('nicos_ess.estia.devices.pt100.EpicsPT100Temperature',
        readpv = 'estia-selpt100-001:Calc_out',
        statuspv = 'estia-selpt100-001:AnalogStatus',
        unit = 'C',
        description = 'Temperature Sensor'
    ),
)
