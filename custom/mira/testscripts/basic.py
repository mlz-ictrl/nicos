# pylint: skip-file

from nicos import session

loaded_setups = session.loaded_setups

# read basic devices

basic_devices = [atten1, atten2, lamfilter, flip2, ms2pos, Shutter, PSDGas,
                 Cooling, CoolTemp,
                 ss1, ss2, ms2,
                 m2th, m2tt, m2tx, m2ty, m2gx,
                 phi, om, stx, sty, stz, sgx, sgy,
                 NL6, ReactorPower]

for dev in basic_devices:
    dev.status(0)

for dev in basic_devices:
    read(dev)

if 'cascade' in loaded_setups:
    for dev in [psd, PSDHV]:
        dev.status(0)
    read(PSDHV)
    SetDetectors(psd)
    read(psd)

if 'diff' in loaded_setups:
    print(Sample.samplename)
    for dev in [mira, vana, vath, vatt, ki, Ei, lam]:
        dev.status(0)
    for dev in [mira, vana, vath, vatt, ki, Ei, lam]:
        read(dev)

if 'tas' in loaded_setups:
    print(Sample.samplename)
    for dev in [mira, ki, kf, Ei, Ef]:
        dev.status(0)
    for dev in [mira, ki, kf, Ei, Ef]:
        read(dev)

# basic operations

SetDetectors(det)
cscan(om, 0, 0.1, 2, 1)
cscan(phi, 0, 0.2, 2, 1)

for i in [0, 1, 0]:
    maw(stx, i)
for i in [0, 1, 0]:
    maw(sgy, i)
