description = 'The Vinci high pressure syringe pump'

pv_root = 'SE-SEE:SE-VINP-001:'

devices = dict(
    vinci_pressure=device(
        'nicos.devices.epics.pva.EpicsAnalogMoveable',
        description='Pressure',
        readpv='{}Pressure-R'.format(pv_root),
        writepv='{}PM_Pressure-S'.format(pv_root),
        pva=True,
        monitor=True,
    ),
    vinci_pressure_SP=device(
        'nicos.devices.epics.pva.EpicsAnalogMoveable',
        description='Pressure setpoint',
        readpv='{}PM_Pressure-S'.format(pv_root),
        writepv='{}PM_Pressure-S'.format(pv_root),
        pva=True,
        monitor=True,
    ),
    vinci_volume=device(
        'nicos.devices.epics.pva.EpicsReadable',
        description='Pump volume',
        readpv='{}Volume-R'.format(pv_root),
        pva=True,
        monitor=True,
    ),
    vinci_flowrate=device(
        'nicos.devices.epics.pva.EpicsReadable',
        description='Pump flow-rate',
        readpv='{}Flow-R'.format(pv_root),
        pva=True,
        monitor=True,
    ),
    vinci_process_valve=device(
        'nicos.devices.epics.pva.EpicsMappedMoveable',
        description='Status of the process valve',
        readpv='{}ProcValveOpened-RB'.format(pv_root),
        writepv='{}ProcValveOpen-S'.format(pv_root),
        pva=True,
        monitor=True,
    ),
    vinci_tank_valve=device(
        'nicos.devices.epics.pva.EpicsMappedMoveable',
        description='Status of the tank valve',
        readpv='{}TankValveOpened-RB'.format(pv_root),
        writepv='{}TankValveOpen-S'.format(pv_root),
        pva=True,
        monitor=True,
    ),
    vinci_pump=device(
        'nicos.devices.epics.pva.EpicsMappedMoveable',
        description='Status of the pump',
        readpv='{}Stopped-RB'.format(pv_root),
        writepv='{}Start-S'.format(pv_root),
        pva=True,
        monitor=True,
    ),
)
