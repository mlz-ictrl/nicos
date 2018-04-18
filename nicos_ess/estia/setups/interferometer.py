description = 'Prototype interferometer measurement'

ip_address = '192.168.1.1'

devices = dict(
    ids_server=device(
        'nicos_ess.estia.devices.attocube.IDS3010Server',
        ip=ip_address,
        lowlevel=True
    ),
    ih1=device(
        'nicos_ess.estia.devices.attocube.IDS3010Axis',
        axis=1,
        description='Horizontal IF axis top',
        server='ids_server'
    ),
    ih2=device(
        'nicos_ess.estia.devices.attocube.IDS3010Axis',
        axis=2,
        description='Horizontal IF axis bottom',
        server='ids_server'
    ),
    ih3=device(
        'nicos_ess.estia.devices.attocube.IDS3010Axis',
        axis=3,
        description='Cart position top',
        server='ids_server'
    ),
    IDS3010=device(
        'nicos_ess.estia.devices.attocube.IDS3010Control',
        description='Attocube IDS3010 control',
        server='ids_server'
    ),
    dhtop=device(
        'nicos_ess.estia.devices.attocube.MirrorDistance',
        axis='ih1',
        description='Horizontal distance top',
    ),
    dhbottom=device(
        'nicos_ess.estia.devices.attocube.MirrorDistance',
        axis='ih2',
        description='Horizontal distance bottom',
    ),
)
