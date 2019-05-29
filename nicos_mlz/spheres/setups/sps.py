# -*- coding: utf-8 -*-

description = 'sps devices'

group = 'lowlevel'

tangohost = 'phys.spheres.frm2'
profibus_base = 'tango://%s:10000/spheres/profibus/sps_' % tangohost
profinet_base = 'tango://%s:10000/spheres/profinet/back_' % tangohost

vis = {'metadata', 'devlist', 'namespace'}

analogs = dict(
    rpower = dict(desc='reactor power', unit='MW', vis=vis),
    chop_vib1 = dict(desc='chopper primary bearing vibration', unit='mm/s', vis=()),
    chop_vib2 = dict(desc='chopper secondary bearing vibration', unit='mm/s', vis=()),
    chop_spm1 = dict(desc='chopper primary bearing volume', unit='dB', vis=()),
    chop_spm2 = dict(desc='chopper secondary bearing volume', unit='dB', vis=()),
    chop_tmpmot = dict(desc='chopper motor temperature', unit='deg C', vis=()),
    chop_curr = dict(desc='chopper motor current', unit='A', vis=()),
    chop_freq = dict(desc='chopper frequency', unit='Hz', vis=()),
    chop_tmp1 = dict(desc='chopper primary bearing temperature', unit='deg C', vis=()),
    chop_tmp2 = dict(desc='chopper secondary bearing temperature', unit='deg C', vis=()),
    oxygen_floor1 = dict(desc='oxygen floor 1', unit='percent', vis=()),
    oxygen_ceil1 = dict(desc='oxygen ceiling 1', unit='percent', vis=()),
    oxygen_floor2 = dict(desc='oxygen floor 2', unit='percent', vis=()),
    oxygen_ceil2 = dict(desc='oxygen ceiling 2', unit='percent', vis=()),
    sel_tmp1 = dict(desc='selector rotor temperature', unit='deg C', vis=()),
    sel_water_tmp_i = dict(desc='selector water in temperature', unit='deg C', vis=()),
    sel_water_tmp_f = dict(desc='selector water out temperature', unit='deg C', vis=()),
    sel_water_flow = dict(desc='selector water out temperature', unit='deg C', vis=()),
    sel_freq = dict(desc='selector frequency', unit='Hz', vis=()),
    sel_vib1 = dict(desc='sleector vibration 1', unit='BCU', vis=()),
    sel_vib2 = dict(desc='selector vibration 2', unit='mm/s', vis=()),
    sel_vacuum = dict(desc='selector vacuum', unit='prop to lg mbar', vis=()),
    dop_tmp_L_mot = dict(desc='doppler left motor temperature', unit='deg C', vis=()),
    dop_tmp_L_i = dict(desc='doppler left motor water in temperature', unit='deg C', vis=()),
    dop_tmp_L_f = dict(desc='doppler left motor water out temperature', unit='deg C', vis=()),
    dop_tmp_R_mot = dict(desc='doppler right motor temperature', unit='deg C', vis=()),
    dop_tmp_R_i = dict(desc='doppler right motor water in temperature', unit='deg C', vis=()),
    dop_tmp_R_f = dict(desc='doppler right motor water out temperature', unit='deg C', vis=()),
    argon_PDIC11 = dict(desc='housing pressure difference', unit='mbar', vis=()),
    argon_Pin_argon = dict(desc='argon supply pressure', unit='bar', vis=()),
    argon_Pin_air = dict(desc='air supply pressure', unit='bar', vis=()),
    argon_flow1 = dict(desc='RV1 flow', unit='m3/h', vis=()),
    argon_volume1 = dict(desc='RV1 input volume', unit='m3', vis=()),
    argon_flow2 = dict(desc='RV2 flow', unit='m3/h', vis=()),
    argon_volume2 = dict(desc='RV2 input volume', unit='m3', vis=()),
    argon_step = dict(desc='argon controll status', unit='', vis=()),
    housing_tmp = dict(desc='housing temperature', unit='deg C', vis=()),
    hall_air_P = dict(desc='hall air pressure', unit='mbar', vis=()),
    seal_hatch_P = dict(desc='hatch seal pressure', unit='bar', vis=()),
    seal_door_P = dict(desc='door seal pressure', unit='bar', vis=()),
    chopper_vac = dict(desc='chopper vacuum', unit='mbar', vis=()),
    nguide_vac = dict(desc='neutronguide vacuum', unit='mbar', vis=()),
    nguide_he = dict(desc='neutronguide helium percentage', unit='percent', vis=()),
)

digitals = dict(
    upstream_connection = dict(mapping=4, desc='NLA-Leittechnik', unit='', vis=()),
    upstream_approval = dict(mapping=5, desc='NLA-Leittechnik Freigabe', unit='', vis=()),
    shut_remote = dict(mapping=0, desc='toggle switch remote', unit='', vis=()),
    shut_key = dict(mapping=4, desc='shutter release', unit='', vis=()),
    shut_indicator = dict(mapping=6, desc='off-limit area indicator', unit='', vis=()),
    door_closed_locked = dict(mapping=4, desc='door closed and locked', unit='', vis=()),
    housing_hatch_open = dict(mapping=0, desc='housing hatch open', unit='', vis=()),
    housing_clearance = dict(mapping=4, desc='housing clearance', unit='', vis=()),
    housing_tmp_alert = dict(mapping=6, desc='housing temperature alert', unit='', vis=()),
    housing_chain1_open = dict(mapping=0, desc='housing chain 1 open', unit='', vis=()),
    housing_chain2_open = dict(mapping=0, desc='housing chain 2 open', unit='', vis=()),
    housing_chain3_open = dict(mapping=0, desc='housing chain stairs open', unit='', vis=()),
    compressed_air = dict(mapping=4, desc='compressed air status', unit='', vis=()),
    emergency_stop_ok = dict(mapping=5, desc='emergency stop', unit='', vis=()),
    sps_fault = dict(mapping=4, desc='F-SPS fault', unit='', vis=()),
    sps_ack_req = dict(mapping=4, desc='F-SPS acknowledge required', unit='', vis=()),
    argon_indicator = dict(mapping=6, desc='argon indicator', unit='', vis=()),
    argon_horn = dict(mapping=6, desc='argon horn', unit='', vis=()),
    argon_Pin_argon_alert = dict(mapping=6, desc='PI2: argon supply underpressure', unit='', vis=()),
    argon_Pin_air_alert = dict(mapping=6, desc='PI3: air supply underpressure', unit='', vis=()),
    argon_PDIC11_alert = dict(mapping=7, desc='pressure difference 1', unit='', vis=()),
    argon_PDIC12_alert = dict(mapping=7, desc='pressure difference 2', unit='', vis=()),
    argon_emergency_stop = dict(mapping=6, desc='argon emergency stop', unit='', vis=()),
)

clusters = dict(
    upstream_shut1 = dict(mapping=0, desc='6-fold shutter', unit='', vis=()),
    upstream_shut2 = dict(mapping=0, desc='fastshutter NL6', unit='', vis=()),
    upstream_shut3 = dict(mapping=0, desc='DNS shutter', unit='', vis=()),
    shut = dict(mapping=0, desc='experiment shutter', unit='', vis=()),
    argon_AV1 = dict(mapping=1, desc='exhaust bottom ventilator', unit='', vis=()),
    argon_K1 = dict(mapping=0, desc='exhaust bottom hatch', unit='', vis=()),
    argon_K2 = dict(mapping=0, desc='exhaust top hatch', unit='', vis=()),
    argon_MV1 = dict(mapping=0, desc='argon supply', unit='', vis=()),
    argon_MV2 = dict(mapping=0, desc='argon inlet', unit='', vis=()),
    argon_MV3 = dict(mapping=0, desc='compressed air inlet', unit='', vis=()),
    argon_MV4 = dict(mapping=0, desc='compressed air supply', unit='', vis=()),
    argon_MV9 = dict(mapping=0, desc='u pipe', unit='', vis=()),
    argon_MV10 = dict(mapping=2, desc='flush air', unit='', vis=()),
)

background = dict(
    current = dict(desc='backgroundchopper current', limits=None, unit='A', vis=()),
    flow = dict(desc='backgroundchopper water flow', limits=None, unit='', vis=()),
    frequency = dict(desc='backgroundchopper frequency', limits=None, unit='Hz', vis=vis),
    mode = dict(desc='backgroundchopper mode (1:x)', limits=None, unit='', vis=vis),
    offset = dict(desc='backgroundchopper offset to pst', limits=None, unit='deg', vis=vis),
    spm1 = dict(desc='backgroundchopper primary bearing force', limits=None, unit='mg', vis=()),
    spm2 = dict(desc='backgroundchopper primary bearing force', limits=None, unit='mg', vis=()),
    temperature = dict(desc='backgroundchopper temperature', limits=None, unit='deg C', vis=()),
    vib = dict(desc='backgroundchopper vibration', limits=None, unit='mm/s', vis=()),
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
    devices[name] = device('nicos.devices.entangle.AnalogInput',
        description=analog['desc'],
        tangodevice=profibus_base + name,
        unit=analog['unit'],
        visibility=analog['vis']
    )

for name, digital in digitals.items():
    devices[name] = device('nicos.devices.entangle.NamedDigitalInput',
        description=digital['desc'],
        tangodevice=profibus_base + name,
        unit=digital['unit'],
        mapping=mappings[digital['mapping']],
        visibility=digital['vis']
    )

for name, cluster in clusters.items():
    devices[name] = device('nicos.devices.entangle.NamedDigitalInput',
        description=cluster['desc'],
        tangodevice=profibus_base + name,
        unit=cluster['unit'],
        mapping=mappings[cluster['mapping']],
        visibility=cluster['vis']
    )

for name, dev in background.items():
    devices['back_' + name] = device('nicos.devices.entangle.AnalogInput',
        description=dev['desc'],
        tangodevice=profinet_base + name,
        unit=dev['unit'],
        visibility=dev['vis'],
        warnlimits=dev['limits']
    )
