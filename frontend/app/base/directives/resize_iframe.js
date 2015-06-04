angular.module('app.directives').directive('resizeIframe', resizeIframe);

function resizeIframe () {
    return {
        restrict: 'A',
        link: function ($scope, element, attrs) {
            var maxHeight = $('body').outerHeight();
            element.on('load', function() {
                element.removeClass('hidden');

                // do this after .inbox-view is visible
                var ifDoc, ifRef = this;

                // set ifDoc to 'document' from frame
                try {
                    ifDoc = ifRef.contentWindow.document.documentElement;
                } catch (e1) {
                    try {
                        ifDoc = ifRef.contentDocument.documentElement;
                    } catch (e2) {
                    }
                }

                // calculate and set max height for frame
                if (ifDoc) {
                    var subtractHeights = [
                        element.offset().top,
                        $('.footer').outerHeight(),
                        $('.inbox-attached').outerHeight()
                    ];
                    for (var height in subtractHeights) {
                        maxHeight = maxHeight - height;
                    }

                    if (ifDoc.scrollHeight > maxHeight) {
                        ifRef.height = maxHeight;
                    } else {
                        ifRef.height = ifDoc.scrollHeight;
                    }
                }
            });
        }
    }
}
