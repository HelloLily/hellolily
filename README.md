# HelloLily #

## Prerequisites ##

- python >= 2.5
- pip
- virtualenv/wrapper (optional)
- foreman (gem)
- heroku (gem)
- gevent (optional, requires stupid compiler on mac, no use on windows 64 bit since gunicorn is paid)

## Installation ##

### Creating the environment ###

Create a virtual python environment for the project.
If you're not using virtualenv or virtualenvwrapper you may skip this step.

#### For virtualenvwrapper ####

```mkvirtualenv --no-site-packages hellolily-env```

```workon hellolily-env```

#### For virtualenv ####

```virtualenv --no-site-packages herokuapp-env```

```cd herokuapp-env```

```source bin/activate```

### Install requirements ###

```cd herokuapp```

```pip install -r requirements.txt```

### Create app at heroku ###

```heroku apps:create -s cedar herokuapp```

Add redis addon to your heroku app

```heroku addons:add redistogo:nano```

### Configure project ###

Edit file ```.env```

### Sync database and create initial data ###

Syncd the database and migrate but do not create an admin via the standard interactive shell of Django, instead we use the createadmin command.

```foreman run 'python herokuapp/manage.py syncdb --all'```

```foreman run 'python herokuapp/manage.py migrate --fake'```

```foreman run python herokuapp/manage.py createadmin```

## Running ##

Gunicorn (and thus gevent) will not run on windows. So you need to adapt a little.

### Windows ###

```foreman run python manage.py runserver```

Open browser to 127.0.0.1:8000

### Mac ###

Edit the procfile to remove the gevent workers from the command if you have not installed this. Then run:

```foreman start```

Open browser to 127.0.0.1:5000
