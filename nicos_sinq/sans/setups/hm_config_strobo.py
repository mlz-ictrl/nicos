description = 'Devices for configuring Histogram Memory'

group = 'lowlevel'
excludes = ['hm_config']

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
        length = 16387, # 128x128 + 3 monitors
        mapping = 'direct',
        label = 'ID',
        unit = '',
    ),
    tof_array = device('nicos_sinq.devices.sinqhm.configurator.HistogramConfTofArray',
        description = 'TOF data array',
        dim = [
            5,
        ],
        data = [10, 20, 30, 40, 50],
        visibility = (),
        formatter = '%9d',
    ),
    hm_ax_tof = device('nicos_sinq.devices.sinqhm.configurator.HistogramConfAxis',
        description = 'TOF axis',
        visibility = (),
        mapping = 'boundary',
        array = 'tof_array',
        label = 'TOF',
        unit = 'arbitrary'
    ),
    hm_bank0 = device('nicos_sinq.devices.sinqhm.configurator.HistogramConfBank',
        description = 'HM First Bank',
        bankid = 0,
        axes = ['hm_b0_ax_x', 'hm_ax_tof']
    ),
    hm_configurator = device('nicos_sinq.devices.sinqhm.configurator.ConfiguratorBase',
        description = 'Configurator for the histogram memory',
        filler = 'tof',
        mask = '0x20000000',
        active = '0x00000000',
        increment = 1,
        banks = ['hm_bank0'],
        connector = 'hm_connector',
    ),
)
