description = 'GE detector setup PV values'
group = 'configdata'

EIGHT_PACKS = [
    # ('ep01', 'GE-DD590C-EP'), # replaced 2015/10/29
    ('ep01', 'GE-DD6D8C-EP'),
    ('ep02', 'GE-DD5FB3-EP'),
    ('ep03', 'GE-DDA871-EP'),
    ('ep04', 'GE-DD7D29-EP'),
    ('ep05', 'GE-DDBA8F-EP'),
    ('ep06', 'GE-DD5913-EP'),
    ('ep07', 'GE-DDC7CA-EP'),
    ('ep08', 'GE-DD6DEF-EP'),
    ('ep09', 'GE-DD5FB6-EP'),
    ('ep10', 'GE-DDBA88-EP'),
    # ('ep11', 'GE-DD6AE9-EP'),
    # ('ep11', 'GE-DD6D79-EP'), # was spare
    ('ep11', 'GE-DD9522-EP'),  # changed 2015/09/23
    ('ep12', 'GE-DD6D89-EP'),
    ('ep13', 'GE-DD6D96-EP'),
    ('ep14', 'GE-DD6974-EP'),
    ('ep15', 'GE-DD5FA9-EP'),
    ('ep16', 'GE-DDA874-EP'),
    ('ep17', 'GE-DD6975-EP'),
    ('ep18', 'GE-DD5916-EP'),
]

HV_VALUES = {n[0]: 1530 for n in EIGHT_PACKS}
# -- To set different HVs for some 8-packs:
# HV_VALUES['ep01'] = 0
# HV_VALUES['ep18'] = 0

PV_SCALES = {
    'ep01': [('AScales', [2077, 2033, 2127, 2137, 2095, 2130, 2149, 2123]), ('Scales', [2102, 2114, 2118, 2088, 2088, 2076, 2107, 2124])],
    'ep02': [('AScales', [2089, 2148, 2095, 2090, 2088, 2147, 2107, 2098]), ('Scales', [2069, 2099, 2061, 2100, 2104, 2090, 2101, 2087])],
    'ep03': [('AScales', [2105, 2084, 2112, 2107, 2183, 2050, 2084, 2102]), ('Scales', [2093, 2125, 2086, 2112, 2101, 2097, 2102, 2111])],
    'ep04': [('AScales', [2060, 2036, 2055, 2063, 2060, 2071, 2067, 2083]), ('Scales', [2006, 1991, 1996, 2003, 2011, 2002, 1996, 1999])],
    'ep05': [('AScales', [2016, 2064, 2037, 2083, 2062, 2023, 2078, 2083]), ('Scales', [2009, 1997, 1973, 2020, 1989, 2038, 2010, 2010])],
    'ep06': [('AScales', [2026, 2048, 2087, 2059, 2040, 2050, 2073, 2037]), ('Scales', [2007, 2005, 2011, 2009, 2010, 1990, 2002, 2010])],
    'ep07': [('AScales', [2041, 2037, 1999, 1996, 2031, 2013, 1982, 2063]), ('Scales', [1982, 2021, 1993, 1984, 1987, 1961, 1986, 1964])],
    'ep08': [('AScales', [2055, 2074, 2039, 2032, 2068, 2070, 2054, 2100]), ('Scales', [2010, 1999, 1987, 2009, 1986, 2005, 1984, 2005])],
    'ep09': [('AScales', [2031, 2065, 2005, 2088, 2048, 2048, 2035, 2009]), ('Scales', [2001, 1999, 1984, 2018, 1979, 1992, 1986, 1977])],
    'ep10': [('AScales', [2050, 2022, 2040, 2082, 2059, 2030, 2033, 2055]), ('Scales', [1978, 2030, 1978, 1980, 1997, 2016, 1982, 1991])],
    'ep11': [('AScales', [2035, 2024, 2042, 2014, 2024, 2005, 2063, 2037]), ('Scales', [1996, 2018, 1996, 1975, 1966, 1963, 2035, 2016])],
    'ep12': [('AScales', [2063, 2079, 2042, 2049, 2053, 2055, 2050, 2063]), ('Scales', [1990, 2020, 2003, 2002, 1978, 1988, 2015, 1975])],
    'ep13': [('AScales', [2072, 2095, 2092, 2104, 2083, 2077, 2036, 2092]), ('Scales', [2018, 2013, 2004, 2013, 2007, 2002, 2027, 2004])],
    'ep15': [('AScales', [2078, 2060, 2063, 2091, 2050, 2053, 2071, 2061]), ('Scales', [2014, 2000, 2017, 1998, 1989, 1996, 2002, 2030])],
    'ep14': [('AScales', [2070, 2078, 2055, 2026, 2075, 2053, 2072, 2073]), ('Scales', [2011, 2002, 2009, 1990, 1998, 1963, 2015, 1986])],
    'ep16': [('AScales', [2196, 2085, 2053, 2161, 2168, 2127, 2155, 2185]), ('Scales', [2087, 2079, 2090, 2113, 2100, 2085, 2082, 2086])],
    'ep17': [('AScales', [2144, 2188, 2168, 2153, 2192, 2148, 2178, 2205]), ('Scales', [2105, 2070, 2098, 2109, 2111, 2099, 2103, 2090])],
    'ep18': [('AScales', [2178, 2134, 2149, 2053, 2142, 2191, 2154, 2115]), ('Scales', [2125, 2118, 2110, 2154, 2113, 2132, 2102, 2099])],
}

# -- For recalibration, set everything to defaults:
# PV_SCALES = {
#     'ep%02d' % i: [('AScales', [2048]*8), ('Scales', [2048]*8)] for i in range(1, 19)
# }

# event modes
MODE = 0x03
MODE_DIAG = 0x06
MODE_FAKE = 0x23
MODE_FAKEDIAG = 0x26

PV_VALUES_COMMON = [
    ('Mode', MODE),
    ('DecimationFactor', 1),
    ('DiscriminatorLevel', 1024),
    ('NegativeVeto', -16384),
    ('PositiveVeto', 16383),
    ('Sample1', 10),
    ('BScales', [2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048]),
    ('TubeEnables', [1, 1, 1, 1, 1, 1, 1, 1]),
    ('AccumulationLength', 60),
    ('WaveformCaptureLength', 1015),
]

# pixel per tube
PPT_S = 94
PPT_M = 206
PPT_L = 256

# -- For recalibration, set to max. pixel resolution:
# PPT_S = 1024
# PPT_M = 1024
# PPT_L = 1024

PV_VALUES_SINGLE = {
    'ep01': [('ModulePixelIdStart', 0*8192),  ('PixelCount', PPT_S)],
    'ep02': [('ModulePixelIdStart', 1*8192),  ('PixelCount', PPT_S)],
    'ep03': [('ModulePixelIdStart', 2*8192),  ('PixelCount', PPT_S)],
    'ep04': [('ModulePixelIdStart', 3*8192),  ('PixelCount', PPT_M)],
    'ep05': [('ModulePixelIdStart', 4*8192),  ('PixelCount', PPT_M)],
    'ep06': [('ModulePixelIdStart', 5*8192),  ('PixelCount', PPT_M)],
    'ep07': [('ModulePixelIdStart', 6*8192),  ('PixelCount', PPT_L)],
    'ep08': [('ModulePixelIdStart', 7*8192),  ('PixelCount', PPT_L)],
    'ep09': [('ModulePixelIdStart', 8*8192),  ('PixelCount', PPT_L)],
    'ep10': [('ModulePixelIdStart', 9*8192),  ('PixelCount', PPT_L)],
    'ep11': [('ModulePixelIdStart', 10*8192), ('PixelCount', PPT_L)],
    'ep12': [('ModulePixelIdStart', 11*8192), ('PixelCount', PPT_L)],
    'ep13': [('ModulePixelIdStart', 12*8192), ('PixelCount', PPT_M)],
    'ep14': [('ModulePixelIdStart', 14*8192), ('PixelCount', PPT_M)],
    'ep15': [('ModulePixelIdStart', 13*8192), ('PixelCount', PPT_M)],
    'ep16': [('ModulePixelIdStart', 15*8192), ('PixelCount', PPT_S)],
    'ep17': [('ModulePixelIdStart', 16*8192), ('PixelCount', PPT_S)],
    'ep18': [('ModulePixelIdStart', 17*8192), ('PixelCount', PPT_S)],
}
