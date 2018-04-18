description = 'Prototype PT100 temperature measurement'

ip_address = '192.168.1.101'
AMSnetID = '5.49.88.38.1.1'

devices = dict(
    ads_server=device(
        'nicos_ess.estia.devices.beckhoff_direct.ADSServer',
        ip=ip_address,
        port=852,
        amsnetid=AMSnetID,
        timeout=10.,
        lowlevel=True
    ),
    T1=device(
        'nicos_ess.estia.devices.beckhoff_direct.PT100',
        attribute='nTempM1',
        description='Foot Sensor',
        server='ads_server',
        fmtstr='%.1f',
    ),
    T2=device(
        'nicos_ess.estia.devices.beckhoff_direct.PT100',
        attribute='nTempM2',
        description='Mapproach motor',
        server='ads_server',
        fmtstr='%.1f',
    ),
    T3=device(
        'nicos_ess.estia.devices.beckhoff_direct.PT100',
        attribute='nTempM3',
        description='Metrology rack',
        server='ads_server',
        fmtstr='%.1f',
    ),
    T4=device(
        'nicos_ess.estia.devices.beckhoff_direct.PT100',
        attribute='nTempM4',
        description='Top of Granite',
        server='ads_server',
        fmtstr='%.1f',
    ),
)
