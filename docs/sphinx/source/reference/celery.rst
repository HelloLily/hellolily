##################################
Running and debugging Celery tasks
##################################

Celery is a distributed task queue in Python that's being used to perform several
queued tasks from within |project|. These are mostly tasking like syncing email
and updating ElasticSearch indexes.


=======
Running
=======

.. code:: bash

    celery worker -B --app=lily.celery --loglevel=info -Q celery,queue1,queue2,queue3 -n beat.%h -c 1


=========
Debugging
=========
Code that's being executed by a Celery worker can be PDB'ed with RDB. Add the following
to your Celery code:

.. code:: bash

    from celery.contrib import rdb
    rdb.set_trace()

You should see a notification in the Celery console when a worker stumbles upon the rbd trace. At that point you can use
telnet to login to the remote PDB session like:

.. code:: bash

    telnet localhost 6902
    help
