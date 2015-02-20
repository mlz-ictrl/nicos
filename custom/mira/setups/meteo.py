description = 'The outside temperature on the campus'
group = 'lowlevel'

devices = dict(
    OutsideTemp = device('mira.meteo.Temp',
                         description = 'temperature at TUM meteo station tower',
                        ),
)
