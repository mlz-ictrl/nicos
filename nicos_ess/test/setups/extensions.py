devices = dict(
    DeviceCanDisable = device('nicos_ess.test.test_devices.test_epics_extensions'
        '.EpicsDeviceThatHasDisablePv',
        description = 'A device that HasDisablePv mixin',
        switchpvs = {
            'read': 'EPICS:Enable.RBV',
            'write': 'EPICS:Enable'
        },
        switchstates = {
            'enable': 1,
            'disable': 0
        },
    ),
)
