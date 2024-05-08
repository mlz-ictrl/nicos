# pylint: skip-file

# test: subdirs = frm2
# test: setups = 07_refsans_full

wichtig = [
    'this script MOVES!',
    'it should be uses after a power down',
    'elements are referenced',
    'and moved in home',
    'BUT you are at REFSANS',
    'in God we trust REFSANS should be checked',
    ]
god = [
    'power up done:',
    'in God we trust,',
    'REFSANS should be checked! b2!',
    ]
fails = []
for line in wichtig:
    printinfo(line)

set('nok6r_motor', 'accel', 100)
set('nok6r_motor', 'speed', 100)
set('nok6s_motor', 'accel', 40)
set('nok6s_motor', 'speed', 40)

try:
    printinfo('image.listmode ', image.listmode)
    image.listmode = True   # 2021-03-29 12:43:01
    printinfo('image.listmode done')
except:
    fails.append('image missing! image.listmode = True')

if True:
    try:
        for tag in ['_motor', '_enc']:
            CreateDevice('det_yoke'+tag)
        det_yoke_motor.setPosition(det_yoke_enc.read(0))
    except:
        fails.append('det_yoke')

Liste_refmove = [
  'disc3',
  'disc4',
  'sc2',
  ]

Liste_homing1 = [
    'disc3', 0,
    'disc4', 0,
    'sc2', 0,
    ]

for tag in Liste_refmove:
    reference(tag)
maw(*Liste_homing1)

printwarning('power up done:')
for line in god:
    printinfo(line)
for line in fails:
    printerror(line)

Remark('REFSANS greets his friends')
