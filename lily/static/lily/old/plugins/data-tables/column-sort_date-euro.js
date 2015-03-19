$(function($){
    $.fn.dataTableExt.oSort['date-euro-asc'] = function(a, b) {
        a = $($.parseHTML(a)).text();
        a = $.trim(a.replace(/\s{1,}/g, ' '));
        b = $($.parseHTML(b)).text();
        b = $.trim(b.replace(/\s{1,}/g, ' '));

        var x, y = 10000000000000;
        if (a.length !== '') {
            var frDatea = $.trim(a).split(' ');
            var frTimea = frDatea[1].split(':');
            var frDatea2 = frDatea[0].split('/');
            x = (frDatea2[2] + frDatea2[1] + frDatea2[0] + frTimea[0] + frTimea[1] + frTimea[2]) * 1;
        }

        if (b.length !== '') {
            var frDateb = $.trim(b).split(' ');
            var frTimeb = frDateb[1].split(':');
            frDateb = frDateb[0].split('/');
            y = (frDateb[2] + frDateb[1] + frDateb[0] + frTimeb[0] + frTimeb[1] + frTimeb[2]) * 1;
        }

        var z = ((x < y) ? -1 : ((x > y) ? 1 : 0));
        return z;
    };

    $.fn.dataTableExt.oSort['date-euro-desc'] = function(a, b) {
        a = $($.parseHTML(a)).text();
        a = $.trim(a.replace(/\s{1,}/g, ' '));
        b = $($.parseHTML(b)).text();
        b = $.trim(b.replace(/\s{1,}/g, ' '));

        var x, y = 10000000000000;
        if (a.length !== '') {
            var frDatea = $.trim(a).split(' ');
            var frTimea = frDatea[1].split(':');
            var frDatea2 = frDatea[0].split('/');
            x = (frDatea2[2] + frDatea2[1] + frDatea2[0] + frTimea[0] + frTimea[1] + frTimea[2]) * 1;
        }

        if (b.length !== '') {
            var frDateb = $.trim(b).split(' ');
            var frTimeb = frDateb[1].split(':');
            frDateb = frDateb[0].split('/');
            y = (frDateb[2] + frDateb[1] + frDateb[0] + frTimeb[0] + frTimeb[1] + frTimeb[2]) * 1;
        }

        var z = ((x < y) ? 1 : ((x > y) ? -1 : 0));
        return z;
    };
});
