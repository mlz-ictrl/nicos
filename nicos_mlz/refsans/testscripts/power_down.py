# pylint: skip-file

# test: subdirs = frm2
# test: setups = 07_refsans_full

wichtig = [
    'this script MOVES!',
    'it should be used if a power down has to be prepared,',
    'elements are moved home or next to point of reference',
    'BUT you are at REFSANS',
    'in God we trust REFSANS should be checked',
    ]
for ele in ['b2']:
    for axis in ['r', 's']:
        CreateDevice(f'{ele}{axis}_motor')
lmsg = '_power_down'
for line in wichtig:
    printinfo(line)
set('chopper', 'delay', 0.0)
set('chopper2', 'phase', 10.0)
set('chopper3', 'phase', 10.0)
set('chopper4', 'phase', 10.0)
set('chopper5', 'phase', 10.0)
set('chopper6', 'phase', 10.0)

Liste = [
    [
        # det_yoke, 0,
        'hv_anode', 0,
        'hv_drift1', 0,
        'hv_drift2', 0,
        'hv_mon1', 0,
        'hv_mon2', 0,
        'hv_mon3', 0,
        'hv_mon4', 0,
        chopper_speed, 0,
        b2r_motor, b2r_motor.usermax,  # TODO: check if really user limits!!
    ],
    [
        b2s_motor, b2s_motor.usermin,  # TODO: check if really user limits!!
        chopper2_pos, 1,
        disc3, disc3.usermin,
        disc4, disc4.usermin,
        sc2, sc2.usermax,
    ]
]

for sub in Liste:
    maw(*sub)

lmsg += ' done'
printinfo(lmsg)
