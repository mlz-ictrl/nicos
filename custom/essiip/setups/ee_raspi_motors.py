description = 'Setup with two motors (IcePAP simulator).'

devices = dict(

    # Maybe it would make sense to define motor differently, for example with
    # a pv_prefix (everything after the . is part of the motor record and thus standard).
    # That would further reduce the code at this point.
    motor1=device('essiip.epics_motor.EpicsMotor',
                  epicstimeout=3.0,
                  description='Motor 1 of IcePAP simulator',
                  motorpv='IOC:m1',
                  ),

    motor2=device('essiip.epics_motor.EpicsMotor',
                  epicstimeout=3.0,
                  description='Motor 2 of IcePAP simulator',
                  motorpv='IOC:m2',
                  ),
)
