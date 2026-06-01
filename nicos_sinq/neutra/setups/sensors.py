description = 'Beam line environmental sensors'

display_order = 95

pvprefix = 'SQ:NEUTRA:EPLUSE:'

devices = dict(
    dynamic_sensors_device = \
            device('nicos_sinq.devices.epics.dynamic.AsynDevice',
                    monitor = True,
                    readpv = pvprefix + 'ASYN',
                    devicesconfig = {
                        ('temperature', 'nicos.devices.epics.base.EpicsReadable') : {
                            'description': 'Beam line temperature',
                            'readpv': pvprefix + 'TEMP',
                        },
                        ('humidity', 'nicos.devices.epics.base.EpicsReadable') : {
                            'description': 'Beam line relative humidity',
                            'readpv': pvprefix + 'RELHUM',
                        }
                    },
                    visibility = {'metadata', 'namespace'},
            ),
)
