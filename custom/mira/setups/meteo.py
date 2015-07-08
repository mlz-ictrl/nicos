description = 'The outside temperature on the campus'
group = 'lowlevel'

devices = dict(
    OutsideTemp = device('jcns.meteo.MeteoStation',
                   description = 'Outdoor air temperature',
                   query = 'temperature/air',
                   location = 'Garching',
                   unit = 'degC',
                  ),
)
