Application
===========


Base application class
----------------------

.. autoclass:: noseapp.app.base.NoseApp
    :members:
    :exclude-members: __dict__, __weakref__, class_factory, collector_class, config_class
    :private-members:
    :special-members:


Config
------

.. autoclass:: noseapp.app.config.Config
    :members:
    :exclude-members: __dict__, __weakref__
    :private-members:
    :special-members:

.. autofunction:: noseapp.app.config.get_config_path_by_env


Context
-------

.. autofunction:: noseapp.app.context.merge_context


.. autoclass:: noseapp.app.context.AppContext
    :members:
    :exclude-members: __dict__, __weakref__
    :private-members:
    :special-members:
