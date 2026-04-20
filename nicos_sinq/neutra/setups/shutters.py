description = 'Devices for the shutter at SANS-LLB'

group = 'lowlevel'

neutraprefix = 'SQ:NEUTRA:'

devices = dict(
    n_shutter = device('nicos_sinq.devices.epics.shutter.Shutter',
        description = 'Experiment shutter',
        pvprefix = neutraprefix + "SPS-N-SHUTTER",
        #cbs_in_daemon = True
    ),
    xray_shutter = device('nicos_sinq.devices.epics.shutter.Shutter',
        description = 'X-ray shutter',
        pvprefix = neutraprefix + "SPS-X-RAY-SHUTTER",
        #cbs_in_daemon = True
    ),
)
