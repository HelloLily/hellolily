/**
* Source: https://github.com/ziscloud/angular-slimscroll
*/
angular.module('ui.slimscroll', []).directive('slimscroll', function() {
    'use strict';

    return {
        restrict: 'A',
        link: function($scope, $elem, $attr) {
            var off = [];
            var option = {};

            var refresh = function() {
                if ($attr.slimscroll) {
                    option = $scope.$eval($attr.slimscroll);
                } else if ($attr.slimscrollOption) {
                    option = $scope.$eval($attr.slimscrollOption);
                }

                // This `destroy` causes not being able to use options in the directive.
                // There isn't a proper solution for this slim scroll wrapper yet (as
                // seen on Github, but not using the destroy oesn't seem to evoke any
                // weird behaviour for us at the moment.
                // $($elem).slimScroll({ destroy: true });

                $($elem).slimScroll(option);
            };

            var init = function() {
                refresh();

                if ($attr.slimscroll && !option.noWatch) {
                    off.push($scope.$watchCollection($attr.slimscroll, refresh));
                }

                if ($attr.slimscrollWatch) {
                    off.push($scope.$watchCollection($attr.slimscrollWatch, refresh));
                }

                if ($attr.slimscrolllistento) {
                    off.push($scope.$on($attr.slimscrolllistento, refresh));
                }
            };

            var destructor = function() {
                off.forEach(function(unbind) {
                    unbind();
                });
                off = null;
            };

            off.push($scope.$on('$destroy', destructor));
            init();
        },
    };
});
