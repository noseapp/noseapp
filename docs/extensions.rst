==========
Extensions
==========

You will can create extensions for noseapp as independent library. Usage redirect imports from noseapp.ext

Example::

  # from your lib
  from noseapp_my_ext import Extension
  # With redirect import
  from noseapp.ext.my_ext import Extension


This is realization from flask library.
