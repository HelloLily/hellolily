angular.module('app.services').service('HLUtils', HLUtils);

function HLUtils() {
    this.formatPhoneNumber = function(phoneNumber) {
        if (!phoneNumber.raw_input || phoneNumber.raw_input.match(/[a-z]/i)) {
            // If letters are found, skip formatting: it may not be a phone field after all
            return false;
        }

        // Format phone number
        var newNumber = phoneNumber.raw_input
            .replace('(0)', '')
            .replace(/\s|\(|\-|\)|\.|\\|\/|\–|x|:|\*/g, '')
            .replace(/^00/, '+');

        if (newNumber.length === 0) {
            return false;
        }

        // Check if it's a mobile phone number
        if (newNumber.match(/^\+31([\(0\)]+)?6|^06/)) {
            // Set phone number type to mobile
            phoneNumber.type = 'mobile';
        }

        if (!newNumber.startsWith('+')) {
            if (newNumber.startsWith('0')) {
                newNumber = newNumber.substring(1);
            }

            newNumber = '+31' + newNumber;
        }

        if (newNumber.startsWith('+310')) {
            newNumber = '+31' + newNumber.substring(4);
        }

        phoneNumber.raw_input = newNumber;

        return phoneNumber;
    };

    this.getFullName = function(user) {
        // Join strings in array while ignoring empty values.
        return [user.first_name, user.preposition, user.last_name].filter(function(val) { return val; }).join(' ');
    };

    this.getSorting = function(field, descending) {
        var sort = '';
        sort += descending ? '-' : '';
        sort += field;
        return sort;
    };

    this.timeCategorizeObjects = function(data, field) {
        var now = moment();
        var tomorrow = moment().add('1', 'day');

        var items = {
            expired: [],
            today: [],
            tomorrow: [],
            later: [],
        };

        angular.forEach(data, function(item) {
            if (item[field]) {
                var day = moment(item[field]);

                if (day.isBefore(now, 'day')) {
                    items.expired.push(item);
                } else if (day.isSame(now, 'day')) {
                    items.today.push(item);
                } else if (day.isSame(tomorrow, 'day')) {
                    items.tomorrow.push(item);
                } else {
                    items.later.push(item);
                }
            } else {
                items.later.push(item);
            }
        });

        return items;
    };

    this.addBusinessDays = function(daysToAdd, date) {
        var i = 0;
        var newDate;

        if (date) {
            // Given date might not be a moment object, so just convert it.
            newDate = moment(date);
        } else {
            newDate = moment();
        }

        // Add days based on what the priority is. Skip weekends.
        while (i < daysToAdd) {
            newDate = newDate.add(1, 'day');

            if (newDate.day() !== 0 && newDate.day() !== 6) {
                i++;
            }
        }

        return newDate.format();
    };
}
