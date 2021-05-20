description = 'Devices for configuring FOCUS middle bank Histogram Memory'

includes = [
    'detector',
]

devices = dict(
    middle_connector = device('nicos_sinq.devices.sinqhm.connector.HttpConnector',
        description = "Connector for Histogram Memory Server",
        byteorder = configdata('config.HISTOGRAM_MEMORY_ENDIANESS'),
        baseurl = configdata('config.MIDDLEHM_MEMORY_URL'),
        base64auth = 'c3B5OjAwNw==',
        lowlevel = True
    ),
    hm_b0_ax_x = device('nicos_sinq.devices.sinqhm.configurator.HistogramConfAxis',
        description = 'Detector ID',
        lowlevel = True,
        length = 150,
        mapping = 'direct',
        label = 'Detector-ID',
        unit = '',
    ),
    hm_middle = device('nicos_sinq.devices.sinqhm.configurator.HistogramConfBank',
        description = 'FOCUS middle bank',
        lowlevel = True,
        bankid = 0,
        axes = ['hm_b0_ax_x', 'hm_ax_tof']
    ),
    middle_configurator = device('nicos_sinq.devices.sinqhm.configurator.ConfiguratorBase',
        description = 'Configurator for FOCUS middle bank',
        filler = 'tof',
        mask = '0x00F00000',
        active = '0x00200000',
        increment = 1,
        banks = ['hm_middle'],
        connector = 'middle_connector'
    ),
)
