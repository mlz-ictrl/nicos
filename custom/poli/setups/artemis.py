description = 'Pseudo detector for neutron camera'

group = 'optional'

devices = dict(
    camera    = device('poli.artemis.ArtemisCapture',
                       description = 'Pseudo detector for camera',
                       datapath = '/home/jcns/camera',
                      ),
)
