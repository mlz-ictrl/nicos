# -*- coding: utf-8 -*-

description = 'sps devices'

group = 'lowlevel'

tangohost = 'phys.spheres.frm2'
profibus_base = 'tango://%s:10000/spheres/profibus/sps_' % tangohost
profinet_base = 'tango://%s:10000/spheres/profinet/back_' % tangohost

analogs = dict(
    rpower = dict(desc='reactor power', unit='MW', low=False),
    chop_vib1 = dict(desc='chopper primary bearing vibration', unit='mm/s', low=True),
    chop_vib2 = dict(desc='chopper secondary bearing vibration', unit='mm/s', low=True),
    chop_spm1 = dict(desc='chopper primary bearing volume', unit='dB', low=True),
    chop_spm2 = dict(desc='chopper secondary bearing volume', unit='dB', low=True),
    chop_tmpmot = dict(desc='chopper motor temperature', unit='deg C', low=True),
    chop_curr = dict(desc='chopper motor current', unit='A', low=True),
    chop_freq = dict(desc='chopper frequency', unit='Hz', low=True),
    chop_tmp1 = dict(desc='chopper primary bearing temperature', unit='deg C', low=True),
    chop_tmp2 = dict(desc='chopper secondary bearing temperature', unit='deg C', low=True),
    oxygen_floor1 = dict(desc='oxygen floor 1', unit='percent', low=True),
    oxygen_ceil1 = dict(desc='oxygen ceiling 1', unit='percent', low=True),
    oxygen_floor2 = dict(desc='oxygen floor 2', unit='percent', low=True),
    oxygen_ceil2 = dict(desc='oxygen ceiling 2', unit='percent', low=True),
    sel_tmp1 = dict(desc='selector rotor temperature', unit='deg C', low=True),
    sel_water_tmp_i = dict(desc='selector water in temperature', unit='deg C', low=True),
    sel_water_tmp_f = dict(desc='selector water out temperature', unit='deg C', low=True),
    sel_water_flow = dict(desc='selector water out temperature', unit='deg C', low=True),
    sel_freq = dict(desc='selector frequency', unit='Hz', low=True),
    sel_vib1 = dict(desc='sleector vibration 1', unit='BCU', low=True),
    sel_vib2 = dict(desc='selector vibration 2', unit='mm/s', low=True),
    sel_vacuum = dict(desc='selector vacuum', unit='prop to lg mbar', low=True),
    dop_tmp_L_mot = dict(desc='doppler left motor temperature', unit='deg C', low=True),
    dop_tmp_L_i = dict(desc='doppler left motor water in temperature', unit='deg C', low=True),
    dop_tmp_L_f = dict(desc='doppler left motor water out temperature', unit='deg C', low=True),
    dop_tmp_R_mot = dict(desc='doppler right motor temperature', unit='deg C', low=True),
    dop_tmp_R_i = dict(desc='doppler right motor water in temperature', unit='deg C', low=True),
    dop_tmp_R_f = dict(desc='doppler right motor water out temperature', unit='deg C', low=True),
    argon_PDIC11 = dict(desc='housing pressure difference', unit='mbar', low=True),
    argon_Pin_argon = dict(desc='argon supply pressure', unit='bar', low=True),
    argon_Pin_air = dict(desc='air supply pressure', unit='bar', low=True),
    argon_flow1 = dict(desc='RV1 flow', unit='m3/h', low=True),
    argon_volume1 = dict(desc='RV1 input volume', unit='m3', low=True),
    argon_flow2 = dict(desc='RV2 flow', unit='m3/h', low=True),
    argon_volume2 = dict(desc='RV2 input volume', unit='m3', low=True),
    argon_step = dict(desc='argon controll status', unit='', low=True),
    housing_tmp = dict(desc='housing temperature', unit='deg C', low=True),
    hall_air_P = dict(desc='hall air pressure', unit='mbar', low=True),
    seal_hatch_P = dict(desc='hatch seal pressure', unit='bar', low=True),
    seal_door_P = dict(desc='door seal pressure', unit='bar', low=True),
    chopper_vac = dict(desc='chopper vacuum', unit='mbar', low=True),
    nguide_vac = dict(desc='neutronguide vacuum', unit='mbar', low=True),
    nguide_he = dict(desc='neutronguide helium percentage', unit='percent', low=False),
)

digitals = dict(
    upstream_connection = dict(mapping=4, desc='NLA-Leittechnik', unit='', low=True),
    upstream_approval = dict(mapping=5, desc='NLA-Leittechnik Freigabe', unit='', low=True),
    shut_remote = dict(mapping=0, desc='toggle switch remote', unit='', low=True),
    shut_key = dict(mapping=4, desc='shutter release', unit='', low=True),
    shut_indicator = dict(mapping=6, desc='off-limit area indicator', unit='', low=True),
    door_closed_locked = dict(mapping=4, desc='door closed and locked', unit='', low=True),
    housing_hatch_open = dict(mapping=0, desc='housing hatch open', unit='', low=True),
    housing_clearance = dict(mapping=4, desc='housing clearance', unit='', low=True),
    housing_tmp_alert = dict(mapping=6, desc='housing temperature alert', unit='', low=True),
    housing_chain1_open = dict(mapping=0, desc='housing chain 1 open', unit='', low=True),
    housing_chain2_open = dict(mapping=0, desc='housing chain 2 open', unit='', low=True),
    housing_chain3_open = dict(mapping=0, desc='housing chain stairs open', unit='', low=True),
    compressed_air = dict(mapping=4, desc='compressed air status', unit='', low=True),
    emergency_stop_ok = dict(mapping=5, desc='emergency stop', unit='', low=True),
    sps_fault = dict(mapping=4, desc='F-SPS fault', unit='', low=True),
    sps_ack_req = dict(mapping=4, desc='F-SPS acknowledge required', unit='', low=True),
    argon_indicator = dict(mapping=6, desc='argon indicator', unit='', low=True),
    argon_horn = dict(mapping=6, desc='argon horn', unit='', low=True),
    argon_Pin_argon_alert = dict(mapping=6, desc='PI2: argon supply underpressure', unit='', low=True),
    argon_Pin_air_alert = dict(mapping=6, desc='PI3: air supply underpressure', unit='', low=True),
    argon_PDIC11_alert = dict(mapping=7, desc='pressure difference 1', unit='', low=True),
    argon_PDIC12_alert = dict(mapping=7, desc='pressure difference 2', unit='', low=True),
    argon_emergency_stop = dict(mapping=6, desc='argon emergency stop', unit='', low=True),
)

clusters = dict(
    upstream_shut1 = dict(mapping=0, desc='6-fold shutter', unit='', low=True),
    upstream_shut2 = dict(mapping=0, desc='fastshutter NL6', unit='', low=True),
    upstream_shut3 = dict(mapping=0, desc='DNS shutter', unit='', low=True),
    shut = dict(mapping=0, desc='experiment shutter', unit='', low=True),
    argon_AV1 = dict(mapping=1, desc='exhaust bottom ventilator', unit='', low=True),
    argon_K1 = dict(mapping=0, desc='exhaust bottom hatch', unit='', low=True),
    argon_K2 = dict(mapping=0, desc='exhaust top hatch', unit='', low=True),
    argon_MV1 = dict(mapping=0, desc='argon supply', unit='', low=True),
    argon_MV2 = dict(mapping=0, desc='argon inlet', unit='', low=True),
    argon_MV3 = dict(mapping=0, desc='compressed air inlet', unit='', low=True),
    argon_MV4 = dict(mapping=0, desc='compressed air supply', unit='', low=True),
    argon_MV9 = dict(mapping=0, desc='u pipe', unit='', low=True),
    argon_MV10 = dict(mapping=2, desc='flush air', unit='', low=True),
)

background = dict(
    current = dict(desc='backgroundchopper current', limits=None, unit='A', low=True),
    flow = dict(desc='backgroundchopper water flow', limits=None, unit='', low=True),
    frequency = dict(desc='backgroundchopper frequency', limits=None, unit='Hz', low=False),
    mode = dict(desc='backgroundchopper mode (1:x)', limits=None, unit='', low=False),
    offset = dict(desc='backgroundchopper offset to pst', limits=None, unit='deg', low=False),
    spm1 = dict(desc='backgroundchopper primary bearing force', limits=None, unit='mg', low=True),
    spm2 = dict(desc='backgroundchopper primary bearing force', limits=None, unit='mg', low=True),
    temperature = dict(desc='backgroundchopper temperature', limits=None, unit='deg C', low=True),
    vib = dict(desc='backgroundchopper vibration', limits=None, unit='mm/s', low=True),
)

mappings = [
    {'closed': 0, 'open': 1},
    {'off': 0, 'on': 1},
    {'closed': 0, 'open': 1, 'flows': 2},
    {'fault': 0, 'ok': 1},
    {'no': 0, 'yes': 1},
    {'not active': 0, 'active': 1},
    {'0': 0, '1': 1},
    {'normal': 0, 'high': 1},
]

devices = dict()

for name, analog in analogs.items():
    devices[name] = device('nicos.devices.tango.AnalogInput',
        description=analog['desc'],
        tangodevice=profibus_base + name,
        unit=analog['unit'],
        lowlevel=analog['low']
    )

for name, digital in digitals.items():
    devices[name] = device('nicos.devices.tango.NamedDigitalInput',
        description=digital['desc'],
        tangodevice=profibus_base + name,
        unit=digital['unit'],
        mapping=mappings[digital['mapping']],
        lowlevel=digital['low']
    )

for name, cluster in clusters.items():
    devices[name] = device('nicos.devices.tango.NamedDigitalInput',
        description=cluster['desc'],
        tangodevice=profibus_base + name,
        unit=cluster['unit'],
        mapping=mappings[cluster['mapping']],
        lowlevel=cluster['low']
    )

for name, dev in background.items():
    devices['back_' + name] = device('nicos.devices.tango.AnalogInput',
        description=dev['desc'],
        tangodevice=profinet_base + name,
        unit=dev['unit'],
        lowlevel=dev['low'],
        warnlimits=dev['limits']
    )
