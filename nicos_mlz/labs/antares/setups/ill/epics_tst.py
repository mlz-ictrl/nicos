description = 'Test Epics'

group = 'optional'

base_pv = 'NECTAR:Penguin:LumaCam:'
base_pv = 'office:penguin:tpx3cam:cam1:'

devices = dict(
    # test = device('nicos.devices.epics.EpicsStringMoveable',
    test = device('nicos.devices.epics.EpicsReadable',
        description = 'Test EPICS connection',
    #    readpv = base_pv + 'AcquisitionStatus',
        readpv = base_pv + 'BiasVoltage_RBV',
    #    writepv = base_pv + 'AcquisitionStatus',
    #    targetpv = base_pv + 'AcquisitionStatus',
    ),
    teststate = device('nicos.devices.epics.EpicsStringReadable',
        description = 'TODO: ',
        readpv = base_pv + 'DetectorState_RBV',
    #    writepv = 'NECTAR:Penguin:LumaCam:AcquisitionStatus',
    #    targetpv = 'NECTAR:Penguin:LumaCam:AcquisitionStatus',
    ),
)

