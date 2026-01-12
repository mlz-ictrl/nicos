description = 'SECoP devices'
group = 'configdata'
secop_devices = {
    "demo": {

    },
    "heatswitch": {
        "description": "Heatswitch for `mf` device",
        "target": "off",

    },
    "label": {
        "description": "some label indicating the state of the magnet `mf`.",

    },
    "mf": {
        "description": "simulates some cryomagnet with persistent/non-persistent switching",
        "limits": (-15.0, 15.0),
        "unit": "T",
                "target": 1.55,

    },
    "tc1": {
        "description": "some temperature",

    },
    "tc2": {
        "description": "some temperature",

    },
    "ts": {
        "description": "some temperature",
        "unit": "K",
                "target": 14.0,

    },
}
