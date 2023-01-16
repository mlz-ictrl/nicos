description = 'Prototype interferometer measurement'

devices = dict(
    pilot_laser=device(
        'nicos_ess.estia.devices.multiline.PilotLaser',
        description='Pilot laser',
        pvprefix='ESTIA-ETALON-001',
        readpv='ESTIA-ETALON-001:LaserReady-R',
        switchstates={
            'enable': 1,
            'disable': 0
        },
        switchpvs={
            'read': 'ESTIA-ETALON-001:RedPilotLaser-S',
            'write': 'ESTIA-ETALON-001:RedPilotLaser-S'
        },
        visibility=()
    ),
    ih1=device(
        'nicos_ess.estia.devices.attocube.IDS3010Axis',
        axis=1,
        description='Horizontal IF axis top',
        readpv='ESTIA-ATTOCUBE-001:Axis1:Displacement_RBV',
        pvprefix='ESTIA-ATTOCUBE-001'
    ),
    ih2=device(
        'nicos_ess.estia.devices.attocube.IDS3010Axis',
        axis=2,
        description='Horizontal IF axis bottom',
        readpv='ESTIA-ATTOCUBE-001:Axis2:Displacement_RBV',
        pvprefix='ESTIA-ATTOCUBE-001'
    ),
    ih3=device(
        'nicos_ess.estia.devices.attocube.IDS3010Axis',
        axis=3,
        description='Cart position top',
        readpv='ESTIA-ATTOCUBE-001:Axis3:Displacement_RBV',
        pvprefix='ESTIA-ATTOCUBE-001'
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
    env_humidity=device(
        'nicos.devices.epics.EpicsReadable',
        description='Environmental humidity',
        readpv='ESTIA-ETALON-001:EnvDataHum-R',
        visibility=(),
    ),
    env_pressure=device(
        'nicos.devices.epics.EpicsReadable',
        description='Environmental pressure',
        readpv='ESTIA-ETALON-001:EnvDataPress-R',
        visibility=(),
    ),
    env_temperature=device(
        'nicos.devices.epics.EpicsReadable',
        description='Environmental temperature',
        readpv='ESTIA-ETALON-001:EnvDataTemp-R',
        visibility=(),
    ),
    temp_1=device(
        'nicos.devices.epics.EpicsReadable',
        description='First temperature sensor',
        readpv='ESTIA-ETALON-001:TempSensorS1-R'
    ),
    temp_2=device(
        'nicos.devices.epics.EpicsReadable',
        description='Second temperature sensor',
        readpv='ESTIA-ETALON-001:TempSensorS2-R'
    ),
    temp_3=device(
        'nicos.devices.epics.EpicsReadable',
        description='Third temperature sensor',
        readpv='ESTIA-ETALON-001:TempSensorS3-R'
    ),
    temp_4=device(
        'nicos.devices.epics.EpicsReadable',
        description='Fourth emperature sensor',
        readpv='ESTIA-ETALON-001:TempSensorS4-R'
    ),
    multiline=device(
        'nicos_ess.estia.devices.multiline.MultilineController',
        description='Multiline interferometer controller',
        pvprefix='ESTIA-ETALON-001',
        readpv='ESTIA-ETALON-001:SelectedChannels-R',
        pilot_laser='pilot_laser',
        temperature='env_temperature',
        pressure='env_pressure',
        humidity='env_humidity'
    ),
)

for ch in range(1, 9):
    devices[f'ch{ch:02}'] = device(
        'nicos_ess.estia.devices.multiline.MultilineChannel',
        description=f'Value of channel {ch}',
        readpv=f'ESTIA-ETALON-001:Ch{ch}DataLength-R',
        latest_valid_pv=f'ESTIA-ETALON-001:Ch{ch}DataLenValid-R',
        gain_pv=f'ESTIA-ETALON-001:Ch{ch}Gain-R',
        unit='mm',
    )
