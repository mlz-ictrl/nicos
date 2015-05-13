description = 'Keithley 6221 current source, for susceptometer measurements'
group = 'optional'

includes = []

devices = dict(
    keithley_ampl = device('antares.keithley6221.Current',
                           description = 'Keithley amplitude',
                           tacodevice = 'antares/network/keithley',
                           abslimits = (0, 0.01),
                           unit = 'A',
                          ),
    keithley_freq = device('antares.keithley6221.Frequency',
                           description = 'Keithley frequency',
                           tacodevice = 'antares/network/keithley',
                           abslimits = (1e-3, 1e5),
                           unit = 'Hz',
                          ),
)

startupcode = '''
'''
