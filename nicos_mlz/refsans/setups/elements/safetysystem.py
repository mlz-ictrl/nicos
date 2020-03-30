description = 'shs SicherHeitsSystem'

group = 'lowlevel'

instrument_values = configdata('instrument.values')

tango_base = instrument_values['tango_base']
code_base = instrument_values['code_base'] + 'safetysystem.'

# 'Shutter':                              (0, 0),  # 0x0000
# 'Ampeltest_inv':                        (3, 0),  # 0x0001
# 'Betreten_Verboten_inv':                (3, 1),  # 0x0002
# 'Hupentest_inv':                        (3, 2),  # 0x0004
# 'Schluesselschalter_Wartung_inv':       (3, 3),  # 0x0008
# 'Tuer_PO_auf':                          (3, 6),  # 0x0040
# 'Tuer_PO_zu':                           (3, 7),  # 0x0080
# 'Schnellschluss-Shutter_auf':           (3, 8),  # 0x0100
# 'Schnellschluss-Shutter_zu':            (3, 9),  # 0x0200
# '6-fach-Shutter_auf':                   (3, 10),  # 0x0400
# '6-fach-Shutter_zu':                    (3, 11),  # 0x0800
# 'Verbindung_zu_Warte_iO':               (3, 12),  # 0x1000
# 'Freigabe_von_Warte_fuer_ESShutter':    (3, 13),  # 0x2000
# 'Instrumentenverantwortlicher':         (3, 14),  # 0x4000
# 'Not-Aus_Kreis_inv':                    (3, 15),  # 0x8000
# 'Verbindungstuer':                      (4, 8),  # 0x0100
# 'Tuer_SR_auf':                          (4, 10),  # 0x0400
# 'Tuer_SR_zu':                           (4, 11),  # 0x0800
# 'externer_User_Kontakt_A':              (5, 0),  # 0x0001
# 'externer_User_Kontakt_B':              (5, 1),  # 0x0002
# 'PO-Aus-Schalter_1':                    (5, 2),  # 0x0004
# 'PO-Aus-Schalter_2':                    (5, 4),  # 0x0008
# 'Drucksensor_CB':                       (6, 0),  # 0x0001
# 'Drucksensor_SFK':                      (6, 1),  # 0x0002
# 'Drucksensor_Tube':                     (6, 2),  # 0x0004
# 'Chopper_Drehzahl':                     (6, 3),  # 0x0008
# 'Druck_service_inv':                    (6, 4),  # 0x0010
# 'Personenschluessel_Terminal':          (6, 11),  # 0x0800
# 'Freigabe_Taster':                      (6, 12),  # 0x1000
# 'Lampentest_inv':                       (6, 13),  # 0x2000
# 'Endschalter_Ex_Shutter_inv':           (6, 14),  # 0x4000
# 'Handbetrieb_tube_inv':                 (6, 15),  # 0x8000
# 'Probenort_Geraeumt_inv':               (14, 2),  # 0x0004
# 'Streurohr_Geraeumt_inv':               (14, 3),  # 0x0008
# 'IV_key_1':                             (15, 8),  # 0x0100
# 'IV_key_2':                             (15, 9),  # 0x0200
# 'gelb_inv':                             (17, 3),  # 0x0008
# 'Freigabe_EIN':                         (17, 10),  # 0x0400
# 'rot_inv':                              (18, 8),  # 0x0100
# 'Warnschilder':                         (18, 9),  # 0x0200
# 'Keine_Freigabe_Hub_Streurohr':         (18, 10),  # 0x0400
# 'Freigabe_Hub_Streurohr_inv':           (18, 10),  # 0x0400
# 'shutterzustand':                       (18, 11),  # 0x0800
# 'gruen_inv':                            (18, 12),  # 0x0800

devices = dict(
    safetysystem = device(code_base + 'Shs',
        description = 'io device for Pilz',
        tangodevice = tango_base + 'safetysystem/io/modbus',
        lowlevel = True,
    ),
    techOK = device(code_base + 'Group',
        description = ' ',
        shs = 'safetysystem',
        bitlist = ['Chopper_Drehzahl', 'Drucksensor_CB', 'Drucksensor_SFK',
                   'Drucksensor_Tube'],
        okmask = 0b1111,
        lowlevel = False,
    ),
    place = device(code_base + 'Group',
        description = ' ',
        shs = 'safetysystem',
        bitlist = ['Probenort_Geraeumt_inv', 'Streurohr_Geraeumt_inv'],
        okmask = 0b00,
        lowlevel = False,
    ),
    doors = device(code_base + 'Group',
        description = ' ',
        shs = 'safetysystem',
        bitlist = ['Tuer_PO_auf', 'Tuer_PO_zu', 'Verbindungstuer',
                   'Tuer_SR_auf', 'Tuer_SR_zu'],
        okmask = 0b01101,
        lowlevel = False,
    ),
    signal = device(code_base + 'Group',
        description = '',
        shs = 'safetysystem',
        bitlist = ['gruen_inv', 'gelb_inv', 'rot_inv'],
        okmask = 0b000,
        lowlevel = True,
    ),
    service = device(code_base + 'Group',
        description = ' ',
        shs = 'safetysystem',
        bitlist = ['Hupentest_inv', 'Schluesselschalter_Wartung_inv',
                   'Lampentest_inv', 'Handbetrieb_tube_inv',
                   'Druck_service_inv', 'Ampeltest_inv'],
        okmask = 0b000000,
        lowlevel = False,
    ),
    PO_save = device(code_base + 'Group',
        description = ' ',
        shs = 'safetysystem',
        bitlist = ['Probenort_Geraeumt_inv', 'Tuer_PO_auf', 'Tuer_PO_zu',
                   'Verbindungstuer'],
        okmask = 0b1010,
        lowlevel = False,
    ),
    SR_save = device(code_base + 'Group',
        description = ' ',
        shs = 'safetysystem',
        bitlist = ['Streurohr_Geraeumt_inv', 'Tuer_SR_auf', 'Tuer_SR_zu',
                   'Verbindungstuer'],
        okmask = 0b1010,
        lowlevel = False,
    ),
    supervisor = device(code_base + 'Group',
        description = ' ',
        shs = 'safetysystem',
        bitlist = ['6-fach-Shutter_auf', '6-fach-Shutter_zu',
                   'Schnellschluss-Shutter_auf', 'Schnellschluss-Shutter_zu',
                   'Verbindung_zu_Warte_iO', 'Freigabe_von_Warte_fuer_ESShutter'],
        okmask = 0b110101,
        lowlevel = False,
    ),
    user = device(code_base + 'Group',
        description = ' ',
        shs = 'safetysystem',
        bitlist = ['externer_User_Kontakt_A', 'externer_User_Kontakt_B'],
        okmask = 0b11,
        lowlevel = False,
    ),
)
