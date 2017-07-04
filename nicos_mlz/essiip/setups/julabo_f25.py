description = 'Julabo F25 at Utgard Lab.'

devices = dict(
    T1=device('nicos_mlz.essiip.devices.epics_julabo_controller.EpicsJulaboController',
              description='Julabo F25',
              readpv='Ulab:TEMP',
              writepv='Ulab:TEMP:SP1',
              targetpv='Ulab:TEMP:SP1:RBV',
              statuscodepv='Ulab:STATUS',
              statusmsgpv='Ulab:STATUSc',
              switchpvs={'read': 'Ulab:MODE', 'write': 'Ulab:MODE:SP'},
              switchstates={'on': 1, 'off': 0},
              epicstimeout=3.0,
              precision=0.1,
              timeout=None,
              window=30.0,
              ),
)
