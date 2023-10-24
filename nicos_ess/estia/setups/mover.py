description = 'Selene1 mover motors'

pvprefix = 'PSI-ESTIARND:MC-MCU-01:'

devices = dict(
    mover_fl_re_us=device(
        'nicos_ess.devices.epics.pva.motor.EpicsMotor',
        description='M1 Selene1 1-Mover FL-RE-US',
        motorpv=f'{pvprefix}m1',
        has_powerauto=False,
        pollinterval=None,
        monitor=True,
        pva=True,

    ),
    mover_pr_re_ds=device(
        'nicos_ess.devices.epics.pva.motor.EpicsMotor',
        description='M2 Selene1 1-Mover PR-RE-DS',
        motorpv=f'{pvprefix}m2',
        has_powerauto=False,
        pollinterval=None,
        monitor=True,
        pva=True,
    ),
    mover_pr_li_ds=device(
        'nicos_ess.devices.epics.pva.motor.EpicsMotor',
        description='M3 Selene1 1-Mover PR-LI-DS',
        motorpv=f'{pvprefix}m3',
        has_powerauto=False,
        pollinterval=None,
        monitor=True,
        pva=True,
    ),
    mover_pr_li_us1=device(
        'nicos_ess.devices.epics.pva.motor.EpicsMotor',
        description='M4 Selene1 2-Mover PR-LI-US-1',
        motorpv=f'{pvprefix}m4',
        has_powerauto=False,
        pollinterval=None,
        monitor=True,
        pva=True,
    ),
    mover_pr_li_us2=device(
        'nicos_ess.devices.epics.pva.motor.EpicsMotor',
        description='M5 Selene1 2-Mover PR-LI-US-2',
        motorpv=f'{pvprefix}m5',
        has_powerauto=False,
        pollinterval=None,
        monitor=True,
        pva=True,
    ),
)
