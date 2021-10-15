from nicos_ess.nexus import DeviceDataset, EventStream

ymir_default = {
    "NeXus_Version": "4.3.0",
    "instrument": "YMIR",
    "entry1:NXentry": {
        "comment": DeviceDataset('Exp', 'remark'),
        "title": DeviceDataset('Exp', 'title'),
        "experiment_identifier": DeviceDataset('Exp', 'proposal'),
        "user:NXuser": {
            "name": DeviceDataset('Exp', 'users'),
        },
        "motion:NXentry": {
            "motor": EventStream("Ymir_motion", "SES-SCAN:MC-MCU-001:m1.RBV",
                                 mod="f142", dtype="double",),
        }
    }
}
