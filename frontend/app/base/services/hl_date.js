angular.module('app.services').service('HLDate', HLDate);

function HLDate () {
    /**
     * getSubtractedDate() subtracts x amount of days from the current date
     *
     * @param days (int): amount of days to subtract from the current date
     *
     * @returns (string): returns the subtracted date in a yyyy-mm-dd format
     */
    this.getSubtractedDate = function (days) {
        var date = new Date();
        date.setDate(date.getDate() - days);

        return date.getFullYear() + '-' + (date.getMonth() + 1) + '-' + date.getDate();
    };


    this.addBusinessDays = function (date, businessDays) {
        var weeks = Math.floor(businessDays/5);
        var days = businessDays % 5;
        var day = date.getDay();
        if (day === 6 && days > -1) {
            if (days === 0) {days-=2; day+=2;}
            days++; dy -= 6;}
        if (day === 0 && days < 1) {
            if (days === 0) {days+=2; day-=2;}
            days--; day += 6;}
        if (day + days > 5) days += 2;
        if (day + days < 1) days -= 2;
        date.setDate(date.getDate() + weeks * 7 + days);
        return date;
    }
}
