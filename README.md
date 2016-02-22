# HelloLily

HelloLily, an open source CRM project built on Django and Elasticsearch.

## Prerequisites

- [Docker](https://www.docker.com/)
- [Docker-Compose](https://docs.docker.com/compose/)

That's it! As long as you are able to run Docker, you can work on HelloLily. Verify that Docker works by running a test image:

    docker run ubuntu:14.04 /bin/echo 'Hello world'

(The first run may take a while as it pulls in Docker images).

## Setup

After checking out the project, build the Docker images.

    docker-compose build

Do a first time migration of the models.

    docker-compose run web python manage.py migrate

Create a search index.

    docker-compose run web python manage.py index

Populate the database with some testdata.

    docker-compose run web python manage.py testdata

Install Node modules.
    # With locally installed npm.
    npm install
    # Or by using a dockerfied npm (for convenience).
    docker run -v $(pwd):/home/docker ferdynice/gulpy npm install

## Running the webserver

Run Gulp (build and watch changes)
    # With locally installed gulp.
    gulp
    # Or by using a dockerfied gulp (for convenience).
    docker run -v $(pwd):/home/docker ferdynice/gulpy gulp

Run the Django development server along with dependent containers.

    docker-compose run --service-ports web

To login, go to http://localhost:8003/ (or `boot2docker ip` in case you're using that). Use credentials that were printed during the `testdata` command.

## Sync mail

To sync mail, set the following properties in your .env file (get the values from the Google Developers Console)
- GA_CLIENT_ID
- GA_CLIENT_SECRET
- GMAIL_CALLBACK_URL

## License

For license details see the LICENSE file.
