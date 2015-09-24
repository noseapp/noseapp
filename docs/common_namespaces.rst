Namespaces
==========

Namespaces is building so


.. code-block:: python

    import noseapp


    app = noseapp.NoseApp('app_name')

    print(app.name)
    'app_name'

    suite = noseapp.Suite('suite_name')

    print(suite.name)
    'suite_name'

    app.register_suite(suite)

    print(suite.name)
    'app_name.suite_name'


    @suite.register
    class TestCase(noseapp.TestCase):

        def test(self):
            pass


    test = TestCase('test')

    print(repr(test))
    'test (app_name.suite_name:TestCase)'
