# pylint: skip-file

def check_pressure(comment, outdev, outvalue, indev, inrange):
    outdev.move(outvalue)
    sleep(1.5)
    print '%s: %s' % (comment, 'OK' if inrange[0] <= indev.read(0) <= inrange[1] else 'FAILED')
        

def check_switch(comment, outdev, indev, value):
    outdev.move(value)
    sleep(0.5)
    print '%s: %s' % (comment, 'OK' if indev.read(0) == value else 'FAILED')
 
 
check_switch('Compressor on', ccr21_compressor, tb_compressor, 'on')
check_switch('Compressor off', ccr21_compressor, tb_compressor, 'off')
check_switch('Gas on', ccr21_gas_switch, tb_gasvalve, 'on')
check_switch('Gas off', ccr21_gas_switch, tb_gasvalve, 'off')
check_switch('Vacuum on', ccr21_vacuum_switch, tb_vacuumvalve, 'on')
check_switch('Vacuum off', ccr21_vacuum_switch, tb_vacuumvalve, 'off')
        
check_pressure('P1 0V', tb_v1, 0, ccr21_p1, [960, 970])
check_pressure('P1 1V', tb_v1, 1, ccr21_p1, [860, 865])
check_pressure('P1 2V', tb_v1, 2, ccr21_p1, [760, 765])
check_pressure('P1 5V', tb_v1, 5, ccr21_p1, [460, 465])
check_pressure('P1 10V', tb_v1, 10, ccr21_p1, [-40, 0])

check_pressure('P2 0V', tb_v2, 0, ccr21_p2, [-1, 0])
check_pressure('P2 1V', tb_v2, 1, ccr21_p2, [9e-4, 1e-3])
check_pressure('P2 2V', tb_v2, 2, ccr21_p2, [0.125, 0.126])
check_pressure('P2 5V', tb_v2, 5, ccr21_p2, [0.49, 0.51])
check_pressure('P2 10V', tb_v2, 10, ccr21_p2, [1.12, 1.13])

# Switch compressor on
ccr21_compressor.move('on')
sleep(0.5)
if tb_compressor.read() == 'on':
    tb_err_oil.move('on')
    sleep(5)
    st = tb_err_oil.read()
    if st == 'on':
        print 'Oil ERRROR : OK'
        # read status
        tb_err_oil.move('off')
    else:
        print 'Oil ERROR : FAILED'
else:
    print 'Oil ERROR : SKIPPED'
    
