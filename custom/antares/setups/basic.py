description = 'Fundamental Functions of ANTARES'

group = 'lowlevel'

devices = dict(
# Here we intend to put fundamental devices always needed for ANTARES
# These will be Shutters, Collimators, Pilz State inputs, ...
    shf = device('devices.taco.io.DigitalOutput', # Fast Shutter
                  description = 'Fast Shutter of Antares',
                  tacodevice = 'antares/i7000/fastshut',
                ),
)