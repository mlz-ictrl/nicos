#  -*- coding: utf-8 -*-

description = 'Setup of a Monochromator Focuing Box on PANDA'

group = 'optional'

devices = dict(
    # Nicos based access to phytron in magnet rack
    focimotorbus=device( 'panda.mcc2.TacoSerial',
                    tacodevice='//pandasrv/panda/moxa/port3',        # new value as of 2013-09-30 PC
                    lowlevel = True,
                    ),
    focibox = device( 'panda.mcc2.MCC2Monoframe',
                    bus = 'focimotorbus',
                    description = 'reads monocodes and returns which mono is connected',
                    addr = 0,
                    unit = '',
                    ),

    mfh  = device('devices.generic.DeviceAlias',
            alias='',
            description='Alias to currently used horizontal focusing motor',
    ),
    mfv  = device('devices.generic.DeviceAlias',
            alias='',
            description='Alias to currently used vertical focusing motor',
    ),
)

startupcode = '''
RemoveSetup('mono_pg', 'mono_si','mono_cu','mono_heusler')
m = focibox.read(0)
if m == 'PG':
    AddSetup('mono_pg')
elif m == 'Si':
    AddSetup('mono_si')
elif m == 'Cu':
    AddSetup('mono_cu')
elif m == 'Heusler':
    AddSetup('mono_heusler')
else:
    printerror('Wrong or no Mono on table!')
del m
'''

