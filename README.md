# HelloLily (Herokuapp/Django project) #

## Prerequisites ##

- python >= 2.5
- pip
- virtualenv/wrapper (optional)
- foreman (gem)
- heroku (gem)

## Installation ##

### Creating the environment ###

Create a virtual python environment for the project.
If you're not using virtualenv or virtualenvwrapper you may skip this step.

#### For virtualenvwrapper ####

```mkvirtualenv --no-site-packages herokuapp-env```

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

### Sync database ###

```foreman run python herokuapp/manage.py syncdb```

## Running ##

```foreman start```

On Windows this won't work however, so use:

```foreman run python manage.py runserver```

Open browser to 127.0.0.1:5000 (:8000 if you're on Windows)
