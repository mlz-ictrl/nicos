Single Crystal Diffraction
==========================

This document describes the SINQ style single crystal diffraction support in NICOS.
This is based on the well proven ANSII-C routines from SICS ported to python.

Instrument Setup
------------------

Most single crystal diffractometers at SINQ support multiple diffraction geometries. Changing
the geometry can be achieved by loading the appropriate setup. For example, at MORPHEUS:

     AddSetup('euler')
     NewSetup()

will load the setup for the eulerian cradle. The command:

     ListSetups()

will show what is available. NICOS supports the following diffraction geometries:

- Eulerian cradle
- Normal beam geometry
- Triple axis using Marks Lumsdens UB-matrix calculus. This can be used both in elastic
  and inelastic mode

Diffractometer setups are mutually exclusive: thus you will have to unload an old setup with

     RemoveSetup('euler')

before being able to load another single crystal diffraction setup.


Parameters
------------

Single crystal diffraction is a parameter heavy business. The interesting parameters are
associated with the sample object and the diffractometer object. The diffractometer object
always has the name of the instrument. Thus, for example, at MORPHEUS the following two commands
will show all that is available:

     ListParams(Sample)
     ListParams(MORPHEUS)

The Sample object holds the cell parameters and the UB matrix, no surprises here. The only parameter
requiring explanation is *Sample.reflist*. This parameter holds the name of the default reflection list
to use with reflection list commands. Two reflection lists come preconfigured:


- *ublist* intended for peak search and UB matrix refinement
- *messlist* for reflections to be measured

More reflection lists can be configured easily on demand.

The diffractometer object holds some interesting parameters for the operation of the diffractometer.
All examples are for MORPHEUS, replace that with the name of your instrument as appropriate.
The first set are the centering parameters which will be used when centering reflections:

- *MORPHEUS.center_counter* The counter channel to be used for centering. Usually configured for
   you properly.
- *MORPHEUS.center_maxpts* The maximum number of points to consider for centering. This determines
  together with the center_steps the width of the search for a peak when centering.
- *MORPHEUS.center_steps* A list of step widths to use when centering reflections,
  one each for the relevant diffractometer angles.

Another interesting set of parameters controls measuring reflection lists:

- *MORPHEUS.scanmode* The scan mode to use for measuring reflections. Can be
  omega or t2t
- *MORPHEUS.scansteps* The number of steps to measure for each reflection.
- *MORPHEUS.scan_uvw* The parameters for calculating the scan width for each reflection
  from ``sqrt(u + v *tan Theta + w * tan² Theta)``.

For all parameters, the usual NICOS syntax for changing them apply. All of them are
cached and thus persist between NICOS invocations.

Reflection List Commands
-------------------------

Manipulating reflection lists needs to be frequently done in single crystal
diffraction. All reflection list commands take an reflist parameter. If this
parameter is missing, then the command is applied to the default reflection list
configured in *Sample.reflist*. Else the parameter must be the name of a
reflection list.

Each reflection is characterized by three tuples of information:

- reciprocal lattice coordinates, (h, k, l), example: (1, 0, 0)
- angle settings, (stt, om, chi, phi) or other as appropriate for the goniometer, example
  (12.2, 6.1, 66.77, 120.3)
- aux which is not yet really used

In the reflection manipulation commands (AddRef(), SetRef()) all tuples can be
given or only only the ones which are available or need to be changed. The others
can be None.

Now the commands:

    ListRef(reflist=None)

lists a reflection list.

    ClearRef(reflist=None)
removes all entries from a relfection list

    LoadRef(filename, reflist=None)

Loads a reflection list from filename. Filename should contain lines of the form:

    h k l stt om chi phi

The angles can be missing.

    SaveRef(filename, reflist=None, fmt=None)

Saves a reflection list to filename. The default is a very simple list format.
Other formats are supported:

- *fmt='rafin'* creates a reflection list in rafin format for
  UB matrix refinement
- *fmt='dirax'* creates a reflection list in the format for the
  indexing program dirax

    AddRef(hkl, angles, aux, reflist=None)

adds a reflection to a reflection list. hkl, angles, aux are all expected to
be tuples of floats. Or None when the information is not available.

    SetRef(idx, hkl, angles, aux, reflist=None)

modifies the reflection with the index idx in the reflection list.
hkl, angles or aux are all expected to be tuples of float or None. When None,
then the corresponding data for the reflection is left unchanged.

    DelRef(idx, reflist=None)

deletes the reflection with index idx from the reflection list.

Starting a new single crystal experiment
------------------------------------------

When starting a new single crystal experiment first fill in all the administrative
information, most importantly the proposal ID, in the NICOS GUI. Then:

    Sample.new({'name': 'F22O3', 'a': 7.7})

clears all crystallographic information and initialises the diffractometer. The statement
above is the minimum. The parameter for Sample.new() is a dictionary which can hold more
entries:

- *b*, *c* second and third lattice constant
- *alpha*, *beta*, *gamma* lattice angles, defaulted to 90 when not given
- *lattice* An alternative to give cell constants individually, expects a list of
   [a, b, c] as argument
- *angles* An alternative to give cell angles individually, expects a list of
   [alpha, beta, gamma] as argument
- *bravais* Bravias type of the sample
- *laue* The laue group of the sample

This also sets up an initial B matrix such that some crystallographic calculations
can work.

Driving in reciprocal space
-----------------------------
Once a UB matrix or at leat cell constants have been defined, it is possible
to drive the goniometer directly in reciprocal space.

The reciprocal indices h, k, l can be driven like any other device:

    maw(h, 2, k, 2)

NICOS supports a collective movement by using the diffractometer as a device:

    maw(MORPHEUS,(2,2,0))

This drives to reflection 2,2,0.


Finding reflections
---------------------

One way to find reflections for the determination of the UB matrix is manually. Just use
the normal NICOS scan commands for this.

With the cell constants properly set, the command:

    CalcAng((h, k, l))

will at least display the proper two theta and omega for the reflection.

Another helpful command may be

    Max(dev, step, counter, maxpts, **preset)

for example:

    Max(stt, .1, 'ctr1', 40, t=.1)

which finds a maximum for a peak with respect to the device given.
This implements a hill climbing algorithm.

NICOS also supports automatic reflection search. The process is that you need
to configure the search ranges and steps for each angle to be searched with the
command:

    SearchPar(key, min, max, step)

for example:

    SearchPar('stt', 10, 15, .2)

causes the search range for two theta to be between 10 and 15 degrees . .2 degree steps.
Configure the ranges for the other angles of the diffractometer in a similar way. The command:

    ShowSearchPar()

displays the current set of search parameters.

With:

    PeakSearch(reflist, threshold, **preset)

for example:

    PeakSearch(ublist, 100, t=.2)

the actual search for reflections is started. Be prepared to wait for some time
for this operation to complete. The threshold is a minimum count rate required in order
for a reflection to be considered.

The angular positions of reflections found can be refined further with the

    Center(idx,reflist=None, **preset)

for example:

    Center(5, t=.5)

command.


Indexing Reflections
----------------------

For simple indexing, there is the

    IndexTH(idx, reflist=None, hkllim=10)

command which suggests possible indices for the reflection with index idx in the
reflection list based on two theta. hkllim defines the range of miller indices to
consider.

For more complex indexing problems, save the reflection list with:

    SaveRef(filename, reflist=None, fmt='dirax')

and use the program dirax outside of NICOS in order to find indices.

When indices have been found assign them to reflections using:

    SetRef(idx, (h, k, l), None, None)


Calculating and refining UB
----------------------------

Once more then two reflections have been found and indexed a UB matrix
can be calculated with:

    CalcUB(idx1, idx2, replace=False)

idx1 and idx2 are the two reflection to use for UB matrix calculation in the
reflection list. The replace parameter determines if the default UB matrix is
to be replaced with the new calculated one.

The process then is to edit the reflection list and 10-20 additional strong reflections
to it. Take care that the reflections are well spaced in angles and observe the sample
from as many quadrants as possible. The angular positions of these reflections have to
be optimized with the command:

    CenterList(reflist, **preset)

for example:

    CenterList(t=.5)

This has to happen in two runs:

- The first run with an rather open collimation
- The second run with a closed collimation

Once centering has finished the reflection list can be saved with:

    SaveRef(filename, fmt='rafin')

Then use the program rafin outside of NICOS in order to refine the UB matrix.
The result can entered into NICOS through:

    Sample.ubmatrix=[ub11, ub12, ub13, ub21, ub22, ub23, ub31, ub32, ub33]


Reflection List Measurements
------------------------------

The bread and butter of single crystal diffraction is to measure many reflections and
determine or refine the crystal structure afterwards. The first thing needed for this is
a list of reflections to measure. NICOS can generate a suitable  list with:

    GenerateList(dmin, dmax, reflist)

with dmin and dmax denoting the limits in d for the reflections. When the sample parameters
have been properly set, systematic extinctions and symmetrical equivalents will be filtered
properly.

Once a list has been generated, it can be measured with:

    Measure(scanmode=None, skip=0, reflist=None, **preset)

for example:

    Measure(t=.5)

The parameters are:

- scanmode: either omega or t2t for an omega scan or an omega two theta scan repectivly. When not given,
  the default scan mode defined as a parameter to Sample is used
- skip allows the starr processing the reflection list a t a certain index. Comes in usefule when
  you need to continue a reflection list scan.
- reflist is the reflection list to use
- Preset is the count preset.

The scan step and number of scan points for each reflection is calculated from the
parameters at the instrument object.

NICOS also supports measuring incommensurate structures. To this purpose, there is the command:

    GenerateSuper(targetlist, vector, srclist)

for example:

    GenerateSuper(superlist, (.3, 0,0))

which generates a list of super structure reflection for a source list by applying
vector to it. This can be called multiple times. Almost always you wish to measure super
structure reflections froma separate list as you will require different data collection
parameters.

Miscellaneous commands
-----------------------

    CalcAng((h,k,l))

calculates the angles for a reflection without driving to it.

    CalcPos((stt, om, chi, phi))

calculates the reciprocal space position form the angles provided.

    ShowAng()

shows the position of all diffractometer motors.

    integrate(*columns)

is to be used after a scan and calculates the integrated intensity
of a peak in the scan.

    ScanOmega((h, k, l), **preset)

performs a omega scan of the reflection (h, k, l)

    ScanT2T((h, k, l), **preset)

performs an omega two theta scan of the reflection (h, k, l)

