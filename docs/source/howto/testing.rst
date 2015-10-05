=========================
Running and writing tests
=========================

Good code needs tests. A project like |project| simply can't afford to incorporate new code
that doesn't come with its own tests.

Tests provide some necessary minimum confidence: they can show the code will
behave as it expected, and help identify what's going wrong if something breaks
it. We certainly do want your contributions and fixes, but we need your tests with
them too. Otherwise, we'd be compromising our codebase.

So, you are going to have to include tests if you want to contribute. However,
writing tests is not particularly difficult, and there are plenty of examples in
the code to help you.


*************
Running tests
*************

The testrunner accepts parameters to specify which tests you want to run:


Run specific tests by their stored id
-------------------------------------
.. code:: bash

    ./manage.py test --with-id
    # run test #5 and 6 as assigned by --with-id
    ./manage.py test --with-id 5 6


Run tests by directory, filename, class or function
---------------------------------------------------
.. code:: bash

    # all contacts tests.
    ./manage.py test ./lily/contacts/api/tests.py
    # Run the test_create_object_with_relations test .
    ./manage.py test ./lily/contacts/api/tests.py:ContactTests:UnicodeTestCase.test_create_object_with_relations


Run tests that are tagged by category
-------------------------------------
.. code:: bash

    docker-compose run web ./manage test --attr=api
    docker-compose run web ./manage test --attr=processes


*************
Writing tests
*************

The directory structure for test-related material for each Django app is:

.. code:: bash

    ./app/factories.py  <= contains the factory boy factories for this app's models
    ./app/tests/test_models.py  <= model functions are tested here (unit tests)
    ./app/tests/test_utils.py  <= helper functions from utils.py are tested here (unit tests)
    ./app/tests/test_views.py  <= contains ghostrunner tests.
    ./app/tests/tests.py  <= generic tests that don't fit anywhere else


Always inherit from a |project| testcases class. Modify the |project| testcase class if you need additional functionality.
The first line of the test string should be short, concise and descriptive. Use the minimal amount of words to describe the test.
Use the descriptive paragraph beneath the first docstring line to explain the test in detail.

What to test is an ungoing debate. In theory you should test as much as possible, but it's not practical to have tests
for all changes, since it may take large amounts of time to test every detail. Here are some general guidelines in what
situations testing may be useful:

#. User processes are ideal to write functional tests for. These tests are also a nice documentation source on how the platform is used.

.. note::

    * Override settings.DEBUG = True in your testcase to force DEBUG information.
    * Check for settings.TESTING in your maincode if you need test-specific code.
    * Exclude tests from running on production by checking for settings.PRODUCTION


****************
Performance tips
****************

* It's possible to reuse the testing database on the next run by executing tests with:

.. code:: bash

    REUSE_DB=1 ./manage test


* Django nose supports running the testsuite with multiple processes. This is especially useful for functional tests.

.. code:: bash

    ./manage test --attr=views --processes=3 --process-timeout=600
