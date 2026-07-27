description = 'He3 spectrometers'

group = 'optional'

tango_base = 'tango://localhost:10000/he3/'

devices = dict(
    hr4000 = device(
        'nicos_jcns.seop.devices.spectrometer.HR4000',
        description = 'OceanOptics spectrometer',
        tangodevice = tango_base + 'spectrometers/ocean_hr4000',
    ),
    av4096 = device(
        'nicos_jcns.seop.devices.spectrometer.AV4096',
        description = 'Avantes spectrometer',
        tangodevice = tango_base + 'spectrometers/avaspec_4096',
    ),
)
