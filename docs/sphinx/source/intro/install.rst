.. _intro/install:

####################
Installing |project|
####################

Getting up and running a |project| instance is straightforward using our docker-compose setup.

=============
Prerequisites
=============
* you have `docker <https://www.docker.com/>`_ and `docker-compose <https://docs.docker.com/compose/>`_ installed
* you have git installed
* you have nodejs, npm and gulp installed

============
Installation
============

1. Checkout the |project| project and install gulp dependencies.

.. code:: bash

    cd ~/projects/
    git clone git@github.com:HelloLily/hellolily.git
    cd hellolily
    npm install
    gulp build

2. Build the docker image. This takes a while the first time. [#f1]_

.. code:: bash

    docker-compose build

.. note:: This command needs to run every time the Dockerfile, requirements or patches are adjusted. Good practice would be to run it every time the git repo is updated. If nothing changed, the command would complete almost instantly.

3. Do a first time migration of the models.

.. code:: bash

    docker-compose run web python manage.py migrate


4. Create a search index for ElasticSearch.

.. code:: bash

    docker-compose run web python manage.py index

5. Populate the database with some testdata.

.. code:: bash

    docker-compose run web python manage.py testdata

6. Run the Django development server along with dependent containers.

.. code:: bash

    docker-compose run --service-ports web


Open http://localhost:8000 in your browser to see the running |project| instance. You can login
using user **superuser1@lily.com** and **admin** as password. Congratulations, you now have |project| running!



.. rubric:: Footnotes

.. [#f1] You might experience connectiviy issues duing build. Checkout `this post <http://serverfault.com/questions/642981/docker-containers-cant-resolve-dns-on-ubuntu-14-04-desktop-host>`_ for more info.
