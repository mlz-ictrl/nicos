description = 'GE detector setup PV values'
group = 'configdata'

EIGHT_PACKS = [
    ('ep01', 'GE-D76A55-EP'),
    ('ep02', 'GE-D74199-EP'),
    ('ep03', 'GE-D7426B-EP'),
    ('ep04', 'GE-D76A68-EP'),
    ('ep05', 'GE-D74270-EP'),
    ('ep06', 'GE-D72EB0-EP'),
    ('ep07', 'GE-D72F9D-EP'),
    ('ep08', 'GE-D73043-EP'),
    ('ep09', 'GE-D7561E-EP'),
    ('ep10', 'GE-D72EA6-EP'),
    ('ep11', 'GE-D75751-EP'),
    ('ep12', 'GE-D73046-EP'),
    ('ep13', 'GE-D75623-EP'),
    ('ep14', 'GE-D72F44-EP'),
    ('ep15', 'GE-D7304D-EP'),
    ('ep16', 'GE-D74372-EP'),
    ('ep17', 'GE-D7436D-EP'),
    ('ep18', 'GE-D76A50-EP'),
]

HV_VALUES = {n[0]: 1530 for n in EIGHT_PACKS}
# -- To set different HVs for some 8-packs:
# HV_VALUES['ep01'] = 0

PV_SCALES = {
    'ep01': [('AScales', [2038, 1947, 1937, 1962, 1993, 1956, 1957, 1970]), ('Scales', [2258, 2252, 2242, 2263, 2246, 2251, 2236, 2249])],
    'ep02': [('AScales', [1957, 1969, 1999, 2025, 1944, 1970, 1958, 1965]), ('Scales', [2250, 2246, 2257, 2239, 2230, 2239, 2235, 2227])],
    'ep03': [('AScales', [1958, 1953, 1956, 1908, 1938, 1930, 1956, 1923]), ('Scales', [2236, 2253, 2256, 2238, 2246, 2250, 2249, 2254])],
    'ep04': [('AScales', [2062, 2061, 2049, 2014, 2001, 2019, 2014, 2016]), ('Scales', [2057, 2062, 2069, 2078, 2074, 2071, 2062, 2070])],
    'ep05': [('AScales', [1946, 1960, 1996, 1985, 2015, 2013, 2011, 2004]), ('Scales', [2056, 2075, 2077, 2075, 2089, 2090, 2093, 2080])],
    'ep06': [('AScales', [1995, 1995, 1995, 2014, 2029, 2020, 2033, 2024]), ('Scales', [2064, 2080, 2074, 2079, 2080, 2079, 2089, 2087])],
    'ep07': [('AScales', [1988, 2026, 2007, 1980, 1980, 1994, 2018, 1990]), ('Scales', [2070, 2079, 2075, 2077, 2071, 2079, 2076, 2079])],
    'ep08': [('AScales', [1967, 1970, 1992, 1961, 1978, 1982, 1974, 2023]), ('Scales', [2054, 2059, 2068, 2073, 2075, 2077, 2051, 2084])],
    'ep09': [('AScales', [1994, 2012, 1988, 1978, 1978, 1998, 1974, 2011]), ('Scales', [2073, 2079, 2084, 2081, 2082, 2077, 2074, 2082])],
    'ep10': [('AScales', [1994, 1950, 2004, 1974, 1964, 1978, 1967, 1953]), ('Scales', [2080, 2081, 2077, 2079, 2078, 2075, 2068, 2075])],
    'ep11': [('AScales', [1999, 2004, 1981, 1998, 2010, 2010, 2030, 2002]), ('Scales', [2077, 2074, 2083, 2084, 2078, 2092, 2083, 2090])],
    'ep12': [('AScales', [1975, 1962, 1997, 1988, 1984, 2052, 2015, 1999]), ('Scales', [2059, 2062, 2081, 2075, 2085, 2081, 2086, 2082])],
    'ep13': [('AScales', [1995, 1990, 1996, 1977, 1982, 2035, 1990, 2020]), ('Scales', [2089, 2094, 2088, 2093, 2091, 2092, 2092, 2096])],
    'ep14': [('AScales', [2013, 2017, 2024, 1987, 1984, 1977, 2004, 2004]), ('Scales', [2093, 2093, 2088, 2087, 2093, 2095, 2097, 2092])],
    'ep15': [('AScales', [1981, 2031, 1991, 1958, 1986, 1978, 1972, 1994]), ('Scales', [2085, 2097, 2089, 2090, 2084, 2100, 2093, 2094])],
    'ep16': [('AScales', [1919, 1903, 1909, 1919, 1893, 1919, 1933, 1954]), ('Scales', [2259, 2274, 2267, 2262, 2256, 2268, 2265, 2272])],
    'ep17': [('AScales', [1945, 1889, 1859, 1905, 1850, 1874, 1928, 1862]), ('Scales', [2256, 2268, 2256, 2258, 2255, 2262, 2279, 2270])],
    'ep18': [('AScales', [1935, 1887, 1923, 1932, 1914, 1908, 1925, 1921]), ('Scales', [2270, 2244, 2269, 2261, 2258, 2276, 2257, 2264])],
}

# -- For recalibration, set everything to defaults:
#PV_SCALES = {
#    'ep%02d' % i: [('AScales', [2048]*8), ('Scales', PV_SCALES['ep%02d'%i][1][1])] for i in range(1, 19)
#}

# event modes
MODE = 0x03
MODE_DIAG = 0x06
MODE_FAKE = 0x23
MODE_FAKEDIAG = 0x26

PV_VALUES_COMMON = [
    ('Mode', MODE_DIAG),
    ('Sample1', 0),
    ('AccumulationLength', 30),
    ('NegativeVeto', -16384),
    ('PositiveVeto', 16383),
    ('DiscriminatorLevel', 1024),
    ('BScales', [2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048]),
    ('TubeEnables', [1, 1, 1, 1, 1, 1, 1, 1] + [0] * 24),
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
    'ep14': [('ModulePixelIdStart', 13*8192), ('PixelCount', PPT_M)],
    'ep15': [('ModulePixelIdStart', 14*8192), ('PixelCount', PPT_M)],
    'ep16': [('ModulePixelIdStart', 15*8192), ('PixelCount', PPT_S)],
    'ep17': [('ModulePixelIdStart', 16*8192), ('PixelCount', PPT_S)],
    'ep18': [('ModulePixelIdStart', 17*8192), ('PixelCount', PPT_S)],
}
