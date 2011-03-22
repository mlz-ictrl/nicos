"""
GracePlot.py -- A high-level Python interface to the Grace plotting package

The intended purpose of GracePlot is to allow easy programmatic and interactive
command line plotting with convenience functions for the most common commands. 
The Grace UI (or the grace_np module) can be used if more advanced
functionality needs to be accessed. 

The data model in Grace, (mirrored in GracePlot) goes like this:  Each grace 
session is like virtual sheet of paper called a Plot.  Each Plot can have 
multiple Graphs, which are sets of axes (use GracePlot.multi() to get multiple
axes in GracePlot).  Each Graph has multiple data Sets.  Data Sets are added to
graphs with the plot and histoPlot functions in GracePlot.

The biggest difference in use of my module over Nathaniel Gray's is that I have
abstracted nearly everything into objects. You can only plot a data object,
which contains all the information about symbols and lines for itself. This is
also how future support of other graph types will be builtin, for example error
bars and xyz etc... Currently, only 2d plots are directly implemented.  a
typical session might look like:
######################################################################
from GracePlot import *

p = GracePlot() # A grace session opens

x=[1,2,3,4,5,6,7,8,9,10]
y=[1,2,3,4,5,6,7,8,9,10]

s1=Symbol(symbol=circle,fillcolor=red)
l1=Line(type=none)

d1=Data(x=x,y=y,symbol=s1,line=l1)

p.plot(d1)

p.text('test',.51,.51,color=2)

p.title('Funding: Ministry of Silly Walks')
p.ylabel('Funding (Pounds\S10\N)')
p.xlimit(0, 6)  # Set limits of x-axis
######################################################################

The best place to find documentation is in the docstrings for each
function/class. In general, default values are used by xmgrace unless you set
them to something else. I have done some things like if you set the fill color
of a symbol, then it automatically sets the fill pattern to solid, unless you
set it to something else.

I have basically taken the output of xmgrace and reverse engineered everything
in the Gui and agr files to figure out all these details. The documentation for
grace is not that complete, and has been that way a long time.

An important thing to realize about GracePlot is that it only has a one-way
communications channel with the Grace session.  This means that if you make
changes to your plot interactively (such as changing the number/layout of
graphs) then GracePlot will have NO KNOWLEDGE of the changes.  This should not
often be an issue, since the only state that GracePlot saves is the number and
layout of graphs, the number of Sets that each graph has, and the hold state
for each graph.
Originally, this code started out from:

__version__ = "0.5.1"
__author__ = "Nathaniel Gray <n8gray@caltech.edu>"
__date__ = "September 16, 2001"

Slightly updated by Marcus H. Mendenhall, Vanderbilt University, to allow some
class overrides, including the underlying grace_np Further updated November 8,
2008 by MHM to correctly handle line styles & symbol styles in multi-graph
environments.  All styles used to go to G0.

__author__ = "John Kitchin" (no longer active)

Maintenance of this project was taken over by Marus Mendenhall in April, 2009.

The GracePlot instance no longer depends on any grace_np process as of April 1,
2009.  Instead, it communicates via subprocess.Popen.  This renders the package
incompatible with python < 2.4.

"""

__version__ = "1.44"
__author__ = "Marcus Mendenhall <mendenhall@users.sourceforge.net> (maintainer)"
__date__ = "2009/05/30 22:27:22"

import math
import string

def on_off(flag):
    """convert a bool into an xmgrace on/off string"""
    if flag and flag != 'off': return 'on'
    else: return 'off'
    
# shortcuts for colors
class colors:
    (white, black, red, green, blue, yellow, brown, grey, violet, cyan, magenta,
        orange, indigo, maroon, turquoise, green4) = range(16)
    gray=grey

# shortcuts for symbols
class symbols:
    (none, circle, square, diamond, triangle_up, triangle_left, triangle_down,
     triangle_right, plus, cross, star, character) = range(12)

# shortcuts for linestyle
class lines:
    none, solid, dotted, dashed, long_dashed, dot_dashed=range(6)

# shortcuts for fill patterns
class fills:
    none=0
    solid=1
    opaque=8

# string justification
left=0
center=2
right=1

#frame types
class frames:
    closed=0
    halfopen=1
    breaktop=2
    breakbottom=3
    breakleft=4
    breakright=5

import subprocess
import time
import threading
import weakref
import Queue

class Disconnected(Exception):
    """Thrown when xmgrace unexpectedly disconnects from the pipe.

    This exception is thrown on an EPIPE error, which indicates that
    xmgrace has stopped reading the pipe that is used to communicate
    with it.  This could be because it has been closed (e.g., by
    clicking on the exit button), crashed, or sent an exit command."""
    pass

def _sender(queue, pipe, redraw_interval, auto_redraw):
    """a thread to send data from a queue, so talking to grace doesn't tie up
    the main flow, and to manage redraws"""   
    #note that this is not a class method, to reduce some possible reference loops.
    last_redraw_time=-1
    timeout=None
    sent_commands=False
    redraw_soon=False
    redraw_now=False
    Empty=Queue.Empty
    
    while 1:
        try:
            now=time.time()
            if sent_commands and (redraw_now or (redraw_soon and \
               now > (last_redraw_time+ 0.9*redraw_interval) ) ):
                pipe.write("redraw\n")
                # nothing to do, but we sent stuff before, so redraw
                pipe.flush()
                sent_commands=False
                last_redraw_time=now
                redraw_soon=False
                redraw_now=False
                    
            data=queue.get(True, timeout)
            
            if data is None: #sentinel for a flush
                pipe.flush()
            elif data == -1: #all done, quit
                break
            elif data == -2: #forced redraw
                redraw_now=True
            elif data == -3: #redraw soon   
                redraw_soon=True
            else:
                pipe.write(data)
                sent_commands=True
            timeout=redraw_interval
        except Empty:
            if auto_redraw and sent_commands:
                # we timed out, but data had been sent without being drawn, so
                # draw it now
                redraw_now=True
            else: 
                # go all the way to sleep if we didn't get any data on the last
                # pass and no redraws may be pending
                timeout=None 
            continue
        except IOError:
            # IOError happens when grace dies, and will get recognized in the
            # main thread... just quit here
            break

def format_scientific(val):
    """ format x.xxxe+-yy as a typeset grace string """
    bits = val.split('e')
    if len(bits) == 1:
        return val #no exponent present, just leave it alone
    else:
        mant, exp = bits
        return mant + r"\x\#{b4}\f{}10\S"+str(int(exp))+r"\N"

class GracePlot:   

    resolution=72
    # create a subclass with this set to "gracebat", e.g. if you want no GUI
    grace_command = "xmgrace"
    # create a subclass with these arguments modified if you don't like them
    command_args=('-nosafe','-noask')
    
    def __init__(self, width=None, height=None, auto_redraw=True,
                 redraw_interval=0.1):
        """ Create a GracePlot object, which manages an external grace instance.
        The instance may have multiple GraceGraph objects within it.  Commands
        which are specific to a graph (such as plotting data) are sent to the
        graph object.  Commanbds which are global (such as redraw control) are
        sent to the GracePlot object.
        
        width*resolution=width in pixels, same for height.  Resolution is set to
        72 by default, so width is roughly inches on an old 72 dpi monitor.  By
        changing the class default resolution, you can change the units of width
        & height.
        
        if auto_redraw is True, the graph will automatically hold off redrawing 
        until data stops being sent for a time of redraw_interval (seconds).  
        
        To force an immediate redraw, call GracePlot.redraw(force=True).
        Calling GracePlot.redraw() without an argument schedules a redraw at the
        next quiet interval.  This mechanism greatly reduces thrashing of grace
        windows by repeated un-needed redraws.
        
        To force a redraw on the next cycle of the redrawing thread, call
        GracePlot.redraw(soon=True).  This will cause a redraw even if there is
        still data flowing, but not in a hurry.
        
        The GracePlot class does all its data transmission through a thread, so
        normally there should be no significant time during which the calling
        thread is blocked.  This should improve real-time performance.
        """
        self.debug=False

        self.pagewidth=width
        self.pageheight=height
        
        if width is not None and height is not None:
            args=self.command_args+('-fixed',str(self.resolution*width),
                                    str(self.resolution*height))
            self.aspect=float(width)/height
        else:
            args=self.command_args+('-free',)
            self.aspect=1.0
            
        args = args + ('-dpipe', '0')
        # the -pipe method to get stdin freezes grace until EOF, -dpipe works
        # right
        
        self.grace = subprocess.Popen((self.grace_command, ) + args,
            bufsize=65536,
            stdin=subprocess.PIPE, stdout=None, stderr=None, close_fds=True, shell=False
        )
                
        #start up a thread to send data, so main thread does not block waiting to draw
        self.auto_redraw=auto_redraw
        self._transmit_queue=Queue.Queue(50)
        transmitter=threading.Thread(target=_sender,
            args=(self._transmit_queue, self.grace.stdin,
                  redraw_interval, auto_redraw))
        transmitter.setDaemon(True)
        transmitter.start()
        self._transmitter=transmitter
        
        self.g=[]        
        self.new_graph()
        self.rows = 1
        self.cols = 1
        self.curr_graph=self.g[0]
        
    def __del__(self):
        self.close()
    
    def close(self):
        if self.is_open() and self._transmitter.isAlive():
            self.redraw(force=True)
            self._transmit_queue.put(-1) #flag to tell thread to quit
            self._transmitter.join()
    
    def focus(self, graph_index=None, grace_graph=None):
        """direct commands sent to the GracePlot to the appropriate GraceGraph...
        mostly for backwards compatibility. 
        It is preferable to send the commands directly to the plot"""
        if grace_graph is not None:
            self.curr_graph=grace_graph
        elif graph_index is not None and graph_index >= 0 and graph_index < len(self.g):
            self.curr_graph=self.g[graph_index]
        else:
            raise Exception("no valid graph to focus")
        
    def new_graph(self, **kwargs):
        """add a new graph to our list"""
        g2=GraceGraph(self, len(self.g), **kwargs)
        self.g.append(g2)
        self.focus(grace_graph=g2)
        return g2

    def plot(self, *args, **kwargs):
        """shortcut for sending the plot command directly to the appropriate
        graceGraph object."""
        self.curr_graph.plot(*args, **kwargs)

    def is_open(self):
        """Return True if the pipe is not known to have been closed."""
        return self.grace.poll() is None

    def _send(self, cmd): 
        """send a command to grace, and do not flush the pipe"""
        if not self.is_open(): #grace has melted down!
            raise Disconnected("Grace process has been terminated")
        cmd=cmd.strip()
        if cmd:
            if self.debug: print cmd
            self._transmit_queue.put(cmd+"\n")

    def _flush(self):
        self._transmit_queue.put(None) #sentinel for a flush
    
    def write(self, command):
        "make a graceSession look like a file, and flush after send"
        self._send(command)
        self._flush()

    def send_commands(self, *commands):
        "send a list of commands, and then flush"
        self._send("\n".join(commands))
        self._flush()

    def exit(self):
        """Nuke the grace session.  """
        self.write("exit")

    def redraw(self, force=False, soon=False):
        """Refresh the plot"""
        #print 'redraw'
        if soon:
            # cause timer to redraw on its next automatic cycle, whether graph is busy or not
            self._transmit_queue.put(-3)
        elif not self.auto_redraw  or force:
            self._transmit_queue.put(-2)
            while self.is_open() and self._transmit_queue.qsize():
                time.sleep(0.25) #make sure on a forced redraw that the queue is flushed
                
    def save(self, filename, format='agr'):
        """Save the current plot
        Default format is Grace '.agr' file, but other possible formats
        are: x11, postscript, eps, pdf, mif, svg, pnm, jpeg, png, metafile
        Note:  Not all drivers are created equal.  See the Grace documentation
            for caveats that apply to some of these formats."""
        devs = {'agr':'.agr', 'eps':'.eps', 'jpeg':'.jpeg', 'metafile':'',
                'mif':'', 'pdf':'.pdf', 'png':'.png', 'pnm':'', 
                'postscript':'.ps', 'svg':'', 'x11':''}
        try:
            ext = devs[string.lower(format)]
        except KeyError:
            print 'Unknown format.  Known formats are\n%s' % devs.keys()
            return
            
        if filename[-len(ext):] != ext:
            filename = filename + ext
        if ext == '.agr':
            self.write('saveall "%s"' % filename)
        #I basically only use PNG, so I haven't worked in support for the other ones. This
        #code is basically Nate Gray's but it didn't work for me, so I minimally fixed it.
        # I will probably extend it similar to the png example, since I like graphics
        # to be basically the same each time, and each device is subtly different
        elif ext == '.png': 
            self.send_commands('PAGE RESIZE 600,400', 'device "PNG" dpi 600',
                'hardcopy device "PNG"', 'print to "%s"' % filename, 'print')

    def resize( self, xdim, ydim, rescale=1 ):
        """Change the page dimensions (in pp).  If rescale==1, then also
        rescale the current plot accordingly.  Don't ask me what a pp is--I
        don't know."""
        if rescale:
            self.write('page resize %s %s' % (xdim, ydim))
        else:
            self.write('page size %s %s' % (xdim, ydim))

    def __getitem__( self, item ):
        """Access a specific graph.  Can use either p[num] or p[row, col]."""
        if type(item) == int:
            return self.g[item]
        elif type(item) == tuple and len(item) <= 2:
            if item[0] >= self.rows or item[1] >= self.cols:
                raise IndexError, 'graph index out of range'
            return self.g[item[0]*self.cols + item[1]]
        else:
            raise TypeError, 'graph index must be integer or two integers'

    def load_parameter_file(self, param_file_name):
        """load a grace *.par file"""
        self.write('getp "%s"' % param_file_name)
    
    def assign_color(self, idx, (r, g, b), name):
        self.write('map color %d to (%d, %d, %d), "%s"' % (idx, r, g, b, name))

    def aspect_scale(self, x, y):
        """scale view coordinates to that (1,1) fills view, roughly"""
        if x is not None:
            x=x*max(self.aspect, 1.0)
        if y is not None:
            y=y/min(self.aspect, 1.0)
        return (x,y)
       
class GraceGraph:
    """
    view_x is a tuple of (xmin,xmax)
    view_y is a tuple of (ymin,ymax)
    """
    def __init__(self, grace, gID, view_xmin=0.15, view_xmax=None,
                 view_ymin=0.15, view_ymax=None):
        self._hold = 0       # Set _hold=1 to add datasets to a graph

        self._grace = weakref.ref(grace)
        
        self.nSets = 0
        self.gID = gID

        self.world_xmin= 10000000000000.
        self.world_xmax=-10000000000000.
        self.world_ymin= 10000000000000.
        self.world_ymax=-10000000000000.
                
        if view_ymax is None:
            view_ymax=0.85
        if view_xmax is None:
            view_xmax=0.95
            
        self.SetView(xmin=view_xmin,xmax=view_xmax,ymin=view_ymin,ymax=view_ymax, aspect_scaled=True)
    
    def grace(self):
        s=self._grace() #dereference the weak ref
        if s is None:
            raise Disconnected("GraceGraph detached from main GracePlot!")
        else:
            return s
    
    def autoscale(self, axis=None):
        """if axis is None, scale all axes, otherwise if it is 'x' or 'y' scale that axis"""
        suffix=""
        if axis is not None:
            suffix=axis+"axes"
        
        s=self._grace() #dereference the weak ref
        s.write("with g%d; autoscale %s" % (self.gID, suffix) )

    def redraw(self, *args, **kwargs):
        """pass through to our GraceGraph instance"""
        self.grace().redraw(*args, **kwargs)
        
    def hold(self, onoff=None):
        """Turn on/off overplotting for this graph.
        
        Call as hold() to toggle, hold(1) to turn on, or hold(0) to turn off.
        Returns the previous hold setting.
        """
        lastVal = self._hold
        if onoff is None:
            self._hold = not self._hold
            return lastVal
        if onoff not in [0, 1]:
            raise RuntimeError, "Valid arguments to hold() are 0 or 1."
        self._hold = onoff
        return lastVal
    
    def title(self,string=None,font=None,size=None,color=None):
        """Sets the graph title"""
        send=self.grace()._send
        if string is not None:
            send('with g%d; title "%s"'% (self.gID, string))
        if font is not None:
            send('title font %d' % font)
        if size is not None:
            send('title size %f' % size)
        if color is not None:
            send('title color %d' % color)
        
    def subtitle(self,string=None,font=None,size=None,color=None):
        """Sets the graph subtitle"""
        send=self.grace()._send
        if string is not None:
            send('with g%d; subtitle "%s"'% (self.gID, string))
        if font is not None:
            send('subtitle font %d' % font)
        if size is not None:
            send('subtitle size %f' % size)
        if color is not None:
            send('subtitle color %d' % color)
    
    def gen_axis(self, axis_prefix, ax_min=None, ax_max=None, 
        scale=None, invert=None,
        offset=None, label=None, tick=None, bar=None, autotick=True):
        """general axis handler.  'scale' should be one of 'normal', 'logarithmic', or 'reciprocal'.
        Other parameters should be class entities for the appropriate object, such as label for 'label', or Tick for 'tick'
        """
        axname=axis_prefix+"axis"
        axname2=axis_prefix+"axes"
        
        #collect all commands into a list and then send them, 
        #to make sure it is atomic with respect to the 'with gn' statement
        commands=["with g%d" % self.gID]
        
        if ax_min is not None:
            commands.append('world %smin %g' % (axis_prefix, ax_min))
        if ax_max is not None:
            commands.append('world %smax %g' % (axis_prefix, ax_max))
        if scale is not None:
            commands.append('%s scale %s' % (axname2, scale))
        if invert is not None:
            commands.append('%s invert %s' % (axname2, invert))
        if offset is not None:
            commands.append('%s offset %g, %g' % (axname, offset))
            
        if label is not None:
            if type(label) is str:
                label=Label(label) #shortcut for simple string labels
            commands += label.output(axname)
                                
        if tick is not None:
            commands += tick.output(axname)
        elif autotick:
            commands.append('autoticks')
            
        if bar is not None:
            commands += bar.output(axname)
                
        self.grace().send_commands(*tuple(commands))
        
    def xaxis(self,xmin=None,xmax=None, **kwargs):
        """ Set x axis properties. see description of parameters in gen_axis()"""
        
        if xmin is not None:
            self.world_xmin=xmin
        if xmax is not None:
            self.world_xmax=xmax
         
        self.gen_axis('x', ax_min=xmin, ax_max=xmax, **kwargs)

    def yaxis(self,ymin=None,ymax=None, **kwargs):
        """ Set y axis properties. see description of parameters in gen_axis()"""
         
        if ymin is not None:
            self.world_ymin=ymin
        if ymax is not None:
            self.world_ymax=ymax
         
        self.gen_axis('y', ax_min=ymin, ax_max=ymax, **kwargs)
        
    def xlimit(self, lower=None, upper=None):
        """Convenience function to set the lower and/or upper bounds of the x-axis."""
        self.xaxis(xmin=lower,xmax=upper)

    def ylimit(self, lower=None, upper=None):
        """Convenience function to set the lower and/or upper bounds of the y-axis."""
        self.yaxis(ymin=lower,ymax=upper)

    def xlabel(self,label):
        """Convenience function to set the xaxis label"""
        self.gen_axis('x', label=label, autotick=False)
        
    def ylabel(self,label):
        """Convenience function to set the yaxis label"""
        self.gen_axis('y', label=label, autotick=False)
        
    def kill(self):
        """Kill the plot"""
        send=self.grace()._send
        send('kill g%d' % self.gID)
        send('g%d on' % self.gID)
        self.grace().redraw()
        self.nSets = 0
        self._hold = 0

    def clear(self):
        """Erase all lines from the plot and set hold to 0"""
        send=self.grace()._send
        for i in range(self.nSets):
            send('kill g%d.s%d' % (self.gID, i))
        self.grace().redraw()
        self.nSets=0
        self._hold=0

    def legend(self, strings=None, x=None,y=None,
               boxcolor=None,boxpattern=None,boxlinewidth=None,
               boxlinestyle=None,boxfillcolor=None,boxfillpattern=None,
               font=None,charsize=None,
               color=None,length=None,vgap=None,hgap=None,invert=None, world_coords=True):
        """Sets up the legend
        x and y are the position of the upper left corner
        boxcolor is the color of the legend box lines
        boxpattern is the pattern of the legend box lines
        boxlinewidth is the thickness of the line
        boxlinestyle
        boxfillcolor
        boxfillpattern
        font is the font used in the legend
        charsize controls the size of the characters
        length controls the length of the box must be an integer
        vgap controls the vertical space between entries, can be a float
        hgap controls horizontal spacing in the box can be a float
        invert is True or False, controls the order of entries, either in the order they are entered, or the opposite.
        """
        
        #collect all commands associated with the 'with' statement to assure atomicity
        commands=['with g%d; legend on' % self.gID]
        
        if world_coords and x is not None and y is not None:
            commands.append('legend loctype world')
        else:
            commands.append('legend loctype view')
            if x is None:
                x, yy=self.grace().aspect_scale(0.75, 0.0)
            if y is None:
                xx, y=self.grace().aspect_scale(0., 0.8)
                
        if strings is None:
            strings=self.legend_strings
        for i in range(len(strings)):
            commands.append( ('g%d.s%d legend "' % (self.gID, i)) + strings[i] + '"' )

        if x is not None and y is not None:
            commands.append('legend %f, %f' % (x,y))
        if boxcolor is not None:
            commands.append('legend box color %d' % boxcolor)
        if boxpattern is not None:
            commands.append('legend box pattern %d' % boxpattern)
        if boxlinewidth is not None:
            commands.append('legend box linewidth %f' % boxlinewidth)
        if boxlinestyle is not None:
            commands.append('legend box linestyle %d' % boxlinestyle)
        if boxfillcolor is not None:
            commands.append('legend box fill color %d' % boxfillcolor)
        if boxfillpattern is not None:
            commands.append('legend box fill pattern %d' % boxfillpattern)
        if font is not None:
            commands.append('legend font %d' % font)
        if charsize is not None:
            commands.append('legend char size %f' %charsize)
        if color is not None:
            commands.append('legend color %d' % color)
        if length is not None:
             commands.append('legend length %d' % length)
        if vgap is not None:
            commands.append('legend vgap %d' % vgap)
        if hgap is not None:
            commands.append('legend hgap %d' % hgap)
        if invert:
            commands.append('legend invert %s' % invert)
        
        self.grace().send_commands(*tuple(commands))
        
        self.grace().redraw()

    def frame(self,type=None,linestyle=None,linewidth=None,
              color=None,pattern=None,
              backgroundcolor=None,backgroundpattern=None):
        """
        type= closed,halfopen,breaktop,breakbottom,breakleft,breakright
        linestyle
        linewidth
        color
        pattern
        backgroundcolor
        backgroundpattern
        """
        send=self.grace()._send
        if type is not None:
            send('frame type %d' % type)
        if linestyle is not None:
            send('frame linestyle %d' % linestyle)
        if linewidth is not None:
            send('frame linewidth %d' % linewidth)
        if color is not None:
            send('frame color %d' % color)
        if backgroundcolor is not None:
            send('frame background color %d' % backgroundcolor)
            send('frame background pattern %d' % solid)
        if backgroundpattern is not None:
            send('frame background pattern %d' % backgroundpattern)

    def plot(self, DataSets, autoscale=True, internal_autoscale=False, redraw=True):
        """
        plot Data instances, see Data class
        currently only Data objects are supported.
        """
         
        send=self.grace()._send
        
        if isinstance(DataSets, Data):
            DataSets=[DataSets]
        
        self.datasets=DataSets
        
        if len(DataSets)>1:
            self.hold()

        legend=[]
        count=0
        for dataset in DataSets:
            send("\n".join(dataset.output(self,count)))

            legend.append(dataset.legend)
            count=count+1
       
        self.nSets=len(DataSets)
      
        if len(legend)>0:
            for i in range(len(legend)):
                if legend[i] is None:
                    legend[i]=''
        
        self.legend_strings=legend
        
        if internal_autoscale:
            ### Do these for every type of dataset
            #these lines are necessary so the variables get set.
            # it is my own version of autoscaling, it adds 10%
            # to the borders
            percent=0.10

            self.world_xmax=self.world_xmax+percent*(self.world_xmax-self.world_xmin)
            self.world_xmin=self.world_xmin-percent*(self.world_xmax-self.world_xmin)
            self.world_ymax=self.world_ymax+percent*(self.world_ymax-self.world_ymin)
            self.world_ymin=self.world_ymin-percent*(self.world_ymax-self.world_ymin)
            
            self.xaxis(xmin=self.world_xmin,xmax=self.world_xmax)
            self.yaxis(ymin=self.world_ymin,ymax=self.world_ymax)
            self.autotick()
            
        elif autoscale:
            send('autoscale')
        
        if redraw:
            self.grace().redraw()
    
    def update_data(self, set_index, new_x=[], new_y=[], new_dylist=[]):
        """efficiently update the data for a given data set.  set length, etc. must not change!"""
        outlist=self.datasets[set_index].output_differences(self, set_index, new_x=new_x, new_y=new_y, new_dylist=new_dylist)
        if outlist:
            self.grace()._send('\n'.join(outlist))
    
    def autotick(self):
        self.grace()._send('with g%d; autoticks' % self.gID)
        
    def plotxy(self,*xydatasets):
        # can take a shortcut, and use plotxy([x,y])
        datasets=[]
        for set in xydatasets:
            try:
                self.x=set[0]
                self.y=set[1]
            except:
                raise IndexError,'xy data is in wrong form'      
            datasets.append(Data(x=self.x,y=self.y))
            
        self.plot(datasets)
        
    def text(self,string=None, x=None,y=None,
                 color=None, rot=None, font=None,
                 just=None, charsize=None, world_coords=True):
        """ The coordinates are the cartesian coordinates for a single graph,
        they don't work yet for multi graphs."""
        send=self.grace()._send

        if world_coords:
            send('with g%d' % self.gID)
        
        send('with string')
        send('string on')
        if world_coords:
            send('string loctype world')
        else:
            send('string loctype view')
        
        if x is not None and y is not None:
            send('string %f, %f' % (x, y))
        if color is not None:
            send('string color %d' % color)
        if rot is not None:
            send('string rot %f' % rot)
        if font is not None:
            send('string font %d' % font)
        if just is not None:
            send('string just %d' % just)
        if charsize is not None:
            send('string char size %f' % charsize)
        if string is not None:
            send('string def "%s"' % string)

    def line(self,x1=None,y1=None,x2=None,y2=None,
                 linewidth=None,linestyle=None,
                 color=None,
                 arrow=None,arrowtype=None,arrowlength=None,arrowlayout=None, world_coords=True):
        """
        coordinates are the cartesian cooridinates for a single graph, they
        don't work yet for multi graphs.  arrow tells where the arrowhead is and
        is 0,1,2, or 3 for none, start, end, both ends arrowtype is for line
        (0), filled (1), or opaque (2), and only have an effect if the
        arrowlayout is not (1,1) arrowlayout must be a list of 2 numbers,
        arrowlayout=(1,1) the first number relates to d/L and the second is I/L
        the meaning of which is unclear, but they affect the arrow shape.
        """
        send=self.grace()._send

        if world_coords:
            send('with g%d' % self.gID)
        
        send('with line')
        send('line on')
        if world_coords:
            send('line loctype world')
        else:
            send('line loctype view')
        
        if None not in [x1, x2, y1, y2]:
            send('line %f, %f, %f,%f' %(x1, y1, x2, y2))
        if linewidth is not None:
            send('line linewidth %f' % linewidth)
        if linestyle is not None:
            send('line linestyle %d' % linestyle)
        if color is not None:
            send('line color %d' % color)
        if arrow is not None:
            send('line arrow %d' % arrow)
        if arrowtype is not None:
            send('line arrow type %d' % arrowtype)
        if arrowlength is not None:
            send('line arrow length %f' % arrowlength)
        if arrowlayout is not None:
            send('line arrow layout %f,%f' % arrowlayout)

        send('line def')
    
    def SetView(self,xmin=None,ymin=None,xmax=None,ymax=None, aspect_scaled=True):
        """
        this sets the viewport coords so they are available later
        for translating string and line coords.
        """
        send=self.grace()._send
         
        if aspect_scaled:
            xmin, ymin = self.grace().aspect_scale(xmin, ymin)
            xmax, ymax = self.grace().aspect_scale(xmax, ymax)
    
        self.view_xmin=xmin
        self.view_xmax=xmax
        self.view_ymin=ymin
        self.view_ymax=ymax
        
        send("g%d on; with g%d" % (self.gID, self.gID))
        
        if self.view_xmin is not None:
            send('view xmin %f' % xmin)
        if self.view_xmax is not None:
            send('view xmax %f' % xmax)
        if self.view_ymin is not None:
            send('view ymin %f' % ymin)
        if self.view_ymax is not None:
            send('view ymax %f' % ymax)

class Data:
    """simplest base class for all GracePlot data objects"""
    dataset_type_name='xy'
    #override this if the x values requires special formatting (unix seconds require explicit high precision, e.g.)
    #but mostly the python default str() which is automatically invoked by %s works pretty well
    x_format_string="%s"
    #override this if the y values require special formatting
    y_format_string="%s"
    
    def __init__(self, x=None, y=None, symbol=None,line=None,legend=None,comment=None, errorbar=None, pairs=None, dylist=[], **kwargs):
        if pairs is not None:
            try: #can these be sliced like a numpy array?
                x=pairs[:,0]
                y=pairs[:,1]
            except:
                x, y = map(None, *tuple(pairs)) #unzip zipped data pairs
            
        self.x=x

        self.y=y
        self.symbol=symbol
        self.line=line
        self.legend=legend
        self.comment=comment
        self.dylist=dylist
        self.errorbar=errorbar
        
    def output(self,graceGraph,count):
        """ No checking is done to make sure the datasets are
        consistent with each other, same number of x and y etc...
        Support of None values is only in the xy graph.
        """
        
        gID=graceGraph.gID
               
        x = self.x
        y = self.y
        #I had to implement this myself, because of the way that python treats None
        # apparently, None is less than everything.
        xmin=min(x)
        xmax=max(x)
        ymin=min(y)
        ymax=max(y)
        
        strlist=[]
        strlist.append('g%d.s%d on' %(gID,count))
        strlist.append('g%d.s%d type %s' % (gID,count,self.dataset_type_name))
        strlist.append('with g%d' % (gID, ))
        
        strlist += ['s%d point %s, %s' % (count, self.x_format_string % xi, self.y_format_string % yi) for (xi, yi) in zip(x,y) if xi is not None and yi is not None]
        
        #now, go through all the extra dx and dy values available and output them.
        strlist += ['s%d.y%d[%d]=%g' % (count, dyidx+1, idx, y) for (dyidx, dy) in enumerate(self.dylist) for (idx,y) in enumerate(dy) ]

        if self.symbol is not None:
            strlist += self.symbol.output('s%d' % (count) )
        if self.line is not None:
            strlist += self.line.output('s%d' % (count) )
        if self.errorbar is not None:
            strlist += self.errorbar.output('s%d' % (count))
        return strlist

    def output_differences(self,graceGraph,count, new_x, new_y, new_dylist):
        """output strings to modify already created datasets, issuing results only for changed items"""
        gID=graceGraph.gID
               
        x = self.x
        y = self.y
        
        strlist=['with g%d.s%d' % (gID, count)]
        if new_x:
            strlist += ['x[%d]=%s' % (idx, self.x_format_string % new_x[idx]) for idx in xrange(len(x)) if x[idx]!=new_x[idx]]
            self.x=tuple(new_x) #make a copy!
        if new_y:
            strlist += ['y[%d]=%s' % (idx, self.y_format_string % new_y[idx]) for idx in xrange(len(y)) if y[idx]!=new_y[idx]]
            self.y=tuple(new_y) #make a copy!
            
        #now, go through all the extra dx and dy values available and output them.
        if new_dylist:
            strlist += ['y%d[%d]=%g' % (dyidx+1, idx, dyl[idx]) 
                for (dyidx, (olddyl, dyl)) in enumerate(zip(self.dylist, new_dylist)) 
                for idx in xrange(len(dyl))
                if olddyl[idx] != dyl[idx]]
            self.dylist=[tuple(e) for e in new_dylist] #make copies!
        
        if len(strlist) == 1: return [] #if nothing changed, all we have is the 'with' statement, return empty
        else: return strlist

class DataXYDY(Data):
    """A data set with symmetrical error bars in the 'y' direction"""
    dataset_type_name='xydy'
    def __init__(self, x, y, dy, **kwargs):
        Data.__init__(self, x=x, y=y, dylist=[dy], **kwargs)
    
class DataXYDX(Data):
    """A data set with symmetrical error bars in the 'x' direction"""
    dataset_type_name='xydx'
    def __init__(self, x, y, dx, **kwargs):
        Data.__init__(self, x=x, y=y, dylist=[dx], **kwargs)

class DataXYDYDY(Data):
    """A data set with asymmetrical error bars in the 'y' direction"""
    dataset_type_name='xydydy'
    def __init__(self, x, y, dy_down, dy_up, **kwargs):
        Data.__init__(self, x=x, y=y, dylist=[dy_up, dy_down], **kwargs)

class DataXYDXDX(Data):
    """A data set with asymmetrical error bars in the 'x' direction"""
    dataset_type_name='xydxdx'
    def __init__(self, x, y, dx_left, dx_right, **kwargs):
        Data.__init__(self, x=x, y=y, dylist=[dx_right, dx_left], **kwargs)
        
class DataXYDXDY(Data):
    """A data set with symmetrical error bars in the 'x' and 'y' direction"""
    dataset_type_name='xydxdy'
    def __init__(self, x, y, dx, dy, **kwargs):
        Data.__init__(self, x=x, y=y, dylist=[dx, dy], **kwargs)

class DataXYDXDXDYDY(Data):
    """A data set with asymmetrical error bars in the 'x' and 'y' direction"""
    dataset_type_name='xydxdxdydy'
    def __init__(self, x, y, dx_left, dx_right, dy_down, dy_up, **kwargs):
        Data.__init__(self, x=x, y=y, dylist=[dx_right, dx_left, dy_up, dy_down], **kwargs)

class DataXYBoxWhisker(Data):
    """A data set with a box for an asymmetrical inner error in the 'y' direction 
        and an error bar (whisker) for the asymmetrical outer error bound. 
        The symbol properties set the color (etc.) of the box. The errorbar properties set the color (etc.) of the whisker"""
    dataset_type_name='xyboxplot'
    def __init__(self, x, y, whisker_down, box_down, whisker_up, box_up, **kwargs):
        Data.__init__(self, x=x, y=y, dylist=[box_down, box_up, whisker_down, whisker_up], **kwargs)

class DataBar(Data):
    dataset_type_name='bar'

class DataXYZ(Data):
    dataset_type_name='xyz'
    def __init__(self, x, y, z, **kwargs):
        Data.__init__(self, x=x, y=y, dylist=[z], **kwargs)

class Symbol:
    """
    type can be 'xy','bar'
    symbol:
    0 None
    1 circle
    2 square
    3 diamond
    4 triangle up
    5 triangle left
    6 triangle down
    7 triangle right
    8 +
    9 x
    10 *
    11 character
    
    size is self explanatory, it should be a number.
    
    pattern appears to be the pattern of the outline of the symbol, normally it will be 1, which is solid.
    it can be any integer from 0 to 8 i think.

    linewidth is the thickness of the outline of the symbol
    linestyle will normally be 1, for solid

    fillcolor is the color the symbol is filled with, by default it is the same as the outline color.

    fillpattern is the pattern of the fill, 1 is solid, 0 is None, there are about 20 choices.
    """
    
    def __init__(self,type=None,symbol=None,size=None,color=colors.black,
                 pattern=None,linewidth=None,linestyle=None,
                 filltype=None,fillrule=None,
                 fillcolor=None,fillpattern=None,
                 char=None,charfont=None,skip=None,
                 annotation=None,errorbar=None):
        self.type=type
        self.symbol=symbol
        self.size=size
        self.color=color
        self.pattern=pattern
        self.linewidth=linewidth
        self.linestyle=linestyle
        self.filltype=filltype
        self.fillrule=fillrule
        self.fillcolor=fillcolor
        self.fillpattern=fillpattern
        self.char=char
        self.charfont=charfont
        self.skip=skip
        self.annotation=annotation
        self.errorbar=errorbar

    def output(self,dataset):
        list=[]
        if self.type is not None:
            list.append(dataset+" type %s" % self.type)
        if self.symbol is not None:
            list.append(dataset+" symbol %d" % self.symbol)
        if self.size is not None:
            list.append(dataset+" symbol size %f" % self.size)
        if self.color is not None:
            list.append(dataset+" symbol color %d" % self.color)
        if self.pattern is not None:
            list.append(dataset+" symbol pattern %d" % self.pattern)
        if self.filltype is not None:
            list.append(dataset+" symbol fill type %d" % self.filltype)
        if self.fillrule is not None:
            list.append(dataset+" symbol fill rule %d" % self.fillrule)
        if self.fillcolor is not None:
            list.append(dataset+" symbol fill color %d" % self.fillcolor)
            list.append(dataset+" symbol fill pattern 1")
        if self.fillpattern is not None:
            list.append(dataset+" symbol fill pattern %d" % self.fillpattern)
        if self.linewidth is not None:
            list.append(dataset+" symbol linewidth %d" % self.linewidth)
        if self.linestyle is not None:
            list.append(dataset+" symbol linestyle %d" % self.linestyle)
        if self.char is not None:
            list.append(dataset+" symbol char %d" % self.char)
        if self.charfont is not None:
            list.append(dataset+" symbol char font %d" % self.charfont)
        if self.skip is not None:
            list.append(dataset+" symbol skip %d" % self.skip)

        if self.annotation is not None:
            list=list+ self.annotation.output(dataset)
                
        if self.errorbar is not None:
            list=list+ self.errorbar.output(dataset)
                
                
        return list
class Line:
    """
    Best guesses for acceptable values:
    type will normally be set to 1
    
    style:
    1 is normal
    2 is dotted
    3 is dashed
    4 is long dashed
    5 is dot-dashed

    width:
    goes from 1 to 6 in increasing thickness

    """
    
    def __init__(self,type=None,linestyle=None,linewidth=None,color=None,pattern=None,
                 baselinetype=None, baseline=None,dropline=None):
        
        self.type=type
        self.linestyle=linestyle
        self.linewidth=linewidth
        self.color=color
        self.pattern=pattern
        self.baseline=baseline
        self.baselinetype=baselinetype
        self.dropline=dropline

    def output(self,dataset):
        list=[]
        if self.type is not None:
            list.append(dataset+" line type %s" % self.type)
        if self.linestyle is not None:
            list.append(dataset+" line linestyle %s" % self.linestyle)
        if self.linewidth is not None:
            list.append(dataset+" line linewidth %s" % self.linewidth)
        if self.color is not None:
            list.append(dataset+" line color %s" % self.color)
        if self.pattern is not None:
            list.append(dataset+" line pattern %s" % self.pattern)
        if self.baseline is not None:
            list.append(dataset+" baseline %s" % self.baseline)
        if self.baselinetype is not None:
            list.append(dataset+" baseline type %d" % self.baselinetype)
        if self.dropline is not None:
            list.append(dataset+" dropline %s" % self.dropline)
        return list

class Label:
    """
    Used for labels of the x-axis and y-axis
    """
    def __init__(self,string=None,
                 layout=None,place=None,
                 charsize=None, font=None,
                 color=None,axis=None,):
        self.axis=axis
        self.label=string
        self.layout=layout
        self.place=place
        self.charsize=charsize
        self.font=font
        self.color=color
        self.place=place

    def output(self,axis):
        list=[]
        if self.label is not None:
            list.append(axis+' label "%s"' % self.label)
        if self.layout is not None:
            list.append(axis+' label layout %s' % self.layout)
        if self.place is not None:
            list.append(axis+' label place %s' % self.place)
        if self.charsize is not None:
            list.append(axis+' label char size %f' % self.charsize)
        if self.font is not None:
            list.append(axis+' label font %d' % self.font)
        if self.color is not None:
            list.append(axis+' label color %d' % self.color)
        if self.place is not None:
            list.append(axis+' label place %s' % self.place)
        return list
    
class Bar:
    """
    this class controls the x and y bars in the frame apparently
    usually it is off
    onoff is 'on' or 'off'
    the rest are like everything else
    """
    def __init__(self,axis=None,onoff=True,color=None,linestyle=None,linewidth=None):
        self.axis=axis
        self.onoff=on_off(onoff)
        self.color=color
        self.linestyle=linestyle
        self.linewidth=linewidth
    def output(self,axis):
        list=[]
        list.append(axis+' bar %s' % self.onoff)
        if self.color is not None:
            list.append(axis+' bar color %d' % self.color)
        if self.linestyle is not None:
            list.append(axis+' bar linestyle %d' % self.linestyle)
        if self.linewidth is not None:
            list.append(axis+' bar linewidth %f' % self.linewidth)
        return list
class Tick:
    """
    Controls appearence of ticks on an axis.
    
    onoff is either 'on' or 'off'
    major is the space between ticks?
    minorticks is the number of minorticks between major ticks?
    inout determines if they point 'in' or 'out' or 'both'
    majorsize determines how long the major ticks are
    majorlinewidth is how thick the major ticks are
    majorlinestyle is controls the linestle of the ticks and major gridlines
    majorgrid turns the major grid lines 'on' or 'off'
    minorcolor is the color of the minor tick lines
    minorlinewidth
    minorlinestyle controls the linestle of the ticks and minor gridlines
    minorgrid turns the minor gridlines on
    minorsize is the lengthe of the minor gridlines
    op is? it is usually set to 'both'
    type is ? it is usually set to 'auto'
    default is ? a number
    """
    def __init__(self,axis=None,onoff=True,major=None,minorticks=None,inout=None,
                 majorsize=None,majorcolor=None,majorlinewidth=None,majorlinestyle=None,
                 majorgrid=None,minorcolor=None,minorlinewidth=None,minorlinestyle=None,
                 minorgrid=None,minorsize=None,op=None,type=None,default=None,TickLabel=None):
        self.onoff=on_off(onoff)
        self.major=major
        self.minorticks=minorticks
        self.inout=inout
        self.majorsize=majorsize
        self.majorcolor=majorcolor
        self.majorlinewidth=majorlinewidth
        self.majorlinestyle=majorlinestyle
        self.majorgrid = majorgrid
        self.minorcolor=minorcolor
        self.minorlinewidth=minorlinewidth
        self.minorlinestyle=minorlinestyle
        self.minorgrid=minorgrid
        self.minorsize=minorsize
        self.op=op
        self.type=type
        self.default=default
        self.TickLabel=TickLabel

    def output(self,axis):
        list=[]
        list.append(axis+' tick %s' % self.onoff)
        if self.major is not None:
            list.append(axis+' tick major %g' % self.major)
        if self.minorticks is not None:
            list.append(axis+' tick minor ticks %d' % self.minorticks)
        if self.inout is not None:
            list.append(axis+' tick %s' % self.inout)
        if self.majorsize is not None:
            list.append(axis+' tick major size %f' % self.majorsize)
        if self.majorcolor is not None:
            list.append(axis+' tick major color %d' % self.majorcolor)
        if self.majorlinewidth is not None:
            list.append(axis+' tick major linewidth %f' % self.majorlinewidth)
        if self.majorlinestyle is not None:
            list.append(axis+' tick major linestyle %d' % self.majorlinestyle)
        if self.majorgrid is not None:
            list.append(axis+' tick major grid %s' % self.majorgrid)
        if self.minorcolor is not None:
            list.append(axis+' tick minor color %d' % self.minorcolor)
        if self.minorlinewidth is not None:
            list.append(axis+' tick minor linewidth %f' % self.minorlinewidth)
        if self.minorlinestyle is not None:
            list.append(axis+' tick minor linestyle %d' % self.minorlinestyle)
        if self.minorgrid is not None:
            list.append(axis+' tick minor grid %s' % self.minorgrid)
        if self.minorsize is not None:
            list.append(axis+' tick minor size %f' % self.minorsize)
        if self.op is not None:
            list.append(axis+' tick op %s' % self.op)
        if self.type is not None:
            list.append(axis+' tick type %s' % self.type)
        if self.default is not None:
            list.append(axis+' tick default %s' % self.default)
        if self.TickLabel is not None:
            for i in self.TickLabel.output(axis):
                list.append(i)

        return list
            

class TickLabel:
    def __init__(self,axis=None,onoff=True,type=None,prec=None,format=None,append=None,prepend=None,
                 angle=None,placeon=None,skip=None,stagger=None,op=None,
                 sign=None,starttype=None,start=None,stoptype=None,stop=None,
                 charsize=None,font=None,color=None):
        """
        
        type is ? it is set to 'auto'
        prec is ?
        format is a string ,'decimal' is default
        append is a string that is added to the end of the label
        prepend is a string added to the beginning of the label
        angle is an integer with degrees? of rotation
        placeon is a string, 'ticks'
        skip is an integer which skips some labels somehow
        stagger is an integer that staggers the labels somehow
        op is 'bottom' for x-axis, 'left' for y-axis
        sign is a string 'normal'
        starttype is a string 'auto'
        start is a float don;t know what it does
        stoptype is a string 'auto'
        stop is a float purpose?
        charsize is a float for character size
        font is an integer for the font
        color is an integer for the color
        """
        self.onoff=on_off(onoff)
        self.type=type
        self.prec=prec
        self.format=format
        self.append=append
        self.prepend=prepend
        self.angle=angle
        self.placeon=placeon
        self.skip=skip
        self.stagger=stagger
        self.op=op
        self.sign=sign
        self.starttype=starttype
        self.start=start
        self.stoptype=stoptype
        self.stop=stop
        self.charsize=charsize
        self.font=font
        self.color=color

    def output(self,axis):
        list=[]
        list.append(axis+' ticklabel %s'% self.onoff)
        if self.type is not None:
            list.append(axis+' ticklabel type %s' % self.type)
        if self.prec is not None:
            list.append(axis+' ticklabel prec %d' % self.prec)
        if self.format is not None:
            list.append(axis+' ticklabel format %s' % self.format)
        if self.append is not None:
            list.append(axis+' ticklabel append "%s"' % self.append)            
        if self.prepend is not None:
            list.append(axis+' ticklabel prepend "%s"' % self.prepend)
        if self.angle is not None:
            list.append(axis+' ticklabel angle %d' % self.angle)
        if self.placeon is not None:
            list.append(axis+' ticklabel place on %s' % self.placeon)
        if self.skip is not None:
            list.append(axis+' ticklabel skip %d' % self.skip)
        if self.stagger is not None:
            list.append(axis+' ticklabel stagger %d' % self.stagger)
        if self.op is not None:
            list.append(axis+' ticklabel op %s' % self.op)
        if self.sign is not None:
            list.append(axis+' ticklabel sign %s' % self.sign)
        if self.starttype is not None:
            list.append(axis+' ticklabel start type %s' % self.starttype)
        if self.start is not None:
            list.append(axis+' ticklabel start %f' % self.start)
        if self.stoptype is not None:
            list.append(axis+' ticklabel stop type %s' % self.stoptype)
        if self.stop is not None:
            list.append(axis+' ticklabel stop %f' % self.stop)
        if self.charsize is not None:
            list.append(axis+' ticklabel char size %f' % self.charsize)
        if self.font is not None:
            list.append(axis+' ticklabel font %d' % self.font)
        if self.color is not None:
            list.append(axis+' ticklabel color %d' % self.color)

        return list

class Annotation:
    def __init__(self,onoff=True,type=None,charsize=None,font=None,
                 color=None,rot=None,format=None,prec=None,prepend=None,
                 append=None,offset=None):
        """
        controls annotation
        onoff is 'on' or 'off', on by default, why else would you make one?
        type is a number? 2

        format is a string, 'general','exponential','decimal','power','scientific','engineering'

        offset must be a tuple
        """
        self.onoff=on_off(onoff)
        self.type=type
        self.charsize=charsize
        self.font=font
        self.color=color
        self.rot=rot
        self.format=format
        self.prec=prec
        self.prepend=prepend
        self.append=append
        self.offset=offset

    def output(self,dataset):
        list=[]
        list.append(dataset+' avalue %s' % self.onoff)
        if self.type is not None:
            list.append(dataset+' avalue type %d' % self.type)
        if self.charsize is not None:
            list.append(dataset+' avalue char size %f' % self.charsize)
        if self.font is not None:
            list.append(dataset+' avalue font %d' % self.font)
        if self.color is not None:
            list.append(dataset+' avalue color %d' % self.color)
        if self.rot is not None:
            list.append(dataset+' avalue rot %d' % self.rot)
        if self.format is not None:
            list.append(dataset+' avalue format %s' % self.format)
        if self.prec is not None:
            list.append(dataset+' avalue prec %d' % self.prec)
        if self.prepend is not None:
            list.append(dataset+' avalue prepend "%s"' % self.prepend)
        if self.append is not None:
            list.append(dataset+' avalue append "%s"' % self.append)
        if self.offset is not None:
            list.append(dataset+' avalue offset %f , %f' %self.offset)

        return list
class Errorbar:
    """
    onoff turns the error bars on or off, by default if you make an errorbar, they are on.
    place 'normal'
    color
    pattern
    linewidht
    linestyle
    riserlinewidth risers are the lines from the symbol to the end
    riserlinestyle
    riserclip set to on or off, determines if an arrow is drawn for error bars offscale
    risercliplength
    """
    def __init__(self,onoff=True,place=None, color=None, pattern=None,size=None,
                 linewidth=None, linestyle=None, riserlinewidth=None,riserlinestyle=None,
                 riserclip=None,risercliplength=None):
        self.onoff=on_off(onoff)
        self.place=place
        self.color=color
        self.pattern=pattern
        self.size=size
        self.linewidth=linewidth
        self.linestyle=linestyle
        self.riserlinewidth=riserlinewidth
        self.riserlinestyle=riserlinestyle
        self.riserclip=riserclip
        self.risercliplength=risercliplength

    def output(self,symbol):
        list=[]
        list.append('%s errorbar %s' % (symbol,self.onoff))
        if self.place is not None:
            list.append('%s errorbar place %s' %(symbol,self.place))
        if self.color is not None:
            list.append('%s errorbar color %d' %(symbol,self.color))
        if self.pattern is not None:
            list.append('%s errorbar pattern %d' %(symbol,self.pattern))
        if self.size is not None:
            list.append('%s errorbar size %f' %(symbol,self.size))
        if self.linewidth is not None:
            list.append('%s errorbar linewidth %f' %(symbol,self.linewidth))
        if self.linestyle is not None:
            list.append('%s errorbar linestyle %d' %(symbol,self.linestyle))
        if self.riserlinewidth is not None:
            list.append('%s errorbar riser linewidth %f' %(symbol,self.riserlinewidth))
        if self.riserlinestyle is not None:
            list.append('%s errorbar riser linestyle %d' %(symbol,self.riserlinestyle))
        if self.riserclip is not None:
            list.append('%s errorbar riser clip %s' %(symbol,self.riserclip))
        if self.risercliplength is not None:
            list.append('%s errorbar riser clip length %f' %(symbol,self.risercliplength))

        return list

if __name__=='__main__':
    import math
    a=GracePlot(width=8, height=6, auto_redraw=True)
    a.debug=False
    xvals=range(100)
    yvals=[math.sin(x*1.0) for x in xvals]
    y2vals=[math.cos(x*0.5) for x in xvals]
    a.assign_color(colors.yellow, (128, 128, 0), "yellow-green")
    a.assign_color(20, (64, 64, 0), "dark yellow-green")
    g=a[0]
    g.SetView(ymin=0.5, ymax=0.9)
    
    g.plot([
        Data(x=None, y=None, pairs=zip(xvals, yvals),
            line=Line(type=lines.none), symbol=Symbol(symbol=symbols.plus, color=colors.green4),
            errorbar=Errorbar(color=colors.green4), legend='hello'
        ), 
        DataXYDY(x=xvals, y=[0.8*math.cos(xx*0.3 + 10) for xx in xvals], dy=[yy/10 for yy in y2vals], 
            line=Line(linestyle=lines.dotted, linewidth=3), legend='goodbye'),
        DataXYDX(x=xvals, y=[0.9*math.cos(xx*0.4 + 2.63) for xx in xvals], dx=[0.5 for yy in y2vals], legend='42'),
        DataXYDXDY(x=xvals, y=[0.6*math.cos(xx*0.7 + 2.63) for xx in xvals], dx=[0.3 for yy in y2vals], dy=[yy/20 for yy in y2vals]),
        DataXYDXDXDYDY(x=xvals, y=[0.6*yy for yy in yvals], 
            dx_left=[0.25 for yy in y2vals], 
            dx_right=[0.5 for yy in y2vals], 
            dy_down=[yy/20 for yy in y2vals],
            dy_up=[yy/40 for yy in y2vals],
            legend='abracadabra'
            ),
        DataXYBoxWhisker(x=xvals, y=[y/2 for y in y2vals], 
            whisker_down=[yy/2-0.1 for yy in y2vals], 
            whisker_up=[yy/2+0.05 for yy in y2vals], 
            box_down=[yy/2-abs(yy/20) for yy in y2vals],
            box_up=[yy/2+abs(yy/40) for yy in y2vals],
            line=Line(color=colors.black, linestyle=lines.dashed, linewidth=3),
            symbol=Symbol(color=colors.red), errorbar=Errorbar(color=colors.red),
            legend='foo'
            )
        ])
    g.title("Unbelievably ugly plot!")
    g.legend()
        
    xvals=range(1024)
    y1vals=len(xvals)*[0]
    y2vals=len(xvals)*[0]
    g=a.new_graph(view_ymin=0.1, view_ymax=0.45)
    
    g.plot((DataXYDY(xvals,y1vals, y1vals), Data(xvals, y2vals)))
    g.xaxis(0,1024)
    g.yaxis(scale='logarithmic', ymin=0.5, ymax=1000, tick=Tick(major=10, minorticks=9))
    g.xlabel(Label("channel", charsize=2))
    g.ylabel(Label("counts", charsize=2))
    
    #a.debug=True

    import random
    for i in range(1000):
        for j in range(10):
            chan=int(math.floor(random.gauss(500,50)))
            if chan >=0 and chan < len(y1vals):
                y1vals[chan]+=1
            chan=int(math.floor(random.gauss(200,10)))
            if chan >=0 and chan < len(y2vals):
                y2vals[chan]+=1
            
        g.update_data(0, new_y=y1vals, new_dylist=[[math.sqrt(y) for y in y1vals]])
        g.update_data(1, new_y=y2vals)
        time.sleep(0.02)
        a.redraw(soon=True)
    

    
