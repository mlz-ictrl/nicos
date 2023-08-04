description = 'Temperature measurement and control'

devices = dict(
    T01=device(
        'nicos_ess.estia.devices.pt100.EpicsPT100Temperature',
        description='Reference Air',
        readpv='estia-selpt100-001:Calc_out_01',
        statuspv='estia-selpt100-001:AnalogStatus_01',
        unit='C',
    ),
    T02=device(
        'nicos_ess.estia.devices.pt100.EpicsPT100Temperature',
        description='Upstream Foot Air',
        readpv='estia-selpt100-001:Calc_out_02',
        statuspv='estia-selpt100-001:AnalogStatus_02',
        unit='C',
    ),
    T03=device(
        'nicos_ess.estia.devices.pt100.EpicsPT100Temperature',
        description='Downstream Foot Air',
        readpv='estia-selpt100-001:Calc_out_03',
        statuspv='estia-selpt100-001:AnalogStatus_03',
        unit='C',
    ),
    T04=device(
        'nicos_ess.estia.devices.pt100.EpicsPT100Temperature',
        description='Vacuum Vessel Top',
        readpv='estia-selpt100-001:Calc_out_04',
        statuspv='estia-selpt100-001:AnalogStatus_04',
        unit='C',
    ),
    T05=device(
        'nicos_ess.estia.devices.pt100.EpicsPT100Temperature',
        description='In Vacuum Baseplate',
        readpv='estia-selpt100-001:Calc_out_05',
        statuspv='estia-selpt100-001:AnalogStatus_05',
        unit='C',
    ),
    T06=device(
        'nicos_ess.estia.devices.pt100.EpicsPT100Temperature',
        description='Upstream Carrier',
        readpv='estia-selpt100-001:Calc_out_06',
        statuspv='estia-selpt100-001:AnalogStatus_06',
        unit='C',
    ),
    T07=device(
        'nicos_ess.estia.devices.pt100.EpicsPT100Temperature',
        description='Upstream Foot',
        readpv='estia-selpt100-001:Calc_out_07',
        statuspv='estia-selpt100-001:AnalogStatus_07',
        unit='C',
    ),
    T08=device(
        'nicos_ess.estia.devices.pt100.EpicsPT100Temperature',
        description='Downstream Foot',
        readpv='estia-selpt100-001:Calc_out_08',
        statuspv='estia-selpt100-001:AnalogStatus_08',
        unit='C',
    ),
    T09=device(
        'nicos_ess.estia.devices.pt100.EpicsPT100Temperature',
        description='Downstream Carrier',
        readpv='estia-selpt100-001:Calc_out_09',
        statuspv='estia-selpt100-001:AnalogStatus_09',
        unit='C',
    ),
    T10=device(
        'nicos_ess.estia.devices.pt100.EpicsPT100Temperature',
        description='Center Carrier',
        readpv='estia-selpt100-001:Calc_out_10',
        statuspv='estia-selpt100-001:AnalogStatus_10',
        unit='C',
    ),
    T11=device(
        'nicos_ess.estia.devices.pt100.EpicsPT100Temperature',
        description='Metrology Rack',
        readpv='estia-selpt100-001:Calc_out_11',
        statuspv='estia-selpt100-001:AnalogStatus_11',
        unit='C',
    ),
    T12=device(
        'nicos_ess.estia.devices.pt100.EpicsPT100Temperature',
        description='Metrology Cart',
        readpv='estia-selpt100-001:Calc_out_12',
        statuspv='estia-selpt100-001:AnalogStatus_12',
        unit='C',
    ),
    julabo=device(
        'nicos_ess.estia.devices.julabo.TemperatureController',
        description='The Julabo',
        pvprefix='ESTIA-JUL25HL-001',
        readpv='ESTIA-JUL25HL-001:TEMP',
        writepv='ESTIA-JUL25HL-001:TEMP:SP1',
        targetpv='ESTIA-JUL25HL-001:TEMP:SP1:RBV',
        statuscodepv='ESTIA-JUL25HL-001:STATUS',
        statusmsgpv='ESTIA-JUL25HL-001:STATUSc',
        switchpvs={
            'read': 'ESTIA-JUL25HL-001:MODE:SP',
            'write': 'ESTIA-JUL25HL-001:MODE:SP'
        },
        switchstates={
            'enable': 1,
            'disable': 0
        },
        precision=0.5,
    ),
)
