# pylint: skip-file

# test: subdirs = frm2
# test: setups = 07_refsans_full
# test: setupcode = SetDetectors(det)
# test: needs = configobj

read(optic)
targets = [
    'horizontal',

    # Allowed, but not right configured !!!
    # '12mrad_b3_789',
    # '12mrad_b3_12.000',
    # '12mrad_b3_13.268',
    # '12mrad_b2_12.254_eng',
    # '12mrad_b2_12.88_big',
    # '48mrad',

    # configured, but not allowed !!!
    # '54mrad',

    # numbers are not working at the moment
    # 0,
    # 24,
    # 48,
]
for t in targets:
    maw(optic, t)
    read(optic)

modes = [
    '12mrad234',
    '12mrad789',
    '48mrad',
    'fc:nok5a',
    'fc:nok5b',
    'fc:nok6',
    'fc:nok7',
    'fc:nok8',
    'fc:nok9',
    'gisans',
    'gisans789',
    'neutronguide',
    'point',
    'vc:nok5a',
    'vc:nok5a_fc:nok5b',
    'vc:nok5a_fc:nok6',
    'vc:nok5a_fc:nok7',
    'vc:nok5a_fc:nok8',
    'vc:nok5a_fc:nok9',

    # The following values are configured but not allowed !!!
    # 'vc:nok5b',
    # 'vc:nok5b_fc:nok6',
    # 'vc:nok5b_fc:nok7',
    # 'vc:nok5b_fc:nok8',
    # 'vc:nok5b_fc:nok9',
    # 'vc:nok6',
    # 'vc:nok6_fc:nok7',
    # 'vc:nok6_fc:nok8',
    # 'vc:nok6_fc:nok9',
    # 'vc:nok7',
    # 'vc:nok7_fc:nok8',
    # 'vc:nok7_fc:nok9',
    # 'vc:nok8',
    # 'vc:nok8_fc:nok9',
    # 'vc:nok9',

    # Allowed but not configured !!!
    # 'debug',
    # '54mrad',
]
for m in modes:
    optic.mode = m
    print(optic.mode)
