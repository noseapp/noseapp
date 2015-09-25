Extensions
==========


Redirect imports
----------------

You can create extension for noseapp and to use him as independent library. You get a chance for use redirect import from noseapp.ext.
Thanks mitsuhiko for good idea and realization :) (This is realization from flask library.)

.. code-block:: python

    # from your lib
    from noseapp_my_ext import Extension
    # With redirect import
    from noseapp.ext.my_ext import Extension


Creation and installation standard
----------------------------------

.. code-block:: python

    from noseapp.core import ExtensionInstaller


    class MyExtension(object):

        name = 'ext_name'

        config_key = 'MY_EXTENSION_EX'

        def __init__(self, config_data):
            self.config_data = config_data

        @classmethod
        def install(cls, app):
            installer = ExtensionInstaller(
                cls,
                (app.config.get(self.config_key, {}), ),
                {},
            )
            app.shared_extension(cls=installer)
            return installer
