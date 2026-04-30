description = 'OceanOptics HR4000 spectrometer'

group = 'optional'

tango_base = 'tango://localhost:10000/he3/'

devices = dict(
    hr4000 = device(
        'nicos_jcns.seop.devices.oceanspectrometer.OceanSpectrum',
        description = 'OceanOptics spectrometer',
        tangodevice = tango_base + 'ocean_hr4000/spectrum',
    )
)
