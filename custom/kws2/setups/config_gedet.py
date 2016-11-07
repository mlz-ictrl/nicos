description = 'GE detector setup PV values'
group = 'configdata'

# KWS2TODO: check if these are the latest

EIGHT_PACKS = [
    # ("ep01", "GE-DD590C-EP"), # replaced 2015/10/29
    ("ep01", "GE-DD6D8C-EP"),
    ("ep02", "GE-DD5FB3-EP"),
    ("ep03", "GE-DDA871-EP"),
    ("ep04", "GE-DD7D29-EP"),
    ("ep05", "GE-DDBA8F-EP"),
    ("ep06", "GE-DD5913-EP"),
    ("ep07", "GE-DDC7CA-EP"),
    ("ep08", "GE-DD6DEF-EP"),
    ("ep09", "GE-DD5FB6-EP"),
    ("ep10", "GE-DDBA88-EP"),
    # ("ep11", "GE-DD6AE9-EP"),
    # ("ep11", "GE-DD6D79-EP"), # was spare
    ("ep11", "GE-DD9522-EP"),  # changed 2015/09/23
    ("ep12", "GE-DD6D89-EP"),
    ("ep13", "GE-DD6D96-EP"),
    ("ep14", "GE-DD6974-EP"),
    ("ep15", "GE-DD5FA9-EP"),
    ("ep16", "GE-DDA874-EP"),
    ("ep17", "GE-DD6975-EP"),
    ("ep18", "GE-DD5916-EP"),
]

HV_VALUES = {n[0]: 1530 for n in EIGHT_PACKS}

PV_SCALES = {
    "ep01": [("AScales", [2167, 2015, 2094, 2088, 2085, 2101, 2117, 2075])],
    "ep02": [("AScales", [2081, 2113, 2075, 2071, 2065, 2098, 2056, 2086])],
    "ep03": [("AScales", [2042, 2036, 2075, 2081, 2112, 2010, 2003, 2045])],
    "ep04": [("AScales", [2036, 1998, 2021, 2031, 2026, 2031, 2044, 2048])],
    "ep05": [("AScales", [1991, 2033, 1996, 2041, 2021, 1995, 2034, 2051])],
    "ep06": [("AScales", [2002, 2024, 2064, 2037, 2029, 2032, 2056, 2020])],
    "ep07": [("AScales", [2022, 2028, 1989, 1992, 2009, 2005, 1974, 2012])],
    "ep08": [("AScales", [2027, 2041, 2006, 2008, 2028, 2025, 2015, 2077])],
    "ep09": [("AScales", [1988, 2024, 1977, 2041, 2008, 1998, 1991, 1978])],
    "ep10": [("AScales", [2034, 2019, 2029, 2064, 2040, 2008, 2028, 2024])],
    "ep11": [("AScales", [1995, 1996, 2008, 1967, 1991, 1980, 2015, 2008])],
    "ep12": [("AScales", [1993, 2018, 1977, 1996, 1992, 1985, 1994, 1995])],
    "ep13": [("AScales", [2028, 2046, 2048, 2040, 2033, 2025, 1986, 2043])],
    "ep15": [("AScales", [2045, 2040, 2026, 1989, 2042, 2011, 2047, 2040])],
    "ep14": [("AScales", [2058, 2037, 2036, 2046, 2001, 2040, 2059, 2049])],
    "ep16": [("AScales", [2099, 2043, 1979, 2060, 2095, 2055, 2082, 2102])],
    "ep17": [("AScales", [2089, 2120, 2101, 2089, 2108, 2097, 2111, 2109])],
    "ep18": [("AScales", [2091, 2057, 2067, 1984, 2038, 2081, 2071, 2095])]
}

# event modes
MODE = 0x03
MODE_DIAG = 0x06
MODE_FAKE = 0x23
MODE_FAKEDIAG = 0x26

PV_VALUES_COMMON = [
    ("Mode", MODE),
    ("DecimationFactor", 1),
    ("DiscriminatorLevel", 1024),
    ("NegativeVeto", -16384),
    ("PositiveVeto", 16383),
    ("Sample1", 10),
    ("BScales", [2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048]),
    ("Scales", [2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048]),
    ("TubeEnables", [1, 1, 1, 1, 1, 1, 1, 1]),
    ("AccumulationLength", 60),
    ("WaveformCaptureLength", 1015),
]

# pixel per tube
PPT_S = 94
PPT_M = 206
PPT_L = 256

PV_VALUES_SINGLE = {
    "ep01": [("ModulePixelIdStart", 0), ("PixelCount", PPT_S)],
    "ep02": [("ModulePixelIdStart", 8192), ("PixelCount", PPT_S)],
    "ep03": [("ModulePixelIdStart", 2*8192), ("PixelCount", PPT_S)],
    "ep04": [("ModulePixelIdStart", 3*8192), ("PixelCount", PPT_M)],
    "ep05": [("ModulePixelIdStart", 4*8192), ("PixelCount", PPT_M)],
    "ep06": [("ModulePixelIdStart", 5*8192), ("PixelCount", PPT_M)],
    "ep07": [("ModulePixelIdStart", 6*8192), ("PixelCount", PPT_L)],
    "ep08": [("ModulePixelIdStart", 7*8192), ("PixelCount", PPT_L)],
    "ep09": [("ModulePixelIdStart", 8*8192), ("PixelCount", PPT_L)],
    "ep10": [("ModulePixelIdStart", 9*8192), ("PixelCount", PPT_L)],
    "ep11": [("ModulePixelIdStart", 10*8192), ("PixelCount", PPT_L)],
    "ep12": [("ModulePixelIdStart", 11*8192), ("PixelCount", PPT_L)],
    "ep13": [("ModulePixelIdStart", 12*8192), ("PixelCount", PPT_M)],
    "ep14": [("ModulePixelIdStart", 14*8192), ("PixelCount", PPT_M)],
    "ep15": [("ModulePixelIdStart", 13*8192), ("PixelCount", PPT_M)],
    "ep16": [("ModulePixelIdStart", 15*8192), ("PixelCount", PPT_S)],
    "ep17": [("ModulePixelIdStart", 16*8192), ("PixelCount", PPT_S)],
    "ep18": [("ModulePixelIdStart", 17*8192), ("PixelCount", PPT_S)]
}
