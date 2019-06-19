description = 'SES-PREMP Motors'
pvprefix = 'SES-PREMP:MC-MCU-03:'

devices = dict(
    mcu01_m1 = device('nicos_ess.devices.epics.motor.EpicsMotor',
                      description = 'Motor 1',
                      lowlevel = False,
                      unit = 'mm',
                      fmtstr = '%.2f',
                      abslimits = (-20, 20),
                      epicstimeout = 3.0,
                      precision = 0.1,
                      motorpv = pvprefix + 'm1',
                      errormsgpv = pvprefix + 'm1-MsgTxt',
                      errorbitpv = pvprefix + 'm1-Err',
                      reseterrorpv = pvprefix + 'm1-ErrRst'
               ),

    mcu01_m2 = device('nicos_ess.devices.epics.motor.EpicsMotor',
                      description = 'Motor 2',
                      lowlevel = False,
                      unit = 'mm',
                      fmtstr = '%.2f',
                      abslimits = (-15, 15),
                      epicstimeout = 3.0,
                      precision = 0.1,
                      motorpv = pvprefix + 'm2',
                      errormsgpv = pvprefix + 'm2-MsgTxt',
                      errorbitpv = pvprefix + 'm2-Err',
                      reseterrorpv = pvprefix + 'm2-ErrRst'
               ),

)


