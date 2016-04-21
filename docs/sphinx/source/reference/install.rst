.. _howto/install:

###################
Manual installation
###################
:ref:`Installing <intro/install>` |project| with docker is recommended for most installations, but
there may be cases where you find Docker not suitable. This installation describes how to install
|project| without Docker.

=============
Prerequisites
=============
* you have python 2.7 and virtualenv installed
* you have git installed
* you have nodejs, npm and gulp installed
* you have postgresql up and running
* you have elasticsearch up and running
* you have rabbitmq up and running


==================
Django environment
==================
1. Make a virtualenv, checkout the |project| project and install gulp dependencies.

.. code:: bash

    mkdir -p ~/projects/hellolily-env
    cd ~/projects/hellolily-env
    virtualenv2 .
    . ./bin/activate
    git clone git@github.com:HelloLily/hellolily.git
    cd hellolily
    npm install
    gulp build

2. Install all related Python packages.

.. code:: bash

    pip install -r requirements.txt
    pip install -r requirements-dev.txt

3. Setup a postgresql database for |project|.

.. code:: bash

    sudo su postgres
    cd ~
    createdb hellolily
    createuser hellolily -s
    echo "ALTER USER hellolily WITH ENCRYPTED PASSWORD 'c2cg63&(e';" | psql
    echo "create extension unaccent;" | psql
    exit

4. Override settings using your own environment settings.

.. code:: bash

    vim ~/projects/hellolily-env/hellolily/.env

.. code:: bash

    DEBUG=1
    MULTI_TENANT=1

    DEFAULT_FROM_EMAIL=info@mydomain.org
    SERVER_EMAIL=info@mydomain.org
    EMAIL_USE_TLS=1
    EMAIL_HOST=smtp.gmail.com
    EMAIL_HOST_USER=info@mydomain.org
    EMAIL_HOST_PASSWORD=
    EMAIL_PORT=587

    ADMINS=(('Yourname', 'your@email.com'),)

    DATAPROVIDER_API_KEY=
    # Make SECRET_KEY unique for your own site!
    SECRET_KEY=abcdefghijklmnopqrstuvwxyz0123456789abcdefghijklmn

    DATABASE_URL=postgres://hellolily:c2cg63&(e@localhost/hellolily

    AWS_ACCESS_KEY_ID=aws_key
    AWS_SECRET_ACCESS_KEY=aws_secret_access_key
    AWS_STORAGE_BUCKET_NAME=aws_bucket_name

    REDISTOGO_URL=redis://localhost:6379/0
    CELERY_SEND_TASK_ERROR_EMAILS=0


5. Do a first time migration of the models.

.. code:: bash

    ./manage.py migrate

6. Create a search index for ElasticSearch.

.. code:: bash

    ./manage.py index


7. Populate the database with some testdata.

.. code:: bash

    ./manage.py testdata

8. Run the Django development server.

.. code:: bash

    ./manage.py runserver 0:8000

Open http://localhost:8000 in your browser to see |project|. You can login using user
**superuser1@lily.com** and **admin** as password. Congratulations, you just completed
the basic |project| installation!
