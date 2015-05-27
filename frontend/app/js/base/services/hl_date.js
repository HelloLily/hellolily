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
}
