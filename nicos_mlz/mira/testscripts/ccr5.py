# pylint: skip-file

from nicos import session

loaded_setups = session.loaded_setups

AddSetup('ccr5')
if 'ccr5' in loaded_setups:
    T_ccr5.read(0)
    T_ccr5_A.read(0)
    T_ccr5_B.read(0)
    T_ccr5_C.read(0)
    ccr5_p1.read(0)
    ccr5_compressor_switch.read(0)
    ccr5_gas_switch.read(0)
    ccr5_vacuum_switch.read(0)
