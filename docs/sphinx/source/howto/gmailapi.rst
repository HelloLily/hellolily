###############
Setup GMail API
###############

Hellolily uses Gmail and it's API to process emailaccounts. You need to `register an
account <https://console.developers.google.com>`_ for the Google API and set the following
properties in the *.env* file:

.. code:: bash

    GA_CLIENT_ID=
    GA_CLIENT_SECRET=
    GMAIL_CALLBACK_URL=

*GA_CLIENT_ID* and *GA_CLIENT_SECRET* can be found on the `Google API site <https://console.developers.google.com/>`_.
The *GMAIL_CALLBACK_URL* is http://domain:port/messaging/email/callback/ (e.g. http://127.0.0.1:8000/messaging/email/callback/). 
