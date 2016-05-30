angular.module('app.directives').directive('editableSelect', editableSelect);

function editableSelect() {
    return {
        restrict: 'E',
        scope: {
            viewModel: '=',
            field: '@',
            type: '@',
            choiceField: '@',
            search: '@?',
            multiple: '@?',
            selectOptions: '=?', // contains any custom settings for the select
        },
        templateUrl: 'base/directives/editable_select.html',
        controller: EditableSelectController,
        controllerAs: 'es',
        transclude: true,
        bindToController: true,
        link: function(scope, element, attr) {
            // Bind click event to the current directive.
            element.on('click', '.editable-click', function() {
                if (scope.es.search) {
                    scope.es[scope.es.formName].$show();

                    scope.$apply();
                }
            });
        },
    };
}

EditableSelectController.$inject = ['$scope', 'HLResource', 'HLSearch', 'HLUtils'];
function EditableSelectController($scope, HLResource, HLSearch, HLUtils) {
    var es = this;

    es.getChoices = getChoices;
    es.refreshChoices = refreshChoices;
    es.updateViewModel = updateViewModel;

    activate();

    // Broadcast function that executes the activate() function when somebody
    // dynamically changes the inline select edit by using the 'assign to me'
    // link, instead of selecting a person with the selectbox.
    $scope.$on('activateEditableSelect', function() {
        activate();
    });

    /////

    function activate() {
        if (!es.selectOptions) {
            // If it's undefined just set it to an empty object.
            // Ensures we don't need extra checks in the code.
            es.selectOptions = {};
        }

        es.object = es.viewModel[es.type.toLowerCase()];

        // Certain values in the given view model are objects,
        // so the default value in the select won't always work.
        // If we're not dealing with an inline editable search select check
        // if it's an object and add .id.
        if (!es.search && typeof es.object[es.field] === 'object') {
            if (es.object[es.field]) {
                es.selectModel = es.object[es.field].id;
            }
        } else {
            es.selectModel = es.object[es.field];
        }

        if (es.selectOptions.hasOwnProperty('display')) {
            es.optionDisplay = es.selectOptions.display;
        } else {
            es.optionDisplay = 'name';
        }

        if (es.search) {
            if (es.selectOptions.hasOwnProperty('placeholder')) {
                es.placeholder = es.selectOptions.placeholder;
            }
        }

        // Setup the form name so we can block the element while saving data.
        es.formName = es.field.replace('_', '') + 'Form';
    }

    function getChoices() {
        var type;
        var field;
        var resourceCall;

        if (es.selectOptions.hasOwnProperty('type')) {
            type = es.selectOptions.type;
        } else {
            type = es.type;
        }

        if (es.selectOptions.hasOwnProperty('field')) {
            field = es.selectOptions.field;
        } else {
            field = es.field;
        }

        resourceCall = HLResource.getChoicesForField(type, field);

        if (!resourceCall.hasOwnProperty('$promise')) {
            es.choices = resourceCall;
        } else {
            // Add a return here so the select gets disabled while
            // loading the options.
            return resourceCall.$promise.then(function(data) {
                if (data.hasOwnProperty('results')) {
                    es.choices = data.results;
                } else {
                    es.choices = data;
                }
            });
        }
    }

    function refreshChoices(query) {
        var type;
        var searchPromise;

        if (es.selectOptions.hasOwnProperty('type')) {
            type = es.selectOptions.type;
        } else {
            type = es.type;
        }

        searchPromise = HLSearch.refreshList(query, type);

        if (searchPromise) {
            searchPromise.$promise.then(function(data) {
                es.choices = data.objects;
            });
        }
    }

    function updateViewModel($data) {
        var selected;
        var i;

        var args = {
            id: es.object.id,
        };

        var form = '[name="es.' + es.formName + '"]';

        if (!es.multiple) {
            // $data only contains the ID, so get the name from the choices in the scope.
            for (i = 0; i < es.choices.length; i++) {
                if (es.choices[i].id === $data) {
                    selected = es.choices[i];
                }
            }
        } else {
            HLUtils.blockUI(form, true);
        }

        if (!es.multiple) {
            if (es.choiceField) {
                es.object[es.field] = $data;
                // Choice fields end with '_display', so set the proper
                // variable so front end changes are reflected properly.
                es.object[es.field + '_display'] = selected.name;
            } else {
                es.object[es.field] = selected;
            }
        }

        if (typeof $data === 'undefined') {
            // We're probably clearing a select field, which produces undefined.
            args[es.field] = null;
        } else {
            args[es.field] = $data;
        }

        return es.viewModel.updateModel(args).then(function() {
            if (es.search) {
                HLUtils.unblockUI(form);
                es[es.formName].$hide();

                if (es.multiple) {
                    es.object[es.field] = $data;
                }

                // Inline editable select2 field doesn't properly update
                // es.selectModel, so update it manually.
                es.selectModel = es.object[es.field];
            }
        });
    }
}
