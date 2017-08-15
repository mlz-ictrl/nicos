description = 'Device to be tested in the SINQ_AMOR.'


def create_epics_motor(controller_id, device_id):
    '''
    Creates a motor with controller id (a/b/c) and
    name of the motor device. The motor pv will be used as follows:
    SQ:AMOR:mot<controller_id>:device_id
    '''
    return device('nicos_ess.essiip.devices.epics_motor.EpicsMotor',
                  epicstimeout=3.0,
                  description='Test motor',
                  motorpv='SQ:AMOR:mot' + controller_id + ':' + device_id,
                  )


def create_epics_magnet(device_id):
    '''
    Creates a magnet with the given device id
    '''
    return device('nicos_sinq.amor.devices.epics_amor_magnet.EpicsAmorMagnet',
                  epicstimeout=3.0,
                  description='Test magnet',
                  basepv='SQ:AMOR:' + device_id,
                  pvdelim=':',
                  switchpvs={
                      'read': 'SQ:AMOR:' + device_id + ':PowerStatusRBV',
                      'write': 'SQ:AMOR:' + device_id + ':PowerStatus'},
                  switchstates={'on': 1, 'off': 0},
                  precision=0.1,
                  timeout=None,
                  window=5.0,
                  )


def create_epics_asyn_controller(device_id):
    """
    Creates an asyn controller with the given device id
    """
    return device(
        'nicos_sinq.amor.devices.epics_extensions.EpicsAsynController',
        epicstimeout=3.0,
        description='Asyn controller for motors in serial1',
        commandpv='SQ:AMOR:' + device_id + '.AOUT',
        replypv='SQ:AMOR:' + device_id + '.AINP',
    )


devices = dict(
    com=create_epics_motor('a', 'com'),
    coz=create_epics_motor('a', 'coz'),
    c3z=create_epics_motor('a', 'c3z'),
    cox=create_epics_motor('a', 'cox'),
    eoz=create_epics_motor('a', 'eoz'),
    xlz=create_epics_motor('a', 'xlz'),
    eom=create_epics_motor('a', 'eom'),
    som=create_epics_motor('a', 'som'),
    soz=create_epics_motor('a', 'soz'),
    stz=create_epics_motor('a', 'stz'),
    sch=create_epics_motor('a', 'sch'),
    aom=create_epics_motor('b', 'aom'),
    aoz=create_epics_motor('b', 'aoz'),
    atz=create_epics_motor('b', 'atz'),
    mom=create_epics_motor('b', 'mom'),
    moz=create_epics_motor('b', 'moz'),
    mtz=create_epics_motor('b', 'mtz'),
    mty=create_epics_motor('b', 'mty'),
    fom=create_epics_motor('b', 'fom'),
    ftz=create_epics_motor('b', 'ftz'),
    d5v=create_epics_motor('c', 'd5v'),
    d5h=create_epics_motor('c', 'd5h'),
    d1l=create_epics_motor('c', 'd1l'),
    d1r=create_epics_motor('c', 'd1r'),
    d3t=create_epics_motor('c', 'd3t'),
    d3b=create_epics_motor('c', 'd3b'),
    d4t=create_epics_motor('c', 'd4t'),
    d4b=create_epics_motor('c', 'd4b'),
    d1t=create_epics_motor('c', 'd1t'),
    d1b=create_epics_motor('c', 'd1b'),
    d2t=create_epics_motor('c', 'd2t'),
    d2b=create_epics_motor('c', 'd2b'),
    serial1=create_epics_asyn_controller('serial1'),
    serial2=create_epics_asyn_controller('serial2'),
    serial3=create_epics_asyn_controller('serial3'),
    pby=create_epics_magnet('PBY'),
)
