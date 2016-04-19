========================
Lily Angular style guide
========================

The Angular part of Lily was built with the `John Papa Angular style guide <https://github.com/johnpapa/angular-styleguide>`_ serving as the basis and the `Airbnb JavaScript style guide <https://github.com/airbnb/javascript>`_ for the JavaScript part. This Lily Angular (& JavaScript) style guide will give you an overview of how we use various Angular components and the coding style in Lily. Not all examples might be representative of the actual code and some code might be missing to highlight the important bits. Any improvements are welcome of course.

Note: This isn't meant as a full Angular tutorial/guide, so I assume you have at least know the basics of Angular.

Basics
******
Let's start with the basics. Our coding style. If you're a Spindle employee you can find a complete document of our coding style in the wiki or you can check our ESLint rules in the ``.eslintrc`` file and the scss-lint rules in the ``.sass-lint.yml`` file. Both located in the root of the Lily app. Here's a small excerpt of some general coding style rules.

Naming conventions
==================

Our naming conventions differ slightly from the one used in the John Papa guide.

+-------------+------------------------------+----------------------+
| Element     | Style                        | Example              |
+-------------+------------------------------+----------------------+
| Controllers | Functionality + 'Controller' | ListWidgetController |
+-------------+------------------------------+----------------------+
| Directives  | lowerCamelCase               | listWidget           |
+-------------+------------------------------+----------------------+
| Filters     | lowerCamelCase               | customSanitize       |
+-------------+------------------------------+----------------------+
| Services    | PascalCase                   | HLResource           |
+-------------+------------------------------+----------------------+
| Factories   | PascalCase                   | Account              |
+-------------+------------------------------+----------------------+


Comments
========

Comments start with a capital letter and end with a period. Inline comments (comments on the same line as the code) are written in lowercase and without period.

Directives
**********

Directives are used a lot in Lily. Most things we use more than a few times will get converted to a directives. Even a simple thing like displaying a date is a directive, because we want to be consistent throughout the whole application. Let's take a random directive and break it down.

.. code-block:: javascript

    angular.module('app.directives').directive('editableSelect', editableSelect);

    function editableSelect() {
        return {
            restrict: 'E',
            scope: {
                viewModel: '=',
                field: '@',
                type: '@',
                choiceField: '@',
                selectOptions: '=?', // contains any custom settings for the select
            },
            templateUrl: 'base/directives/editable_select.html',
            controller: EditableSelectController,
            controllerAs: 'es',
            transclude: true,
            bindToController: true,
        };
    }

    EditableSelectController.$inject = ['$scope', '$filter', 'HLResource'];
    function EditableSelectController($scope, $filter, HLResource) {
        var es = this;

        es.getChoices = getChoices;
        es.updateViewModel = updateViewModel;

        activate();

        ...

        <other code>

Let's start at the top.

.. code-block:: javascript

    angular.module('app.directives').directive('editableSelect', editableSelect);

We set up the module and say what name the directive has and what function we call to invoke the directive. The directive can then be used like this (as seen on the ``deals/controllers/detail.html`` page)

.. code-block:: javascript

    <editable-select field="next_step" view-model="vm" type="Deal">
        {{ vm.deal.next_step.name }}
    </editable-select>

Once the directive is called it invokes the ``function editableSelect()``. Let's take the contents of that function and break it down (see comments).

.. code-block:: javascript

    return {
        // This directive can only be used as an HTML element (so by invoking <editable-select></editable-select>).
        restrict: 'E',
        // This directive has an isolated scope and accepts the following parameters:
        scope: {
            // Two way binded param. Changes to this param get reflected in the parent too.
            viewModel: '=',
            // One way binded param, so just pass the value so it can be used in this directive. Changes aren't reflected in the parent.
            field: '@',
            type: '@',
            choiceField: '@',
            // Two way binded optional param.
            selectOptions: '=?',
        },
        templateUrl: 'base/directives/editable_select.html', // The template to be used.
        controller: EditableSelectController, // The controller which contains any logic for this directive.
        controllerAs: 'es', // What variable is used to call the current directive. Is usually 'vm', but sometimes you want a clearer name.
        transclude: true, // Any content put between the directive's HTML tags will be put in the right spot in the template (covered later).
        bindToController: true,
    };

The directive then knows what controller to use and calls that controller (``EditableSelectController`` in this case).

.. code-block:: javascript

    // Inject any dependencies for this controller (such as utility functions).
    EditableSelectController.$inject = ['$scope', '$filter', 'HLResource'];
    function EditableSelectController($scope, $filter, HLResource) {
        // Set the controller's scope to an easier to use variable. Using `this` could given conflicts.
        var es = this;

        // Bind functions to the scope.
        es.getChoices = getChoices;
        es.updateViewModel = updateViewModel;

        // Not required, but used as an 'init' function for the controller.
        activate();

        ...

        <other code>

The rest of this directive's code isn't relevant and won't be covered.

There's one more thing we need, to create a directive: the template. The template for the above controller isn't very complicated and contains everything a normal template contains.

.. code-block:: html

    <span editable-select="es.selectModel" onshow="es.getChoices()" e-ng-options="item.id as item[es.optionDisplay] for item in es.choices"
          onbeforesave="es.updateViewModel($data)" buttons="no">
        <ng-transclude></ng-transclude>
    </span>

This template might be confusing, but you can pretty much ignore all the attributes in the ``span`` tag. They are there to call a third party library (Angular x-editable), but you can see how the controller's variables and function get used to set up the template. The ``ng-transclude`` you see is where I referred to in the intro to this directive. The ``{{ vm.deal.next_step.name }}`` is what will be put in the place of the ``ng-transclude``. This transclusion allows you to have generic templates (like we do with the ``dashboardWidget`` directive).

**Note:** Yes, another ``editableSelect`` directive gets called here, but this is the ``editableSelect`` provided by the Angular x-editable library.

Services
********

We use services to provide generic code to the app. Below is the HLResource service, which provides some useful functions related to resources.

.. code-block:: javascript

    // Make the service available and provide the name of the function which contains the logic.
    angular.module('app.services').service('HLResource', HLResource);

    // Inject any dependencies.
    HLResource.$inject = ['$injector'];
    function HLResource($injector) {
        this.patch = function(model, args) {
            // Function code.
        };

        ...

        <other code>
    }

This function provides a generic way to ``PATCH`` a resource. It also provides generic error and success message once the request is done. An example of it's usage can be found below.

.. code-block:: javascript

    // Inject the HLResource service.
    DealDetailController.$inject = ['Deal', 'HLResource'];
    function DealDetailController(Deal, HLResource) {
        // DealDetailController code.

        function updateModel() {
            // updateModel code.

            return HLResource.patch('Deal', args);
        }
    }

Resources/Factories
*******************

To retrieve data from the backend and to share data across the app we use factories. Below is an excerpt of the Deal factory.

.. code-block:: javascript

    angular.module('app.deals.services').factory('Deal', Deal);

    Deal.$inject = ['$resource', 'HLUtils', 'HLForms', 'User'];
    function Deal($resource, HLUtils, HLForms, User) {
        // 'private' variable to show it's only supposed to be used in this scope.
        // Factory can be used by calling `Deal.<function>`.
        var _deal = $resource(
            '/api/deals/deal/:id/',
            null,
            {
                // Overwrite the built-in patch function Angular provides so we can overwrite the transformRequest
                // and do stuff like cleaning our data.
                patch: {
                    method: 'PATCH',
                    params: {
                        id: '@id',
                    },
                    transformRequest: function () {
                        // transformRequest code.
                    },
                },
                // Allows us to search deals through ElasticSearch.
                query: {
                    url: '/search/search/',
                    method: 'GET',
                    params: {
                        // Set url GET parameters.
                        type: 'deals_deal',
                    },
                },
                // This could be its own resource, but since it's so tightly connected to deals we just
                // provide it in the Deal service.
                getNextSteps: {
                    url: 'api/deals/next-steps/',
                },
            }
        );

        return _deal;

Angular tips & tricks
*********************

This section provides a couple of tips & tricks which can save a lot of Googling and wondering why your code isn't working.

Passing resources to directive
==============================

Make sure you either resolve promises before passing them to a directive or resolve them in the directive's controller. An example of this is the ``listWidget`` directive. Here it's not always sure if we're passing a list or passing a promise. So we do the following check and resolve the promise if needed and then execute our code.

.. code-block:: javascript

    if (vm.collapsableItems) {
        // Certain list widgets have collapsable cells, so set the default state to collapsed.
        if (!vm.list.hasOwnProperty('$promise')) {
            // Array was passed, so just pass the list.
            _setCollapsed(vm.list);
        } else {
            vm.list.$promise.then(function(response) {
                // List hasn't fully loaded, so wait and pass the response.
                _setCollapsed(response);
            });
        }
    }

Building un-minified files
==========================

By default the ``gulp build`` and ``gulp watch`` commands will provide you with minified files. This is nice for production, but when developing it can lead to a lot of frustration because of unclear errors. You can use the following commands to make sure you build un-minified files.

``NODE_ENV=dev gulp build``

``NODE_ENV=dev gulp watch``

Linting
=======

Make sure your editor has ESLint and preferably scss-lint set up so you can instantly see any violations. A pre-commit hook which runs the linters is nice to have as well in case you miss a violation during development.

ng-inspector
============

[ng-inspector](http://ng-inspector.org/): Tired of doing `console.log()` everywhere just to see what you models contain? Use ng-inspector and you get a real-time overview of all variables currently available. If needed you can click one to `console.log()` it.
