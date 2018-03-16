[![Build Status](https://travis-ci.org/HelloLily/hellolily.svg?branch=develop)](https://travis-ci.org/HelloLily/hellolily)
[![Code Climate](https://codeclimate.com/github/HelloLily/hellolily/badges/gpa.svg)](https://codeclimate.com/github/HelloLily/hellolily)
[![Test Coverage](https://codeclimate.com/github/HelloLily/hellolily/badges/coverage.svg)](https://codeclimate.com/github/HelloLily/hellolily/coverage)

# Lily

Lily is an open source CRM project built on top of Django, AngularJS and
Elasticsearch.

## Status

Active/Maintained

## Usage

Check out the [Sphinx docs](http://hellolily.readthedocs.org/en/latest/)
for detailed information

### Requirements

* You have git installed
* You have [Docker](https://www.docker.com/) and [docker-compose](https://docs.docker.com/compose/) installed
* You have [NodeJS](https://nodejs.org/en/), npm (included with NodeJS) and [gulp](http://gulpjs.com/) installed

### Installation & running

1. Checkout the Lily project and install gulp dependencies.

```bash
git clone git@github.com:HelloLily/hellolily.git
cd hellolily
npm install
```

2. Build the Docker image.

To retreive images from DockerHub (uploaded by TravisCI) use:

```bash
docker-compose pull
```

To build your own images locally you can use

```bash
DOCKER_USER_ID=1000 docker-compose -f docker-compose.yml -f docker-compose.new-build.yml build
```

> This command needs to run every time the Dockerfile, requirements or patches are adjusted. Good practice would be to run it every time the git repo is updated. If nothing changed, the command will complete almost instantly.

3. Do a first time migration of the models.

```bash
docker-compose run web python manage.py migrate
```

4. Create a search index for ElasticSearch.

```bash
docker-compose run web python manage.py index
```

5. Populate the database with some testdata.

```bash
docker-compose run web python manage.py testdata
```

### Running

Run the Django development server along with dependent containers.

```bash
docker-compose run --service-ports web
```

You can then log in using the credentials creating in step 5 of the installation process.

## Contributing

See the [CONTRIBUTING.md](CONTRIBUTING.md) file on how to contribute to this project.

## Contributors

See the [CONTRIBUTORS.md](CONTRIBUTORS.md) file for a list of contributors to the project.

## Get in touch with a developer

If you want to report an issue see the [CONTRIBUTING.md](CONTRIBUTING.md) file for more info.

We will be happy to answer your other questions at opensource@wearespindle.com.

## License

Lily is made available under the `GNU General Public License v3.0` license. See the [LICENSE](LICENSE) file for more info.
