angular.module('app.services').service('HLDate', HLDate);

function HLDate() {
    this.addBusinessDays = function(date, businessDays) {
        var weeks = Math.floor(businessDays / 5);
        var days = businessDays % 5;
        var day = date.getDay();
        if (day === 6 && days > -1) {
            if (days === 0) {
                days -= 2;
                day += 2;
            }
            days++;
            day -= 6;
        }
        if (day === 0 && days < 1) {
            if (days === 0) {
                days += 2;
                day -= 2;
            }
            days--;
            day += 6;
        }
        if (day + days > 5) days += 2;
        if (day + days < 1) days -= 2;
        date.setDate(date.getDate() + weeks * 7 + days);
        return date;
    };
}
