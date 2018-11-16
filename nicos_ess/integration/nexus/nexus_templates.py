from __future__ import absolute_import, division, print_function

from nicos_ess.nexus import EventStream

integration_default = {
    "entry-01:NXentry": {
        "instrument:NXinstrument": {
            "events": EventStream(
                "C-SPEC_detector", "c_spec_data", "192.168.12.109:9092"
            ),
            "testCounter": EventStream(
                "testCounter",
                "testCounter",
                "192.168.12.109:9092",
                mod="f142",
                dtype="int32",
            ),
        }
    }
}
