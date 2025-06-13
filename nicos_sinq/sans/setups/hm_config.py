description = 'Devices for configuring Histogram Memory'

group = 'lowlevel'
excludes = ['hm_config_strobo']

devices = dict(
    hm_connector = device('nicos_sinq.devices.sinqhm.connector.HttpConnector',
        description = "Connector for Histogram Memory Server",
        byteorder = configdata('config.HISTOGRAM_MEMORY_ENDIANESS'),
        baseurl = configdata('config.HISTOGRAM_MEMORY_URL'),
        base64auth = 'c3B5OjAwNw==',
        visibility = (),
    ),
    hm_b0_ax_x = device('nicos_sinq.devices.sinqhm.configurator.HistogramConfAxis',
        description = 'Detector ID',
        visibility = (),
        length = 16384,
        mapping = 'direct',
        label = 'Detector-ID',
        unit = '',
    ),
    hm_bank0 = device('nicos_sinq.devices.sinqhm.configurator.HistogramConfBank',
        description = 'HM First Bank',
        visibility = (),
        bankid = 0,
        axes = ['hm_b0_ax_x']
    ),
    hm_configurator = device('nicos_sinq.devices.sinqhm.configurator.ConfiguratorBase',
        description = 'Configurator for the histogram memory',
        filler = 'dig',
        mask = '0x2000000',
        active = '0x00000000',
        increment = 1,
        banks = ['hm_bank0'],
        connector = 'hm_connector'
    ),
)
