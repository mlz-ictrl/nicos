description = 'Temperature measurement and control'

devices = dict(
    T01 = device('nicos_ess.estia.devices.pt100.EpicsPT100Temperature',
        readpv = 'estia-selpt100-001:Calc_out_01',
        statuspv = 'estia-selpt100-001:AnalogStatus_01',
        unit = 'C',
        description = 'Reference Air'
    ),
    T02 = device('nicos_ess.estia.devices.pt100.EpicsPT100Temperature',
        readpv = 'estia-selpt100-001:Calc_out_02',
        statuspv = 'estia-selpt100-001:AnalogStatus_02',
        unit = 'C',
        description = 'Upstream Foot Air'
    ),
    T03 = device('nicos_ess.estia.devices.pt100.EpicsPT100Temperature',
        readpv = 'estia-selpt100-001:Calc_out_03',
        statuspv = 'estia-selpt100-001:AnalogStatus_03',
        unit = 'C',
        description = 'Downstream Foot Air'
    ),
    T04 = device('nicos_ess.estia.devices.pt100.EpicsPT100Temperature',
        readpv = 'estia-selpt100-001:Calc_out_04',
        statuspv = 'estia-selpt100-001:AnalogStatus_04',
        unit = 'C',
        description = 'Vacuum Vessel Top'
    ),
    T05 = device('nicos_ess.estia.devices.pt100.EpicsPT100Temperature',
        readpv = 'estia-selpt100-001:Calc_out_05',
        statuspv = 'estia-selpt100-001:AnalogStatus_05',
        unit = 'C',
        description = 'In Vacuum Baseplate'
    ),
    T06 = device('nicos_ess.estia.devices.pt100.EpicsPT100Temperature',
        readpv = 'estia-selpt100-001:Calc_out_06',
        statuspv = 'estia-selpt100-001:AnalogStatus_06',
        unit = 'C',
        description = 'Upstream Carrier'
    ),
    T07 = device('nicos_ess.estia.devices.pt100.EpicsPT100Temperature',
        readpv = 'estia-selpt100-001:Calc_out_07',
        statuspv = 'estia-selpt100-001:AnalogStatus_07',
        unit = 'C',
        description = 'Upstream Foot'
    ),
    T08 = device('nicos_ess.estia.devices.pt100.EpicsPT100Temperature',
        readpv = 'estia-selpt100-001:Calc_out_08',
        statuspv = 'estia-selpt100-001:AnalogStatus_08',
        unit = 'C',
        description = 'Downstream Foot'
    ),
    T09 = device('nicos_ess.estia.devices.pt100.EpicsPT100Temperature',
        readpv = 'estia-selpt100-001:Calc_out_09',
        statuspv = 'estia-selpt100-001:AnalogStatus_09',
        unit = 'C',
        description = 'Downstream Carrier'
    ),
    T10 = device('nicos_ess.estia.devices.pt100.EpicsPT100Temperature',
        readpv = 'estia-selpt100-001:Calc_out_10',
        statuspv = 'estia-selpt100-001:AnalogStatus_10',
        unit = 'C',
        description = 'Center Carrier'
    ),
    T11 = device('nicos_ess.estia.devices.pt100.EpicsPT100Temperature',
        readpv = 'estia-selpt100-001:Calc_out_11',
        statuspv = 'estia-selpt100-001:AnalogStatus_11',
        unit = 'C',
        description = 'Metrology Rack'
    ),
    T12 = device('nicos_ess.estia.devices.pt100.EpicsPT100Temperature',
        readpv = 'estia-selpt100-001:Calc_out_12',
        statuspv = 'estia-selpt100-001:AnalogStatus_12',
        unit = 'C',
        description = 'Metrology Cart'
    ),
    julabo = device('nicos_ess.estia.devices.julabo.EpicsJulabo',
        description = 'The Julabo',
        pvprefix = 'ESTIA-JUL25HL-001',
        readpv = 'ESTIA-JUL25HL-001:TEMP',
        writepv = 'ESTIA-JUL25HL-001:TEMP:SP1',
        targetpv = 'ESTIA-JUL25HL-001:TEMP:SP1:RBV',
        statuscodepv = 'ESTIA-JUL25HL-001:STATUS',
        statusmsgpv = 'ESTIA-JUL25HL-001:STATUSc',
        switchpvs = {
            'read': 'ESTIA-JUL25HL-001:MODE:SP',
            'write': 'ESTIA-JUL25HL-001:MODE:SP'
        },
        switchstates = {
            'enable': 1,
            'disable': 0
        },
        epicstimeout = 3.0,
        precision = 0.5,
    ),
)
