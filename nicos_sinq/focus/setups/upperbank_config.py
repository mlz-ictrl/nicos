description = 'Devices for configuring FOCUS upper bank Histogram Memory'

includes = [
    'detector',
]

devices = dict(
    upper_connector = device('nicos_sinq.devices.sinqhm.connector.HttpConnector',
        description = "Connector for Histogram Memory Server",
        byteorder = configdata('config.HISTOGRAM_MEMORY_ENDIANESS'),
        baseurl = configdata('config.UPPERHM_MEMORY_URL'),
        base64auth = 'c3B5OjAwNw==',
        lowlevel = True
    ),
    upper_hm_b0_ax_x = device('nicos_sinq.devices.sinqhm.configurator.HistogramConfAxis',
        description = 'Detector ID',
        lowlevel = True,
        length = 110,
        mapping = 'direct',
        label = 'Detector-ID',
        unit = '',
    ),
    hm_upper = device('nicos_sinq.devices.sinqhm.configurator'
        '.HistogramConfBank',
        description = 'FOCUS upper bank',
        lowlevel = True,
        bankid = 0,
        axes = ['upper_hm_b0_ax_x', 'hm_ax_tof']
    ),
    upper_configurator = device('nicos_sinq.devices.sinqhm.configurator.ConfiguratorBase',
        description = 'Configurator for FOCUS upper bank',
        filler = 'tof',
        mask = '0x00F00000',
        active = '0x00200000',
        increment = 1,
        banks = ['hm_upper'],
        connector = 'upper_connector'
    ),
)
