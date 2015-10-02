# pylint: skip-file

# typical PGAA application

from nicos import session

loaded_setups = session.loaded_setups

if 'pgaa' in loaded_setups:
    printwarning('Execute PGAA specific tests')
    sample_motor.status(0)
    samplepos.status(0)
    maw(shutter, 'open')
    read(shutter)
    shutter.read(0)
    scan(sample_motor, [4, 74, 144, 214, 284, 354, ])
    scan(sample_pos, [0, 1, 2, 3, 4, 5, ])
    maw(shutter, 'closed')
