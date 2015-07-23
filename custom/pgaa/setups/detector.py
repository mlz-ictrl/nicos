description = 'PGAA detectors'

group = 'lowlevel'

includes = []

nethost = 'pgaasrv.pgaa.frm2'

devices = dict(
    get_ready = device('devices.taco.io.DigitalInput',
                       description = '',
                       tacodevice = '//%s/pgaa/pgaa/get_ready' % (nethost,),
                       lowlevel = True,
                      ),
    set_ready = device('devices.taco.io.DigitalOutput',
                       description = '',
                       tacodevice = '//%s/pgaa/pgaa/sample_ready' % (nethost,),
                       lowlevel = True,
                      ),
    det = device('pgaa.dspec.DSPec',
                 description = 'DSpec detector device',
                 set_ready = 'set_ready',
                 get_ready = 'get_ready',
                ),
)
