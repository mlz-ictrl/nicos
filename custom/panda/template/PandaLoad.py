import math
import os
import os.path
import re
import math
import ast
import numpy as np
from matplotlib.mlab import griddata
import matplotlib.pyplot as plt
#~ import numpy.ma as ma

def fromto(start, stop, step):
    #~ print 'fromto(%r, %r, %r) -> '%(start, stop, step),
    assert (float(stop-start)/float(step))>0
    r = []
    p = start
    while start <= p <=  stop or start >= p >= stop:
        r.append(p)
        p += step
    if not stop in r:
        r.append(stop)
    #~ print r
    return r

def tickstep(a, b, minticks = 9):
    #~ print 'ticking %r, %r, %r'%(a, b, minticks),
    a, b = min(a, b), max(a, b)
    d = float(b - a) / float(minticks)     #make a first guess
    scale = 1.0
    while d < 1:
        d = d * 10
        scale = scale * 0.1
    while d > 10:
        d = d * 0.1
        scale = scale * 10
    # apply 1:2:5 downscaling
    if d < 2:
        d = 1
    elif d < 5:
        d = 2
    else:
        d = 5
    d = d * scale
    # round a and b to d
    a = d * int(a / d)
    b = d * int(b / d + 1 - 1e-6)
    c = int(round((b - a) / d) + 1)
    return a, b, (b - a) / float(c - 1)

def ticks(a, b, minticks=9):
    return fromto(*tickstep(a, b, minticks))

def lm(*args): #joins any number of lists into one
    if len(args) <= 1:
        return args[0]
    elif len(args) == 2:
        return args[0] + args[1]
    else:
        i = int(len(args) / 2)
        return lm(*args[:i]) + lm(*args[i:])


def plot(*args, **kwargs):
    if len(args) == 0:
        raise UsageError('Need Scans to plot!!!')
    # parse args and sort possible label
    myargs = []
    for a in args:
        if type(a) == NicosData:
            myargs.append(a)
        elif type(a) in (list, tuple):
            for i in a:
                myargs.append(i)
        else:
            myargs.append(a)
    scans = []
    for i in myargs:
        if type(i) == NicosData:  # got a scan
            scans.append([i, '#%d' % i.number])
        elif type(i) == str:   # got a label
            if len(scans) == 0:
                raise UsageError('Please put a scan before assigning a label')
            scans[-1][1] += ', ' + i
        else:
            raise UsageError('Unknown type of argument %r. I understand only scans and labelstrings!' % i)
    pars = kwargs.pop('pars', None)        # Parameternames (temperatures/fields/etc) to include in labels
    xcol = kwargs.pop('xcol', myargs[0].colnames[0])    # defaults to first scanarg
    ycol = kwargs.pop('ycol', myargs[0].detcols[-1])    # default to last detector
    shiftby = int(kwargs.pop('shiftby', 0))     # amount of ycol-units to shift plots
    if len(kwargs) != 0:
        raise UsageError('too many keyword arguments given I don\' understand:\n'
            ', '.join(kwargs.keys()))
    # evaluate pars
    if pars != None and type(pars) == str:       # single par -> make tuple
        pars = (pars, )
    if type(pars) in (list, tuple):      # more than one!
        # check that we understand the string (it must be a valid attr for all scans)
        for i, (s, l) in enumerate(scans):
            for p in pars:
                # try to read it
                l += ', ' + p + ' = %.3f' % np.mean(s[p]) + ' (' + s[p + '_unit'] + ')'
            scans[i][1] = l
    symbols = 'o-k o-r o-b o-g x:k x:r x:b x:g'.split()
    labels = []
    for i, (s, l) in enumerate(scans):
        try:
            plt.errorbar(s[xcol], [y + i * shiftby for y in s[ycol]], s[ycol + '_err'], None, symbols[i])
        except Exception:
            plt.plot(s[xcol], [y + i * shiftby for y in s[ycol]], symbols[i])
        labels.append(l if shiftby == 0 else l + ' shifted by %d' % (i * shiftby))
    plt.legend(labels)
    try:
        m = scans[0][0]
        plt.title(m.Exp_proposal + ' ' + m.Sample_samplename + ' ' + m.Exp_title[:20] + ' ' +
                  m.Exp_remark + ' scans ' + shortlist([s[0].number for s in scans]))
    except Exception:
        plt.title('plot of scans ' + shortlist([s[0].number for s in scans]))
    plt.xlabel(xcol + ' (' + scans[0][0][xcol + '_unit'] + ')')
    plt.ylabel(ycol + ' (' + scans[0][0][ycol + '_unit'] + ')')
    return plt

def MakeMap(*args, **kwargs):

    if len(args) == 0:
        raise UsageError('Need Scans to make a mapping from!!!')
    if len(args) == 1:
        scans = args[0]
    else:
        scans = args
    if not type(scans) in [list, tuple]:
        scans = [scans]   # may be a single scan was given......
    points = kwargs.pop('points', 33)
    clim = kwargs.pop('clim', kwargs.pop('zlim', None))
    #~ zlim = kwargs.pop('zlim', kwargs.pop('clim', None))
    xcol = kwargs.pop('xcol', scans[0].colnames[0])    # defaults to first scanarg
    ycol = kwargs.pop('ycol', scans[0].colnames[1])    # defaults to second scanarg
    zcol = kwargs.pop('zcol', scans[0].detcols[-1])    # default to last detector
    contourlines = kwargs.pop('clines', None)     # which countourlines to draw (or none for Auto)
    colorlevels = kwargs.pop('clevels', None)     # which colorlevels to use (or None for Auto)
    lw = kwargs.pop('cwidths', None)              # linewidths for colorlevels (or None for Auto or a single value for fixed value
    if len(kwargs) != 0:
        raise UsageError('too many keyword arguments given I don\' understand:\n'
            ', '.join(kwargs.keys()))

    x = []
    y = []
    z = []
    for s in scans:
        for p in s[xcol]:
            x.append(p)
        for p in s[ycol]:
            y.append(p)
        for p in s[zcol]:
            z.append(p)
    k = zip(x, y)
    for i in range(len(k)):
        if k[i] in k[i + 1:]:
            x[i] -= float(i) * 1e-6
            y[i] += float(i + 1) * 1e-6

    x = np.array(x)
    y = np.array(y)
    z = np.array(z)
    xw = max(x) - min(x)
    yw = max(y) - min(y)
    # define grid.
    _ = tickstep(min(x) - 0.05 * xw, max(x) + 0.05 * xw, points)
    xi = np.linspace(_[0], _[1], (_[1] - _[0]) / _[2])
    _ = tickstep(min(y) - 0.05 * yw, max(y) + 0.05 * yw, points)
    yi = np.linspace(_[0], _[1], (_[1] - _[0]) / _[2])

    #~ xi = np.linspace(min(x)-0.1*xw, max(x)+0.1*xw, points)
    #~ yi = np.linspace(min(y)-0.1*yw, max(y)+0.1*yw, points)
    # grid the data.
    zi = griddata(x, y, z, xi, yi)
    # contour the gridded data, plotting dots at the data points.
    #~ plt.clf()

    # evaluate contouring args
    if not clim:
        _ticks = tuple(tickstep(min(z), max(z)))
        clim = (_ticks[0], _ticks[1])
    _ticks = tuple(ticks(clim[0], clim[1]))
    if contourlines == None:
        contourlines = _ticks
    if colorlevels == None:
        colorlevels = contourlines
        colorlevels = tuple(ticks(clim[0], clim[1], 50))

    if lw == None:
        lw = [0.5] * len(contourlines)      # default linewidth is 0.5
        for i in ticks(clim[0], clim[1], 2):
            if i in contourlines:
                lw[contourlines.index(i)] = 1.5
    elif type(lw) not in (tuple, list):
        lw = [lw] * len(contourlines)      # default linewidth is given
    # otherwise use given values...

    # check lengths:
    if len(lw) != len(contourlines):
        raise UsageError('Length of cwidths must be the same as length of clines!')

    # all done, now plot the thing....
    Cl = plt.contour(xi, yi, zi, contourlines, linewidths=lw, colors='k', zmin=clim[0], zmax=clim[1])
    Cl.set_clim(clim)
    Cl.zmin = clim[0]
    Cl.zmax = clim[1]
    Cc = plt.contourf(xi, yi, zi, colorlevels, cmap=plt.cm.jet, extend='both', zmin=clim[0], zmax=clim[1])
    Cc.set_clim(clim)
    Cc.zmin = clim[0]
    Cc.zmax = clim[1]
    Cb = plt.colorbar() # draw colorbar
    Cb.set_clim(clim)
    Cb.set_ticks(_ticks)
    Cb.set_clim(clim)
    Cb.set_ticks(_ticks)
    Cb.vmin = clim[0]
    Cb.vmax = clim[0]
    Cb.locator.set_bounds(clim[0], clim[1])
    zstring = zcol + ' (' + scans[0][zcol + '_unit'] + ')'
    if scans[0].normcol:
        zstring += '  per  %s = %g (%s)' % (scans[0].normcol, scans[0].normval, scans[0][scans[0].normcol + '_unit'])
    Cb.set_label(zstring)  # put label on colorbar
    # plot data points.
    plt.scatter(x, y, marker='o', c='w', s=10, linewidths=(1.0, ))
    plt.xlim(min(x), max(x))
    plt.ylim(min(y), max(y))
    try:
        m = scans[0]
        plt.title(m.Exp_proposal + ' ' + m.Sample_samplename + ' ' + m.Exp_title[:20] + ' ' +
                  m.Exp_remark + ' scans ' + shortlist([s.number for s in scans]))
    except Exception:
        plt.title('griddata of scans ' + shortlist([s.number for s in scans]))
    plt.xlabel(xcol + ' (' + scans[0][xcol + '_unit'] + ')')
    plt.ylabel(ycol + ' (' + scans[0][ycol + '_unit'] + ')')
    return plt

def shortlist(l):
    ''' try to find a shorter way of representing a non-overlapping,
    ascending list of integers '''
    r = []
    i = 0
    while i + 1 < len(l):
        a = l[i] # first num in sequence
        while i + 1 < len(l) and l[i + 1] == l[i] + 1:
            i = i + 1
        b = l[i] # last num in sequence
        if b != a:
            a = str(int(a))
            b = str(int(b))
            # skip same digits on b,
            # keep k digits
            k = 0
            for j in range(k, len(a)):
                if b[j] == a[j]:
                    b = b[:j - k] + ' ' + b[j + 1 - k:]
                else:
                    break
            b = b.strip()
            r.append(a + '...' + b)
        else:
            r.append(str(a))
        i = i + 1
    return ', '.join(r)

class Mapping(object):
    ''' handles all necessary stuff for mappings '''
    #DONT USE! It#s not working (yet)
    fit = None
    def __init__(self, *args, **kwargs):
        if len(args) == 0:
            raise UsageError('Need Scans to make a mapping from!!!')
        if len(args) == 1:
            scans = args[0]
        else:
            scans = args
        if not type(scans) in [list, tuple]:
            scans = [scans]   # may be a single scan was given......
        self.scans = scans
        self.points = [kwargs.pop('points', 20)] * 2 #default 'resolution'
        self.clim = kwargs.pop('clim', kwargs.pop('zlim', None))
        self.xlim = kwargs.pop('xlim', None)
        self.ylim = kwargs.pop('ylim', None)
        self.zlim = kwargs.pop('zlim', kwargs.pop('clim', None))
        self.xcol = kwargs.pop('xcol', scans[0].colnames[0])    # defaults to first scanarg
        self.ycol = kwargs.pop('ycol', scans[0].colnames[1])    # defaults to second scanarg
        self.zcol = kwargs.pop('zcol', scans[0].detcols[-1])    # default to last detector

        if len(kwargs) != 0:
            raise UsageError('too many keyword arguments given I don\' understand:\n'
                ', '.join(kwargs.keys()))
        try:
            self.title = (scans[0].Exp_proposal + ' ' + scans[0].Sample_samplename + ' ' +
                          scans[0].Exp_title[:22] + ' ' + scans[0].Exp_remark + ' scans ' +
                          shortlist([s.number for s in scans]))
        except Exception:
            self.title = ('griddata of scans ' + shortlist([s.number for s in scans]))

        self._process_col()
        self._process_lim()

    def _process_col(self):
        # the following needs to be redone on xcol/ycol/zcol changes !!!
        x = []
        y = []
        z = []
        scans = self.scans
        for s in scans:
            for p in s[self.xcol]:
                x.append(p)
            for p in s[self.ycol]:
                y.append(p)
            for p in s[self.zcol]:
                z.append(p)
        k = zip(x, y)
        for i in range(len(k)):
            if k[i] in k[i + 1:]:
                x[i] -= float(i) * 1e-6
                y[i] += float(i + 1) * 1e-6

        self.x = np.array(x)
        self.y = np.array(y)
        self.z = np.array(z)

        self.xwidth = max(x) - min(x)
        self.ywidth = max(y) - min(y)
        self.xmin = min(self.x)
        self.xmax = max(self.x)
        self.ymin = min(self.y)
        self.ymax = max(self.y)
        self.zmin = min(self.z)
        self.zmax = max(self.z)

        self.xlabel = self.xcol + ' (' + scans[0][self.xcol + '_unit'] + ')'
        self.ylabel = self.ycol + ' (' + scans[0][self.ycol + '_unit'] + ')'
        self.zlabel = self.zcol + ' (' + scans[0][self.zcol + '_unit'] + ')'
        if scans[0].normcol:
            self.zlabel += '  per  %s = %g (%s)' % (scans[0].normcol, scans[0].normval,
                                                      scans[0][scans[0].normcol+'_unit'])


    def _process_lim(self):
        if not self.xlim: self.xlim = (self.xmin, self.xmax)
        if not self.ylim: self.ylim = (self.ymin, self.ymax)
        if not self.zlim: self.zlim = (self.zmin, self.zmax)
        if not self.clim: self.clim = self.zlim

        self._ticks = ticks(self.zlim[0], self.zlim[1])
        self._contourlines = tuple(ticks(self.zlim[0], self.zlim[1]))
        self._colorlevels = tuple(ticks(self.clim[0], self.clim[1], 50))

        lw = [0.5] * len(self._contourlines)
        for i in ticks(self.clim[0], self.clim[1], 2):
            if i in self._contourlines:
                lw[self._contourlines.index(i)] = 1.5
        self._linewidths = lw

    def plot(self, *kwargs):
        ''' shall plot a mapping. if it was fitted, also plot the fit '''
        raise Exception('Not Implemented yet')
        #~ if self.fit:
            #~ # make bigger window
            #~ # plot mapping
            #~ # plot fit
            #~ # plot fitargs
            #~ pass
        #~ else:
            #~ # make smaller window
            #~ # plot mapping
            #~ pass

    #~ def fit(self, fitfunc, *fitargs):
        #~ ''' do a fit of a 2d fitfunc to the data of the mapping '''
        #~ self.fit = fit2d(self.x, self.y, self.z, fitfunc, *fitargs)


class UsageError(Exception):
    pass
# container for data storage
class NicosData(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self)
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            if name.isupper():
                return self[name.lower()]
            elif name.islower():
                return self[name.upper()]
            else:
                raise
    def __setattr__(self, name, val):
        self[name] = val
    def __delattr__(self, name):
        del self[name]
    def join(self, other):
        if type(other) in [tuple, list]:
            for o in other:
                self.join(o)
            return
        elif not isinstance(other, NicosData):
            print 'can not join %r, it needs to be of type NicosData!!!' % other
            raise UsageError
        if self.colnames != other.colnames:
            print 'can not join scans with different colnames !'
            print 'me = %r\nother = %r!' % (self.colnames, other.colnames)

#for new style files
def NicosLoad(prefix, filenum=-1, **kwargs):
    ''' use this as 's = NicosLoad("/data/exp/p1234", 32000, mon1 = 1e5)'
    to load datafiles /data/exp/p1234_00032000.dat and normalize all datapoints on
    mon1 to a monitor rate of 1e5
    Result is an object with attributes which are named after
    the colums of the scan and which can be used directly for plotting/fitting/....
    '''
    if filenum != -1:
        # if we got more than one filenum, iterate and return a set of scans
        if type(filenum) in [list, tuple]:
            r = []
            for fn in filenum:
                try:
                    s = NicosLoad(prefix, fn, **kwargs)
                    if s != None:
                        r.append(s)
                except Exception:
                    print 'Error loading filenumber %d' % fn
                    import traceback
                    traceback.print_exc()
            return r
    filename = None
    # check existence of file and check format (old style or new style)
    for f in [prefix, '%s_%08d' % (prefix, filenum), '%s_%08d.dat' % (prefix, filenum)]:
        if os.path.exists(f) and os.path.isfile(f):
            filename = f
            break
    if not filename:
        print "File %s:%d does not exist!" % (prefix, filenum)
        return None
    print "Loading file %s" % filename

    def pythify(v):
        ''' tries to return a pythonic value for a given string'''
        try:
            if v[0] == '[': # try to parse list
                if v.rfind(']') > -1:
                    return ast.literal_eval(v[:v.rfind(']') + 1])
                else:
                    pass
            elif v[0] == "'" and v.rfind("'") > 0:
                return v[1:v.rfind("'") - 1]
            elif v[0] == '"' and v.rfind('"') > 0:
                return v[1:v.rfind('"') - 1]
            return float(v)
            return int(v)  # pylint: disable=W0101
        except Exception:
            return v
    valid_units = 'T K meV A A-1 THz mm deg % m mK s min cts rlu r.l.u. bar mbar'.split()
    def parse_vu(vu): #take a string and try to separate value and unit and return both (or empty strings)
        if vu.find(' ') == -1:
            return pythify(vu), ''   # no space -> one value, no unit
        #~ if sum(map(lambda x: 1 if x.isspace() else 0, vu)) == 1: # exactly 1 space -> easy
        if sum((1 if x.isspace() else 0 for x in vu)) == 1: # exactly 1 space -> easy
            v, u = vu.split(' ')
            if u in valid_units:
                return pythify(v), u
            else:
                return vu, ''
        if vu[0] == '[':
            i = vu.rfind(']')
            if i > 0:
                u = vu[i + 1:].strip()
                v = pythify(vu[:i + 1])
        elif vu[0] == '(':
            i = vu.rfind(')')
            if i > 0:
                u = vu[i + 1:].strip()
                v = pythify(vu[:i + 1])
        elif vu[0] == '"':
            i = vu.rfind('"')
            if i > 0:
                u = vu[i + 1:].strip()
                v = pythify(vu[:i + 1])
        elif vu[0] == "'":
            i = vu.rfind("'")
            if i > 0:
                u = vu[i + 1:].strip()
                v = pythify(vu[:i + 1])
        else:
            return pythify(vu), ''
        if u in valid_units:
            return v, u

        # try to split unit if needed.
        if len(u) > 1 and u.find(' ') > -1:
            u = u.split(' ')
        return v, u

    def process_old(data, line):
        print 'warning, not implemented for old style files'

    def process_header_nicos2(data, line, _re_header = re.compile(r'^#?\s*([^:]*?)\s*:\s*(.*?)\s*$')):
        ''' process part of header, where values are literal or special'''
        if line.startswith('### Scan data'):
            return False    # end of header, next section please!
        if line.startswith('###'):
            return  True# ignore separators
        try:
            k, vu = _re_header.match(line).groups()
            v, u = parse_vu(vu)
            if k.endswith('filter_value'):
                if u in ['K', 'Ohm', 'R', 'T', 'mm']:
                    ks = k.rsplit('_', 1)[0]
                    data[ks] = v
                    data[ks + '_unit'] = u
                else:
                    data[k] = pythify(vu)
            elif k.endswith('_value'): #store value and unit separately
                ks = k.rsplit('_', 1)[0]
                data[ks] = v
                data[ks + '_unit'] = u
            else:
                data[k] = pythify(v)      # insert into data object
        except AttributeError:
            print 'Warning: malformed headerline detected!'
            print 'Offending line was: %r' % line
        return True

    def process_tableheader_nicos2(data, line):
        if data.get('colnames'):   # have names already, read units:
            data.colunits = line[1:].split()
            for i in range(len(data.colnames)):
                if data.colnames[i] != ';':
                    data[data.colnames[i] + '_unit'] = data.colunits[i]
            return False    # next section please
        else:
            # read colnames
            data.colnames = line[1:].replace(':', '_').split() # translate : to _ first and then split into columnames
            # check for and mangle duplicate detector colnames!
            detcolstart = data.colnames.index(';') + 1
            detcolend = len(data.colnames)
            nm = re.compile('([^0-9]*?)([0-9]*?)')
            for i in range(detcolstart, detcolend-1):   # only check detector columns
                n = data.colnames[i]
                while n in data.colnames[i + 1:]:
                    j = data.colnames.index(n, i + 1) # index of duplicate, which must be > = i !!!
                    # try to find another name
                    try:
                        pre, post = nm.match(data.colnames[j]).groups()
                        post = int(post)
                    except Exception:
                        pre = data.colnames[j] + '_'
                        post = 0
                    post += 1 # try a number higher
                    data.colnames[j] = '%s%d' % (pre, post) # change the later name
            # names are now ok. any surviving duplicates will be ignored during reading the table
            # we can not just drop duplicates here or we loose the connection between column index and column name!
            for n in data.colnames:
                if n != ';':
                    data[n] = []  # this will be a list to append points to....
            data.detcols = data.colnames[detcolstart:]
        return True

    def process_table_nicos2(data, line):
        if line.startswith('### End of NICOS data file '):
            return False        # next section please
        c = line.split()
        if len(c) != len(data.colnames):
            print 'Data block: Line too short! has %d columns, but should have %d!' % (len(c), len(data.colnames))
            print 'Offending line was: %r' % line
            return False #don't continue!
        for i in range(len(c)): # iterate over all columns
            if c[i] == ';': continue    # try next column
            if data.colnames[i] in data.colnames[i + 1:]: # there will be another column with same name, forget this value!
                continue
            data[data.colnames[i]].append(pythify(c[i]))  # append value to correct column
        return True

    # format is decided upon format of first line:
    fileformat = 'unknown'
    #~ header = True
    #~ tableheader = False
    #~ table = False
    with open(filename, 'rU') as f:   # open file and ignore different line-endings
        l = f.readline()  # read first line
        if l.startswith('filename     : '):
            fileformat = 'old'
            process = [process_old]
        elif l.startswith('### NICOS data file, created at '):
            fileformat = 'Nicos2'
            process = [process_header_nicos2,
                       process_tableheader_nicos2,
                       process_table_nicos2]
        else:
            print 'WARNING: unknown format detected, aborting!'
            print '(first line was %r)' % l
            return
        print "detected %s format, " % fileformat,
        data = NicosData()    # used to store stuff
        while l != '':
            #~ print '%r %r'%(process[0], l),
            # process data
            r = process[0](data, l)  # pylint: disable=E1111
            #~ print r
            if not r:
                process.pop(0)  #remove sectionparser
            if len(process)  ==  0: # no parsers left
                break
            l = f.readline()
    data.colnames = data.get('colnames', [])
    try:
        d = data.colnames
    except Exception:
        print 'colnames not found !'
        for k, v in data.items():
            print k, '\t', repr(v)
    for i in range(len(data.colnames)-1, -1, -1):
        d = data.colnames[i]
        if d == ';' or d in data.colnames[i + 1:]:
            data.colnames.pop(i)
            data.colunits.pop(i)
    # put errorbars on all detectors as default
    for n in data.detcols:
        if data.colunits[data.colnames.index(n)]  == 'cts':
            data[n + '_err'] = map(math.sqrt, data[n])
    # XXX try to normalize data !!!
    normcol = None
    normval = 1
    if len(kwargs) > 0:   # try to do normalisation
        for k, v in kwargs.items():  # ignore other kwargs....
            if k in data.detcols:
                if normcol != None:
                    print 'Can not normalize to more than one detector colum! Found %s+%s at least!' % (normcol, k)
                    print 'Skipping normalisation !'
                    return data
                else:
                    normcol = k
                    normval = v
    if not normcol:
        data.normcol = None
        return data
    data.normcol = normcol
    data.normval = normval
    # here we have to normalize all data points
    for i in range(len(data[normcol])):
        r = float(normval) / float(data[normcol][i])  # find multiplicator for point i
        #~ for c in data.detcols + map(lambda x: x + '_err', data.detcols):
        for c in data.detcols + [x + '_err' for x in data.detcols]:
            if data.get(c):
                data[c][i] = data[c][i] * r
    return data


# this only works for old format !
def PandaLoad(filename):
    class PandaScan(object):
        import re
        header = {}
        _filename = None
        _re_direct = re.compile(r'^\s*([^:]*?)\s*:\s*(.*?)\s*$')
        _re_scandata = re.compile(r'^scan data:$')

        def __init__(self, filename = None):
            if filename != None:
                self.load(filename)
        def __repr__(self):
            if self._filename != None:
                return "PandaScan('%s')" % self._filename
            else:
                return "PandaScan()"
        def load(self, filename = None):
            self.polarized = False
            mapping = {'name:':'samplename',
                '1st orientation reflection':'orient1',
                '2nd orientation reflection':'orient2',
                'zone axis for scattering plane':'zoneaxis',
                'created at':'created',
                'PSI0 (deg)':'psi_offset',
                'Scattering sense':'scattersense',
                'mono focussing mode':'mono_focus',
                'ana  focussing mode':'ana_focus',
                'TAS operation mode':'opmode',
                'mth  (A1) (deg)':'mth_offset',
                'mtt  (A2) (deg)':'mtt_offset',
                'sth  (A3) (deg)':'sth_offset',
                'stt  (A4) (deg)':'stt_offset',
                'ath  (A5) (deg)':'ath_offset',
                'att  (A6) (deg)':'att_offset',
                }
            if filename == None:
                filename = self._filename # try a reload
            if filename == None:	# no filename to be found!
                print "Please give me a filename to load!"
                return
            if filename == self._filename:
                print "Reloading file %s" % filename
            else:
                print "Loading file %s" % filename
            self._filename = filename
            with open(filename, 'r') as f:
                line = '***'
                while line != '':
                    line = f.readline()
                    # now parse the lines
                    if line.startswith(('***', 'Sample information',
                                        'instrument general setup at file creation',
                                        'offsets of main axes')):
                        continue
                    # translate if necessary
                    for k, v in mapping.items():
                        if line.startswith(k):
                            line = v + line[len(k):]
                    if line.startswith('counting for switching devices'):	# polarized measurements!
                        self.pol_devices = [d.strip() for d in line.split(']')[0].split('[')[1].split(', ')]
                        self.pol_states = []
                        self.polarized = True
                        for s in line.split('states ')[1][1:-1].split('], ['):
                            s = [d.strip() for d in s.split(', ')]
                            ts = {}
                            for i in range(len(self.pol_devices)):
                                ts[self.pol_devices[i]] = s[i]
                            self.pol_states.append(ts)
                    if line.startswith('scan data:'):	# header finished, now parse data section
                        self.command = f.readline().strip()
                        self.colnames = []
                        polstate = -1
                        for i in f.readline().strip().split():
                            #~ if i  != ';': 		# somehow figure out 'x' and 'y' and set the fields....
                            if self.polarized:	#mangle column names for detx, monx+time
                                if i.startswith('det') or i.startswith('mon') or i.startswith('time'):
                                    if i.startswith('time'): polstate += 1 # time is always first det column
                                    for d in self.pol_devices:
                                        i = i + '__' + d + '_' + self.pol_states[polstate][d]
                            self.colnames.append(i)
                            self.__dict__.setdefault(i, [])
                        self.colunits = []
                        for i in f.readline().strip().split():
                            #~ if i  != ';':
                            self.colunits.append(i)
                        self.columns = len(self.colnames)
                        # (re)-set the units (they might be different....)
                        for i in range(self.columns):
                            if self.colnames[i] != ';':
                                self.__dict__['%s_unit' % self.colnames[i]] = self.colunits[i]
                        while line != '':
                            line = f.readline()
                            if line == '':continue
                            if line.startswith('***'): line = '' # marks end of data
                            else:
                                line = line.split()
                                if len(line) != self.columns:
                                    print 'INCOMPLETE DATA !'
                                else: # now store data into the object
                                    for i in range(self.columns):
                                        l = self.colnames[i]
                                        if l != ';' and type(self.__dict__[l])  != list:
                                            self.__dict__[l] = [] # on first line we prepare the element to hold the data
                                        try:
                                            v = line[i]
                                            v = float(v)	# try to convert to float, ignore failure to do so
                                        except Exception:
                                            pass
                                        self.__dict__[l].append(v)	# store data
                        # here we might want to parse optional data after the data-section
                        # normally there is nothing there and we just ignore all the stuff.
                        while line != '':
                            line = f.readline()
                        break	# we are done!
                    try: # try to parse header lines
                        k, v = self._re_direct.findall(line)[0]
                        if v.strip() == v and len(v.split()) == 1:
                            self.__dict__[k] = v
                            #~ print "SIMPLE", k, v
                        elif k.find('filter') > -1 or k in ('saph', 'user', 'phone', 'fax', 'orient1', 'orient2',
                                                            'zoneaxis', 'responsable', 'created', 'scattersense',
                                                            'samplename'): #take whole value
                            self.__dict__[k] = v
                            #~ print "FILTER", k, v
                        elif k in ('ss1', 'ss2'):
                            for i in range(4):
                                self.__dict__['%s_%s' % (k, ('left', 'right', 'bottom', 'top')[i])] = float(v.split()[i])
                                self.__dict__['%s_%s_unit' % (k, ('left', 'right', 'bottom', 'top')[i])] = v.split()[4]
                            self.__dict__[k] = tuple([float(b) for b in v.split()[:4]])
                            self.__dict__['%s_unit' % k] = v.split()[4]
                            #~ print "SLIT", k, v
                        elif k in ('a, b, c (A)', 'alpha, beta, gamma (deg)'):
                            for i in range(3):
                                self.__dict__[(k.split()[0].split(', '))[i]] = float(v.split(', ')[i])
                                self.__dict__['%s_unit' % (k.split()[0].split(', '))[i]] = k.split()[1][1:-1]
                            #~ print "LATTICE", k, v
                        elif k == 'opmode':
                            self.__dict__[k] = v.split()[0][1:-1]
                            self.__dict__[v.split()[0][1:-1]] = v.split()[2]
                            #~ print "OPMODE", k, v.split()[0][1:-1], v.split()[2]
                        elif v.endswith(('mm', 'deg', 'A-1', 'THz', 'meV', 'T', 'K', 'bar', '%', 's', 'min', 'A')):
                            self.__dict__[k] = v.split()[0]
                            self.__dict__['%s_unit' % k] = v.split()[1]
                            #~ print "UNITS", k, v.split()
                        else: print "X: ", k, v.split()
                    except Exception as e:
                        print e
                        #~ pass #ignore bad lines.....

    return PandaScan(filename)

#
if __name__ == '__main__':
    import gtk  # pylint: disable=W0611

    import matplotlib
    matplotlib.use('GTKAgg')
    import matplotlib.pyplot as plt
    #~ import matplotlib.artist as artist
    #~ import matplotlib.colors as colors

    #~ s = PandaScan('../data/test_00033343')
    s1 = PandaLoad('/data/2010/cycle_25/p4305_00044189')
    print s1, dir(s1)
    s2 = PandaLoad('/data/2010/cycle_25/p4305_00044190')
    s3 = PandaLoad('/data/2010/cycle_25/p4305_00044191')
    sp = PandaLoad('/data/2009/cycle_22a/p3705_00036828')
    n = NicosLoad('/data/2012/cycle_28/service_00047333.dat')
    n = NicosLoad('/data/2012/cycle_28/p6658', range(49526, 49529))
    plot(n, 'special label', pars='stt', shiftby=10).show()


    import sys
    sys.exit(1)

    #~ print n, dir(n)

    #~ print sp.pol_devices
    #~ print sp.pol_states
    #~ print sp.colnames
    #~ print sp.colunits

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_xlim(-1, 6)
    ax.set_ylim(0, 600)

    plt.plot(s1.measE, s1.det2, 'o-r', s2.measE, s2.det2, 'x:', s3.measE, s3.det2, 'bo-')
    plt.show()

    plt.plot(n.h, n.det2, 'o-r')
    plt.show()

    s = NicosLoad('/data/2012/cycle_28/p6658', 49609, mon1=10000)
    t = NicosLoad('/data/2012/cycle_28/p6658', 49452, mon1=1000)
    #plt.plot(s.E, s.det2, 'o-r', t.E, t.det2, 'x:')
    plt.errorbar(s.E, s.det2, s.det2_err, None, 'o-r')
    plt.errorbar(t.E, t.det2, t.det2_err, None, 'x:')
    plt.show()


    #~ sys.exit(1)

    # try mapping
    #~ m = NicosLoad('/data/2012/cycle_28/p6658', range(49526, 49556+1))
    m = NicosLoad('/data/2012/cycle_28/p6658', range(49557, 49581+1))

    import numpy as np
    from matplotlib.mlab import griddata
    import matplotlib.pyplot as plt
    #~ import numpy.ma as ma
    #~ from numpy.random import uniform

    x = []
    y = []
    z = []
    for s in m:
        for p in s.l:
            x.append(p)
        for p in s.h:
            y.append(p)
        for p in s.det2:
            z.append(p)
    k = zip(x, y)
    for i in range(len(k)):
        if k[i] in k[i + 1:]: # hack to avoid to points on exactly same position
            x[i] -= 3.5e-4
            y[i] += 1.5e-4

    x = np.array(x)
    y = np.array(y)
    z = np.array(z)
    xw = max(x)-min(x)
    yw = max(y)-min(y)
    # define grid.
    xi = np.linspace(min(x) - 0.1 * xw, max(x) + 0.1 * xw, 201)
    yi = np.linspace(min(y) - 0.1 * yw, max(y) + 0.1 * yw, 201)
    # grid the data.
    zi = griddata(x, y, z, xi, yi)
    # contour the gridded data, plotting dots at the randomly spaced data points.
    CS = plt.contour(xi, yi, zi, 14, linewidths=0.5, colors='k')
    CS = plt.contourf(xi, yi, zi, 71, cmap=plt.cm.jet)
    plt.colorbar() # draw colorbar
    # plot data points.
    plt.scatter(x, y, marker='o', c='w', s=3, linewidths=(0.5, ))
    plt.xlim(min(x), max(x))
    plt.ylim(min(y), max(y))
    plt.title('TEST on scans %d...%d' % (m[0].number, m[-1].number), fontsize=28)
    plt.grid(True) # major/minor/both, x/y/both color = /linestyle = '-'/linewidth =
    plt.xlabel('L (r.l.u.)') #fontsize =
    plt.ylabel('H/K (r.l.u.)') #fontsize =
    #~ plt.savefig('map_7T7.pdf')
    plt.show()

