angular.module('app.directives').directive('resizeIframe', resizeIframe);

function resizeIframe() {
    return {
        restrict: 'A',
        link: function($scope, element, attrs) {
            var maxHeight = $('body').outerHeight();
            element.on('load', function() {
                var ifDoc;
                var ifRef;
                var subtractHeights;
                var height;

                element.removeClass('hidden');

                // Do this after .inbox-view is visible.
                ifDoc = this;
                ifRef = this;

                // set ifDoc to 'document' from frame
                try {
                    ifDoc = ifRef.contentWindow.document.documentElement;
                } catch (e1) {
                    try {
                        ifDoc = ifRef.contentDocument.documentElement;
                    } catch (e2) {
                        throw e2.message;
                    }
                }

                // calculate and set max height for frame
                if (ifDoc) {
                    subtractHeights = [
                        element.offset().top,
                        $('.footer').outerHeight(),
                        $('.inbox-attached').outerHeight(),
                    ];
                    for (height in subtractHeights) {
                        maxHeight = maxHeight - height;
                    }

                    if (ifDoc.scrollHeight > maxHeight) {
                        ifRef.height = maxHeight;
                    } else {
                        ifRef.height = ifDoc.scrollHeight;
                    }
                }
            });
        },
    };
}
