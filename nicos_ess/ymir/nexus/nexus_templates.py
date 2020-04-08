from nicos_ess.nexus import EventStream

ymir_default = {
    "entry-01:NXentry": {
        "instrument:NXinstrument": {
            "ExtSensor1:NXsample": {
                "TEST_sampleEnv": EventStream(
                    "UTGARD_choppers",
                    "LabS-Utgard-VIP:Rack-Chopper-PDU:ExtSensor1-RB",
                    "10.4.0.13:9092",
                    mod="f142",
                    dtype="double",
                ),
            }
        }
    }
}
