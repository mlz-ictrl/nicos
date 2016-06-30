description = 'sps devices'

group = 'optional'

sps_base = 'tango://phys.spheres.frm2:10000/spheres/profibus/sps_'

analogs = [
    {'name': 'rpower', 'desc': 'reactor power', 'unit': 'MW', 'low': False},
    {'name': 'chop_vib1', 'desc': 'chopper primary bearing vibration', 'unit': 'mm/s', 'low': True},
    {'name': 'chop_vib2', 'desc': 'chopper secondary bearing vibration', 'unit': 'mm/s', 'low': True},
    {'name': 'chop_spm1', 'desc': 'chopper primary bearing volume', 'unit': 'dB', 'low': True},
    {'name': 'chop_spm2', 'desc': 'chopper secondary bearing volume', 'unit': 'dB', 'low': True},
    {'name': 'chop_tmpmot', 'desc': 'chopper motor temperature', 'unit': 'deg C', 'low': True},
    {'name': 'chop_curr', 'desc': 'chopper motor current', 'unit': 'A', 'low': True},
    {'name': 'chop_freq', 'desc': 'chopper frequency', 'unit': 'Hz', 'low': True},
    {'name': 'chop_tmp1', 'desc': 'chopper primary bearing temperature', 'unit': 'deg C', 'low': True},
    {'name': 'chop_tmp2', 'desc':'chopper secondary bearing temperature' , 'unit': 'deg C', 'low': True},
    {'name': 'oxygen_floor1', 'desc': 'oxygen floor 1', 'unit': 'percent', 'low': True},
    {'name': 'oxygen_ceil1', 'desc': 'oxygen ceiling 1', 'unit': 'percent', 'low': True},
    {'name': 'oxygen_floor2', 'desc': 'oxygen floor 2', 'unit': 'percent', 'low': True},
    {'name': 'oxygen_ceil2', 'desc': 'oxygen ceiling 2', 'unit': 'percent', 'low': True},
    {'name': 'sel_tmp1', 'desc': 'selector rotor temperature', 'unit': 'deg C', 'low': True},
    {'name': 'sel_water_tmp_i', 'desc': 'selector water in temperature', 'unit': 'deg C', 'low': True},
    {'name': 'sel_water_tmp_f', 'desc': 'selector water out temperature', 'unit': 'deg C', 'low': True},
    {'name': 'sel_water_flow', 'desc': 'selector water out temperature', 'unit': 'deg C', 'low': True},
    {'name': 'sel_freq', 'desc': 'selector frequency', 'unit': 'Hz', 'low': True},
    {'name': 'sel_vib1', 'desc': 'sleector vibration 1', 'unit': 'BCU', 'low': True},
    {'name': 'sel_vib2', 'desc': 'selector vibration 2', 'unit': 'mm/s', 'low': True},
    {'name': 'sel_vacuum', 'desc': 'selector vacuum', 'unit': 'prop to lg mbar', 'low': True},
    {'name': 'dop_tmp_L_mot', 'desc': 'doppler left motor temperature', 'unit': 'deg C', 'low': True},
    {'name': 'dop_tmp_L_i', 'desc': 'doppler left motor water in temperature', 'unit': 'deg C', 'low': True},
    {'name': 'dop_tmp_L_f', 'desc': 'doppler left motor water out temperature', 'unit': 'deg C', 'low': True},
    {'name': 'dop_tmp_R_mot', 'desc': 'doppler right motor temperature', 'unit': 'deg C', 'low': True},
    {'name': 'dop_tmp_R_i', 'desc': 'doppler right motor water in temperature', 'unit': 'deg C', 'low': True},
    {'name': 'dop_tmp_R_f', 'desc': 'doppler right motor water out temperature', 'unit': 'deg C', 'low': True},
    {'name': 'argon_PDIC11', 'desc': 'housing pressure difference', 'unit': 'mabr', 'low': True},
    {'name': 'argon_Pin_argon', 'desc': 'argon supply pressure', 'unit': 'bar', 'low': True},
    {'name': 'argon_Pin_air', 'desc': 'air supply pressure', 'unit': 'bar', 'low': True},
    {'name': 'argon_flow1', 'desc': 'RV1 flow', 'unit': 'm3/h', 'low': True},
    {'name': 'argon_volume1', 'desc': 'RV1 input volume', 'unit': 'm3', 'low': True},
    {'name': 'argon_flow2', 'desc': 'RV2 flow', 'unit': 'm3/h', 'low': True},
    {'name': 'argon_volume2', 'desc': 'RV2 input volume', 'unit': 'm3', 'low': True},
    {'name': 'argon_step', 'desc': 'argon controll status', 'unit': '', 'low': True},
    {'name': 'housing_tmp', 'desc': 'housing temperature', 'unit': 'deg C', 'low': True},
    {'name': 'hall_air_P', 'desc': 'hall air pressure', 'unit': 'mbar', 'low': True},
    {'name': 'seal_hatch_P', 'desc': 'hatch seal pressure', 'unit': 'bar', 'low': True},
    {'name': 'seal_door_P', 'desc': 'door seal pressure', 'unit': 'bar', 'low': True},
]

digitals = [
    {'name': 'upstream_connection', 'mapping': 4, 'desc': 'NLA-Leittechnik', 'low': True},
    {'name': 'upstream_approval', 'mapping': 5, 'desc': 'NLA-Leittechnik Freigabe', 'low': True},
    {'name': 'shut_remote', 'mapping': 0, 'desc': 'toggle switch remote', 'low': True},
    {'name': 'shut_key', 'mapping': 4, 'desc': 'shutter relaease', 'low': True},
    {'name': 'shut_indicator', 'mapping': 6, 'desc': 'off-limit area indicator', 'low': True},
    {'name': 'door_closed_locked', 'mapping': 0, 'desc': 'door closed and locked', 'low': True},
    {'name': 'housing_hatch_open', 'mapping': 0, 'desc': 'housing hatch open', 'low': True},
    {'name': 'housing_clearance', 'mapping': 6, 'desc': 'housing clearance', 'low': True},
    {'name': 'housing_tmp_alert', 'mapping': 6, 'desc': 'housing temperature alert', 'low': True},
    {'name': 'housing_chain1_open', 'mapping': 0, 'desc': 'housing chain 1 open', 'low': True},
    {'name': 'housing_chain2_open', 'mapping': 0, 'desc': 'housing chain 2 open', 'low': True},
    {'name': 'housing_chain3_open', 'mapping': 0, 'desc': 'housing chain stairs open', 'low': True},
    {'name': 'compressed_air', 'mapping': 4, 'desc': 'compressed air status', 'low': True},
    {'name': 'emergency_stop_ok', 'mapping': 5, 'desc': 'emergency stop', 'low': True},
    {'name': 'sps_fault', 'mapping': 6, 'desc': 'F-SPS fault', 'low': True},
    {'name': 'sps_ack_req', 'mapping': 6, 'desc': 'F-SPS acknowledge required', 'low': True},
    {'name': 'argon_indicator', 'mapping': 6, 'desc': 'argon indicator', 'low': True},
    {'name': 'argon_horn', 'mapping': 6, 'desc': 'argon horn', 'low': True},
    {'name': 'argon_Pin_argon_alert', 'mapping': 6, 'desc': 'PI2: argon supply underpressure', 'low': True},
    {'name': 'argon_Pin_air_alert', 'mapping': 6, 'desc': 'PI3: air supply underpressure', 'low': True},
    {'name': 'argon_PDIC11_alert', 'mapping': 7, 'desc': 'pressure difference 1', 'low': True},
    {'name': 'argon_PDIC12_alert', 'mapping': 7, 'desc': 'pressure difference 2', 'low': True},
    {'name': 'argon_emergency_stop', 'mapping': 6, 'desc': 'argon emergency stop', 'low': True},
]

clusters = [
    {'name': 'upstream_shut1', 'mapping': 0, 'desc': '6-fold shutter', 'low': True},
    {'name': 'upstream_shut2', 'mapping': 0, 'desc': 'fastshutter NL6', 'low': True},
    {'name': 'upstream_shut3', 'mapping': 0, 'desc': 'DNS shutter', 'low': True},
    {'name': 'shut', 'mapping': 0, 'desc': 'experiment shutter', 'low': True},
    {'name': 'argon_AV1', 'mapping': 1, 'desc': 'exhaust bottom ventilator', 'low': True},
    {'name': 'argon_K1', 'mapping': 0, 'desc': 'exhaust bottom hatch', 'low': True},
    {'name': 'argon_K2', 'mapping': 0, 'desc': 'exhaust top hatch', 'low': True},
    {'name': 'argon_MV1', 'mapping': 0, 'desc': 'argon supply', 'low': True},
    {'name': 'argon_MV2', 'mapping': 0, 'desc': 'argon inlet', 'low': True},
    {'name': 'argon_MV3', 'mapping': 0, 'desc': 'compressed air inlet', 'low': True},
    {'name': 'argon_MV4', 'mapping': 0, 'desc': 'compressed air supply', 'low': True},
    {'name': 'argon_MV9', 'mapping': 0, 'desc': 'u pipe', 'low': True},
    {'name': 'argon_MV10', 'mapping': 2, 'desc': 'flush air', 'low': True},
]

mappings = [
    {'closed': 0, 'open': 1},
    {'off': 0, 'on': 1},
    {'closed': 0, 'open': 1, 'flows': 2},
    {'fault': 0, 'ok': 1},
    {'no': 0, 'yes': 1},
    {'not active': 0, 'active': 1},
    {'tbd-0': 0, 'tbd-1': 1},
    {'normal': 0, 'high': 1}
]

devices = dict()

for analog in analogs:
    devices[analog['name']] = device('nicos.devices.tango.AnalogInput',
                                     description=analog['desc'],
                                     tangodevice=sps_base + analog['name'],
                                     unit=analog['unit'],
                                     lowlevel=analog['low']
                                    )

for digital in digitals:
    devices[digital['name']] = device('nicos.devices.tango.NamedDigitalInput',
                                      description=digital['desc'],
                                      tangodevice=sps_base + digital['name'],
                                      mapping=mappings[digital['mapping']],
                                      lowlevel=digital['low']
                                     )

for cluster in clusters:
    devices[cluster['name']] = device('nicos.devices.tango.NamedDigitalInput',
                                      description=cluster['desc'],
                                      tangodevice=sps_base + cluster['name'],
                                      mapping=mappings[cluster['mapping']],
                                      lowlevel=cluster['low']
                                     )
