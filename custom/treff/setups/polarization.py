# -*- coding: utf-8 -*-

description = "Field setup"
group = "optional"

includes = ["polarizer", "pow2cc"]

devices = dict(
    pol_state = device("nicos.devices.generic.MultiSwitcher",
        description = "Guide field switcher",
        moveables = ["pflipper", "aflipper"],
        mapping = {
            "dd": ("down", "down"),
            "du": ("down", "up"),
            "ud": ("up", "down"),
            "uu": ("up", "up"),
        },
        precision = None,
        unit = ''
    ),
)
