
Note: This is a copy take n from the original 
github repo: 
https://github.com/javiljoen/lttb.py

lttb.py
=======

Numpy implementation of Steinarsson’s *Largest-Triangle-Three-Buckets*
algorithm for downsampling time series–like data

Based on the original JavaScript code:

https://github.com/sveinn-steinarsson/flot-downsample

and:

Sveinn Steinarsson. 2013.  *Downsampling Time Series for Visual
Representation.* MSc thesis. University of Iceland.

A test data set is provided in ``tests/timeseries.csv``.
It was downloaded from http://flot.base.is/ and converted from JSON to CSV.


Usage
-----

.. code:: python

   import numpy as np
   import lttb
   data = np.array([range(100), np.random.random(100)]).T
   small_data = lttb.downsample(data, n_out=20)
   assert small_data.shape == (20, 2)

For example, here is the data set provided in ``tests`` downsampled to 100
points:

.. image:: tests/timeseries.png


Installation
------------

Download the source code and install the ``lttb`` package into your (virtual)
environment::

   git clone https://github.com/javiljoen/lttb.py.git
   pip install ./lttb.py


Requirements
^^^^^^^^^^^^

* Python 3
* Numpy


Licence: MIT
