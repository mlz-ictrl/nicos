from nicos_ess.nexus import EventStream

dream_default = {
    "entry-01:NXentry": {
        "instrument:NXinstrument": {
            "ExtSensor1:NXsample": {
                "TEST_sampleEnv": EventStream(
                    "Motor_Topic",
                    "IOC:m2.RBV",
                    "localhost:9092",
                    mod="f142",
                    dtype="double",
                ),
            },
            "detector:NXdetector": {
                "data:NXevent_data": {
                    "data": EventStream('fake_events','just-bin-it',
                                        'localhost:9092', dtype='uint32'),
                },
            },
        }
    }
}
