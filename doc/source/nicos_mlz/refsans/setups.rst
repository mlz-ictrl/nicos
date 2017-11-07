===============================================
`REFSANS <http://www.mlz-garching.de/refsans>`_
===============================================

Instrument setups
=================

.. toctree::
    :maxdepth: 1
    :glob:

    setups/*
    setups/nok/*
    setups/elements/*

Service setups
==============

.. toctree::
    :maxdepth: 1
    :glob:

    setups/special/*

Parameter definition
====================

.. module:: nicos_mlz.refsans.params

.. function:: motoraddress

   Converter that accepts only valid motor block addresses for the Beckhoff
   PLC.

   Valid address must start with an offset 0x3020 or 0x4020 and must add a
   multiple of 10. The multiple is limited to 200 so the valid range
   goes from 0x20 to 0x7f0.
