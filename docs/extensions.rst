==========
Extensions
==========

You will can create extension for noseapp and to use him as independent library. You get a chance for use redirect import from noseapp.ext.
Thanks mitsuhiko for good idea and realization :) (This is realization from flask library.)

Example::

  # from your lib
  from noseapp_my_ext import Extension
  # With redirect import
  from noseapp.ext.my_ext import Extension
