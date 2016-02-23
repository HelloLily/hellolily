# Testing HelloLily

## Prerequisites

- Install [Karma](https://karma-runner.github.io/0.12/intro/installation.html) or use the Karma Docker image (see below).

## Run frontend unit tests in Karma

When Karma is installed, it's as simple as running:

    karma start

Or when using Docker, run
    docker run -it -v $(pwd):/home/docker ferdynice/karmay karma start

Karma will runn all the spec files under:

    frontend/app/**/*Spec.js

Karma will run the tests in PhantomJS. Karma will stay alive and watches for file changes and runs the necessary tests again.

Put all your unit tests in the same folder as where the code lives that you are testing. Give the file the same name and
extend the name with `Spec`.

Example:

    frontend/app/accounts/controllers/list.js
    frontend/app/accounts/controllers/listSpec.js

### How to create a frontend unit test

Copy & paste ;-). For info on unit testing in Angular, see [here](https://docs.angularjs.org/guide/unit-testing).

## Run e2e tests in Protractor

Protractor will be installed within the web docker. There is also a selenium docker to run a selenium server that is
needed to run the tests. There is a basic setup to run the e2e tests from within Django, check
`lily.tests.test_e2e_authorization.AuthorizationTestCase`.

To start the e2e tests:

    docker-compose run --service-ports web python manage.py test

Protractor test can be set in the TestCase. Current `AuthorizationTestCase` will run the spec `tests/authorization-spec.js`.
Any fixtures for the e2e test needs to be loaded in the Django TestCase.

Extend all your filenames with `-spec.js` and put all your e2e tests under:

    tests/e2e/

## Files

There are a couple of files related to testing.

### karma.conf.js

[karma.conf.js](karma.conf.js)
Karma configuration file

### protractor.conf.js

[protractor.conf.js](protractor.conf.js)
Protractor configuration file
