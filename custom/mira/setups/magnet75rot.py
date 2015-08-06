TACOBASE = '//magnet/magnet/'

description = 'Phytron device for 7.5 T magnet rotation'

includes = ['alias_sth']

devices = dict(
    # Nicos based access to phytron in magnet rack
    magnetmotorbus=device('panda.mcc2.TacoSerial',
                          lowlevel = True,
                          tacodevice = TACOBASE + 'rs232/phytron',        # new value as of 2012-07-30 EF
                         ),
    sth_B7T5_step = device('panda.mcc2.MCC2Motor',
                           description = '7.5T magnet sample rotation MOTOR using only the RS232 TACOSERVER and talking to mcc2',
                           bus = 'magnetmotorbus',
                           precision = 0.01,
                           fmtstr = '%.3f',
                    #~     tacodevice = TACOBASE + 'rs232/newport',     # old value
                    #      tacodevice = TACOBASE + 'rs232/phytron',        # new value as of 2012-07-30 EF
                           channel = 'Y',
                           addr = 0,
                    #~     slope = -480000.0 / (360.0 * 6),
                           slope = -75000.0 / (360.0),
                           abslimits = (-360, 360),
                           userlimits = (0, 120),
                           unit = 'deg',
                           idlecurrent = 0.4,
                           movecurrent = 1.0,
                           rampcurrent = 1.2,
                           microstep = 8,
                           speed = 2.0,
                          ),
    sth_B7T5_coder = device('panda.mcc2.MCC2Coder',
                            description = '7.5T magnet sample rotation CODER using only the RS232 TACOSERVER and talking to mcc2',
                            bus = 'magnetmotorbus',
                            fmtstr = '%.3f',
                    #       tacodevice = TACOBASE + 'rs232/phytron',        # new value as of 2012-07-30 EF
                            channel = 'Y',
                            addr = 0,
                            slope = -480000.0 / 360.0,
                            unit = 'deg',
                            zerosteps = 0,
                            codertype = 'incremental',
                            coderbits = 25,
                           ),
    sth_B7T5 = device('devices.generic.Axis',
                      description = 'sample rotation inside magnet',
                      motor = 'sth_B7T5_step',
                      coder = 'sth_B7T5_coder',
                      obs = [],
                      precision = 0.01,
                      backlash = -1,
                     ),
)
alias_config = [
    ('sth', 'sth_B7T5', 200),
]

