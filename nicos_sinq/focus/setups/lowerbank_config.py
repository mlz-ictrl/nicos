description = 'Devices for configuring FOCUS lower bank Histogram Memory'

includes = [
    'detector',
]

devices = dict(
    lower_connector = device('nicos_sinq.devices.sinqhm.connector.HttpConnector',
        description = "Connector for Histogram Memory Server",
        byteorder = configdata('config.HISTOGRAM_MEMORY_ENDIANESS'),
        baseurl = configdata('config.LOWERHM_MEMORY_URL'),
        base64auth = 'c3B5OjAwNw==',
        lowlevel = True
    ),
    lower_hm_b0_ax_x = device('nicos_sinq.devices.sinqhm.configurator'
        '.HistogramConfAxis',
        description = 'Detector ID',
        lowlevel = True,
        length = 116,
        mapping = 'direct',
        label = 'Detector-ID',
        unit = '',
    ),
    hm_lower = device('nicos_sinq.devices.sinqhm.configurator'
        '.HistogramConfBank',
        description = 'FOCUS lower bank',
        lowlevel = True,
        bankid = 0,
        axes = ['lower_hm_b0_ax_x', 'hm_ax_tof']
    ),
    lower_configurator = device('nicos_sinq.devices.sinqhm.configurator.ConfiguratorBase',
        description = 'Configurator for FOCUS lower bank',
        filler = 'tof',
        mask = '0x00F00000',
        active = '0x00200000',
        increment = 1,
        banks = ['hm_lower'],
        connector = 'lower_connector'
    ),
)
