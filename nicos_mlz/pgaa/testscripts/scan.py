# pylint: skip-file

# test: subdirs = frm2
# test: setups = pgaa
# test: setupcode = SetDetectors(_60p, LEGe)
# test: setupcode = CreateDevice('samplemotor')

# typical PGAA application

from nicos import session

if 'pgaa' in session.loaded_setups:
    printwarning('Execute PGAA specific tests')
    status('samplemotor')
    read(att)
    sc.status(0)
    maw(shutter, 'open')
    read(shutter)
    shutter.read(0)
    scan('samplemotor', [1, 2, 3, 4, 5], LiveTime=1)
    scan(sc, [1, 2, 3, 4, 5, 10, 15], TrueTime=1)
    maw(shutter, 'closed')
