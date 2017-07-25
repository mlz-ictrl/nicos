description = "Outside world data"
group = "lowlevel"

devices = dict(
    meteo = device("nicos_mlz.jcns.devices.meteo.MeteoStation",
                   description = "Outdoor air temperature",
                   query = "temperature/air",
                   location = "Garching",
                   unit = 'C',
                  ),
)
