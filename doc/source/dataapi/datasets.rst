.. _data_sets:

Data sets
=========

.. module:: nicos.core.data.dataset

.. autoclass:: finish_property

.. autoclass:: BaseDataset
   :member-order: bysource

.. autoclass:: PointDataset

   .. autoattribute:: settype
   .. autoattribute:: countertype

   .. automethod:: devvaluelist()
   .. automethod:: detvaluelist()
   .. automethod:: envvaluelist()
.. .. automethod:: valuestats()

.. autoclass:: ScanDataset

   .. autoattribute:: settype
   .. autoattribute:: countertype

.. .. automethod:: devvaluelists()
   .. automethod:: detvaluelists()
   .. automethod:: envvaluelists()
   .. automethod:: metainfo

.. autoclass:: SubscanDataset

   .. autoattribute:: settype
   .. autoattribute:: countertype

.. autoclass:: BlockDataset

   .. autoattribute:: settype
   .. autoattribute:: countertype

.. autoclass:: ScanData
   :members:
