Data sinks
==========

The :py:class:`~nicos.core.data.sink.DataSink` class is the configurable part
of a data sink whereas the :py:class:`~nicos.core.data.sink.DataSinkHandler`
class implements, how the data should be written.

.. module:: nicos.core.data.sink

.. autoclass:: DataSink
   :members:

.. autoclass:: DataSinkHandler

   .. automethod:: prepare
   .. automethod:: begin
   .. automethod:: putMetainfo
   .. automethod:: putValues
   .. automethod:: putResults
   .. automethod:: end
   .. automethod:: addSubset

.. autoclass:: DataFileBase

.. currentmodule:: nicos.core.data

.. autoclass:: DataFile

.. autoclass:: GzipFile
