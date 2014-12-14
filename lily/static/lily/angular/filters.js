/**
 * lilyFilters is a container for all global lily related Angular filters
 */
angular.module('lilyFilters', [])

    /**
     * relativeDate filter is a filter that represents the date in a nice format
     *
     * relativeDate will return a relative date string given the date. If the
     * date is to far in the past, it will fallback to angulars $filter
     *
     * @param: date {date|string} : date object or date string to transform
     * @param: fallbackDateFormat string (optional): fallback $filter argument
     *
     * @returns: string : a relative date string
     *
     * usage:
     *
     * {{ '2014-11-19T12:44:15.795312+00:00' | relativeDate }}
     */
    .filter('relativeDate', ['$filter', function($filter) {
        return function(date, fallbackDateFormat) {


            // Get current date
            var now = new Date(),
                calculateDelta, day, delta, hour, minute, week, month, year;

            // If date is a string, format to date object
            if (!(date instanceof Date)) {
                date = new Date(date);
            }

            delta = null;
            minute = 60;
            hour = minute * 60;
            day = hour * 24;
            week = day * 7;
            month = day * 30;
            year = day * 365;

            // Calculate delta in seconds
            calculateDelta = function() {
                return delta = Math.round((now - date) / 1000);
            };
            calculateDelta();
            if (delta > day && delta < week) {
                date = new Date(date.getFullYear(), date.getMonth(), date.getDate(), 0, 0, 0);
                calculateDelta();
            }

            // Check delta and return result
            switch (false) {
                case !(delta < 30):
                    return 'just now';
                case !(delta < minute):
                    return '' + delta + ' seconds ago';
                case !(delta < 2 * minute):
                    return 'a minute ago';
                case !(delta < hour):
                    return '' + (Math.floor(delta / minute)) + ' minutes ago';
                case Math.floor(delta / hour) !== 1:
                    return 'an hour ago';
                case !(delta < day):
                    return '' + (Math.floor(delta / hour)) + ' hours ago';
                case !(delta < day * 2):
                    return 'yesterday';
                case !(delta < week):
                    return '' + (Math.floor(delta / day)) + ' days ago';
                case Math.floor(delta / week) !== 1:
                    return 'a week ago';

// For now, longer than a week ago is not relevant to show relative
//
//                case !(delta < month):
//                    return '' + (Math.floor(delta / week)) + ' weeks ago';
//                case Math.floor(delta / month) !== 1:
//                    return 'a month ago';
//                case !(delta < year):
//                    return '' + (Math.floor(delta / month)) + ' months ago';
//                case Math.floor(delta / year) !== 1:
//                    return 'a year ago';

                default:
                    // Check fallbackFormat
                    fallbackDateFormat = fallbackDateFormat !== undefined ? fallbackDateFormat : 'longDate';
                    // Use angular $filter
                    return $filter('date')(date, fallbackDateFormat);
            }
        }
    }]);
