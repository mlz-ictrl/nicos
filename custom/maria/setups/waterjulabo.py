description = "Water-Julabo F12-MA temperature controller"

group = "optional"

includes = ["alias_T"]

tango_base = "tango://phys.maria.frm2:10000/maria"

devices = dict(
    T_julabo = device("devices.tango.TemperatureController",
                       description = "The regulated temperature",
                       tangodevice = tango_base + "/waterjulabo/control",
                       abslimits = (5, 80),
                       unit = "degC",
                       fmtstr = "%.2f",
                       precision = 0.1,
                       timeout = 45*60.,
                      ),
)

alias_config = {
    "T":  {"T_julabo": 100},
    "Ts": {"T_julabo": 100},
}
