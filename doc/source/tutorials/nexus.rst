NeXus data sinks in NICOS
=========================

Writing a `NeXus <https://www.nexusformat.org/>`_ file in NICOS is technically
quite easy.  If a :class:`~nicos_sinq.nexus.nexussink.NexusSink` device
is configured and added to the datasinks in the sysconfig dictionary, a valid
NeXus file will be written.

Example::

      sysconfig = dict(

         datasinks = [ ... , 'nxsink', ... ],

      )

      nxsink = device('nicos_sinq.nexus.nexussink.NexusSink',
         description = '...',
         templateclass = '...',

      ),

The most difficult part is to define the correct structure.  NICOS provides
a mechanism to achieve this.  For this purpose you must implement a template
provider class derived from
:class:`~nicos_sinq.nexus.nexussink.NexusTemplateProvider`.

Your specific template provider class has to implement the ``getTemplate`` method.

Example::

       from nicos_sinq.nexus.nexussink import NexusTemplateProvider

       class YourTemplateProvide(NexusTemplateProvider):

           def getTemplate(self):
               template = {}
               return template

where the ``getTemplate()`` method has to return a dictionary which describes the
desired NeXus file structure to the NexusSink.  In the example the dictionary
is empty, which would result in an empty NeXus file.

We want to show how to implement the NeXus template for the
`WONI <https://manual.nexusformat.org/applying-nexus.html>`_ instrument in
NICOS.  The template variable should be filled with the following content::

   template = {
       'NeXus_Version': 'nexusformat v0.5.3',
       'instrument': 'WONI',
       'owner': DeviceAttribute('WONI', 'responsible'),
       'entry:NXentry': {
           'data:NXdata': {
           },
           'WONI:NXinstrument': {
           },
           'monitor:NXmonitor': {
           },
           'sample:NXsample': {
           },
       },
   }


The example defines a few file level attributes (NeXus_version, instrument) and
a few NeXus groups.  A group is defined as a new dictionary with a syntax of:

   'groupname:NeXus class name': {}

For valid NeXus class names consult the NeXus documentation at
https://nexusformat.org

The :class:`~nicos_sinq.nexus.elements.DeviceAttribute` will be taken from the
`nicos_sinq.nexus.elements` module::

   from nicos_sinq.nexus.elements import DeviceAttribute

The parameters of the ``DeviceAttribute`` class are the *name* of our configured
instrument and its parameter *responsible*::

    WONI = device('nicos.devices.instrument.Instrument',
        responsible = 'R. Esponsible <r.responsible@nicos-controls.org>',
        # ...
    ),

The :class:`DeviceAttribute` will then transfer the `WONI.responsible` into
the NeXus file.

The monochromator can be added like this::

    'WONI:NXInstrument': {
        'monochromator:NXcrystal': {
            'wavelength': DeviceDataset('wavelength',
                                        units=NXAttribute('Angstroem', 'string')),
            'rotation_angle': DeviceDataset('mtt'),
            'd_spacing': DeviceAttribute('mono', 'dvalue'),
            'type': ConstDataset('Si', 'string'),

        }
    }

The classes :class:`~nicos_sinq.nexus.elements.DeviceDataset` and
:class:`~nicos_sinq.nexus.elements.ConstDataset` have to be imported first::

   from nicos_sinq.nexus.elements import ConstDataset, DeviceDataset

The parameters *wavelength*, *mtt*, and *mono* are configured NICOS devices.
*dvalue* is a parameter of the *mono* device definining the distance between
the crystal layers of the monochromator crystal.  The wavelength entry also
provides an example of how a data attribute is added to a data field.  In the
example this is the ``units`` attribute.  The syntax is::

   name = NXAttribute(value, type)

In the example the value of the units attribute is Angstroem, the type is a
string.

The ``ConstDataset`` is used to put a constant value (in our case it is a
string) into the NeXus file.  The ``DeviceDataset`` takes the value of a NICOS
device into NeXus.

The access to the detector values is done by the
:class:`~nicos_sinq.nexus.elements.DetectorDataset` and
:class:`~nicos_sinq.nexus.elements.ImageDataset` classes.

For the monitor value the access is set::

   'monitor:NXmonitor' {
       'integral': DetectorDataset('monitor', 'int32'),
   }

where the parameter 'monitor' of the DetectorDataset is the name of the
NICOS device ``monitor`` and the next parameter defines the data type of
the NeXus entry (in our case a 4 byte integer number).

To put image data into the NeXus file the ``ImageDataset`` is needed::

   'data:NXdata' {
       'data': ImageDataset(0, 0),
   }

The parameters of the ``ImageDataset`` define the number of the image device
and the number of the image in the dataset's result list.

Besides the shown NeXus elements there are some :ref:`others <nexus_elements>`

A number of data placeholder classes, like DeviceDataset, for the NexusSink
have been provided which should cover most use cases.  It can happen that the
provided placeholder do not suffice.  In that case there are two options:

* For simpler cases you derive a class from
  :class:`~nicos_sinq.nexus.elements.CalcData` and implement the necessary
  methods.

* If more control is need how NeXus data is written, derive a class from
  :class:`~nicos_sinq.nexus.elements.NexusElementBase` and implement your
  requirements.

For more details see the reference of these classes.

For more elaborate examples, search the ``nicos_sinq`` tree, for example
``nicos_sinq/sans/nexus`` or ``nicos_sinq/focus/nexus``.

NeXus data sink
---------------

.. module:: nicos_sinq.nexus.nexussink
.. autoclass:: NexusSink()

NeXus template
--------------

.. currentmodule:: nicos_sinq.nexus.nexussink
.. autoclass:: NexusTemplateProvider()
   :members: getTemplate

.. _nexus_elements:

NeXus elements
--------------

.. automodule:: nicos_sinq.nexus.elements
   :member-order: bysource
