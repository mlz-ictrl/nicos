# pylint: skip-file

from time import sleep as tsleep
from nicos.core.status import ERROR


def init_box(compressor, *devices):
    if compressor.status(0)[0] == ERROR:
        compressor.reset()
    for dev in devices:
        dev.maw('off')


def check_pressure(comment, outdev, outvalue, indev, inrange):
    outdev.maw(outvalue)
    tsleep(1.5)
    val = indev.read(0)
    if inrange[0] <= val <= inrange[1]:
        print('%20s : %s' % (comment, 'OK'))
    else:
        printerror('%20s : %s' % (comment, 'FAILED : p = %.4f (%r)' %
                                  (val, inrange)))


def check_switch(comment, outdev, indev, value):
    outdev.move(value)
    tsleep(0.5)
    val = indev.read(0)
    if val == value:
        print('%20s : %s' % (comment, 'OK'))
    else:
        printerror('%20s : %s' % (comment, 'FAILED : value = %s' % (val, )))


def check_compressor_errors(comment, errdev, compressor, indev):
    if compressor.status(0)[0] == ERROR:
        compressor.reset()
    compressor.maw('on')
    tsleep(1.0)
    if indev.read() == 'on':
        errdev.move('on')
        tsleep(1.0)
        st = errdev.read()
        if st == 'on':
            if compressor.status(0)[0] == ERROR:
                print('%20s : OK' % (comment, ))
                compressor.reset()
            else:
                printerror('20%s : %s' % (comment, 'FAILED : compressor not in'
                                          ' ERROR state'))
            errdev.move('off')
        else:
            printerror('%20s : %s' % (comment, 'FAILED : compressor not '
                                      'switched on'))
    else:
        printwarning('%20s : %s' % (comment, 'SKIPPED'))

compressor = ccr21_compressor
gas_switch = ccr21_gas_switch
vacuum_switch = ccr21_vacuum_switch
p1 = ccr21_p1
p2 = ccr21_p2

rangesp1 = {0: [960, 970],
            1: [860, 870],
            2: [760, 770],
            5: [460, 470],
            10: [-40, 0],
            }

rangesp2 = {0: [-1, 0],
            1: [9e-4, 2e-3],
            2: [0.125, 0.127],
            5: [0.49, 0.51],
            10: [1.12, 1.13]
            }

init_box(compressor, (tb_err_compressor, tb_err_gastemp, tb_err_motortemp,
                      tb_err_power, tb_err_waterin, tb_err_waterout,
                      tb_err_gaspressure))

check_switch('Compressor on', compressor, tb_compressor, 'on')
check_switch('Compressor off', compressor, tb_compressor, 'off')
check_switch('Gas on', gas_switch, tb_gasvalve, 'on')
check_switch('Gas off', gas_switch, tb_gasvalve, 'off')
check_switch('Vacuum on', vacuum_switch, tb_vacuumvalve, 'on')
check_switch('Vacuum off', vacuum_switch, tb_vacuumvalve, 'off')

for v in sorted(rangesp1.keys()):
    check_pressure('P1 %2dV' % v, tb_v1, v, p1, rangesp1[v])

for v in sorted(rangesp2.keys()):
    check_pressure('P2 %2dV' % v, tb_v2, v, p2, rangesp2[v])

check_compressor_errors('Oil Error', tb_err_oil, compressor, tb_compressor)
check_compressor_errors('Gas Error', tb_err_gastemp, compressor, tb_compressor)
check_compressor_errors('Gas Pressure Error', tb_err_gaspressure, compressor,
                        tb_compressor)
check_compressor_errors('Motor Error', tb_err_motortemp, compressor,
                        tb_compressor)
check_compressor_errors('Power Error', tb_err_power, compressor, tb_compressor)
check_compressor_errors('Water inlet Error', tb_err_waterin, compressor,
                        tb_compressor)
check_compressor_errors('Water outlet Error', tb_err_waterout, compressor,
                        tb_compressor)
