.. _intro/install:

############
Installation
############

Getting |project| up and running is straightforward using the included docker-compose setup.


=============
Prerequisites
=============
* you have `docker <https://www.docker.com/>`_ and `docker-compose <https://docs.docker.com/compose/>`_ installed
* you have git installed
* you have nodejs, npm and gulp installed


==================
Docker environment
==================
1. Checkout the |project| project and install gulp dependencies.

.. code:: bash

    cd ~/projects/
    git clone git@github.com:HelloLily/hellolily.git
    cd hellolily
    npm install
    gulp build

2. Build the docker image. This takes a while the first time.

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

Open http://localhost:8080 in your browser to see |project|. You can login using user
**superuser1@lily.com** and **admin** as password. Congratulations, you just completed
the basic |project| installation!


=================
Email integration
=================
Lily uses Google email accounts(Gmail) and it's Gmail API to send email messages
with. Customer emails are stored locally and indexed using ElasticSearch. This allows
Lily users to search and find their customer's data very fast,
using extended search queries.

In order to enable email in Lily, you first need to enable the Gmail API and create
an OAuth 2.0 client ID for a web application. This sounds harder than it is; just proceed as following:

 * Login to the `Google APIs website <https://console.developers.google.com>`_
 * From the *Overview* screen, fill in *Gmail API* in the Search bar and select it from the search results
 * Click on the *Enable* button
 * Now you need to create Credentials. Click on the *Go to Credentials* button
 * Check if the following options are selected in the credentials form:
   * Which API are you using? *Gmail API*
   * Where will you be calling the API from? *Web server*
   * What data will you be accessing? *User data*
 * Click on the *What credentials do i need?* button
 * Give the credentials a name, e.g. *Lily*
 * In *Authorized redirect URIs* fill in your development url, e.g. http://localhost:8080/messaging/email/callback/
 * The restriction options can be kept empty. Just click on the *Create client ID* button
 * You can skip step 3. Just click on the *Done* button at the bottom of the form
 * The current screen should be the Credentials overview; click on *Lily*

The credentials are needed for our Lily GMail setup. Let's add them to the appropriate file.
Open the environment settings file with an editor:

.. code:: bash

    vim /path/to/lily/.env

Add the following settings and fill *Client ID* and *Client secret* as GA_CLIENT_ID and GA_CLIENT_SECRET:

.. code:: bash

    GA_CLIENT_ID=your_client_id
    GA_CLIENT_SECRET=your_client_secret
    GMAIL_CALLBACK_URL=http://localhost:8080/messaging/email/callback/

That's it! Lily is now able to manage Gmail accounts. To test if Gmail integration works, go back
to your running Lily instance and visit http://localhost:8080/#/preferences/emailaccounts

 * Select *add an email account*

You should now be redirected to the Google OAuth login screen. Allow Lily to access your Gmail account.
After that, fill in *From name* and *Label* and press the *Save* button. Your email account will now
get synced to Lily.
